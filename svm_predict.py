from __future__ import print_function
from pymongo import MongoClient

from sklearn import svm
from sklearn.model_selection import KFold, cross_val_score
from sklearn.externals import joblib
import pickle
import os.path

from nba_py.game import *
from nba_py.league import *
from nba_py import _api_scrape
from predictor_utils import *
from svm_model import *

# database setting
client = MongoClient('localhost', 27017)
db = client.local
nba_players = db['nba_players']

player_count = nba_players.count()
all_players = nba_players.find()

game_logs_collection = db["nba_game_logs"]

def get_minute(min):
    return int( min.split(":")[0] )

def get_player_pairs(players, teams):
    team_1 = []
    team_2 = []
    pairs = []
    for player in players:
        if player["TEAM_ID"] == teams[0]["TEAM_ID"]:
            team_1.append(player)
        else:
            team_2.append(player)

    for player_1 in team_1:
        if not is_key_player(player_1["MIN"]):
            continue
        
        player_1_data = nba_players.find_one({"PERSON_ID": player_1["PLAYER_ID"]} )
        for player_2 in team_2:
            if not is_key_player(player_2["MIN"]):
                continue
            player_2_data = nba_players.find_one({"PERSON_ID": player_2["PLAYER_ID"]})
            
            if is_pos_match(player_1_data["summary"][0]["POSITION"], player_2_data["summary"][0]["POSITION"]):
                #print(player_1_data["DISPLAY_FIRST_LAST"] + "_" + player_2_data["DISPLAY_FIRST_LAST"])
                pairs.append( (player_1_data, player_2_data, get_minute(player_1["MIN"]), get_minute(player_2["MIN"]) ) ) # [player1_data, player2_data, total minutes played]

    return pairs 
              
if __name__ == '__main__':
    season = "2015-16"
    game_ids = set()
    season_games = game_logs_collection.find_one({"season": season})
    
    result = []
    total_games = 500
    correct_counts = 0
    count = 0
    svc = get_model()
    for boxscore in season_games["boxscores"][0:total_games]:
        #scorebox = game["boxscore"]
        print("Predict {0} / {1} - {2}".format(count + 1, total_games, boxscore["parameters"]["GameID"]))
        
        players = _api_scrape( boxscore, 0 ) 
        teams = _api_scrape( boxscore, 1)
        player_pairs = get_player_pairs(players, teams)
        player_predict_result = []
        total_minutes = 0
        
        team_1_win = teams[0]["PTS"] >= teams[1]["PTS"]

        for pair in player_pairs:
            compare_data = build_base_compare_data(pair[0], pair[1])
            minutes = pair[2] + pair[3]
            total_minutes += minutes # sum the minutes and calculate weight later
            values = order_compare_data(compare_data)[1]
            #print(compare_data)
            #print(values)
            predict = svc.predict([ values ])
            player_predict_result.append((predict[0], minutes))

        # calculate weight average of predict result
        sum = 0.0
        
        #print(player_predict_result)
        result_count = len(player_predict_result)
        for r in player_predict_result:
            weight = float(r[1]) / 116
            if r[1] > 60:
                weight = 1
            elif r[1] > 30:
                weight = 0.75
            else:
                weight = 0.25
            sum += float(r[0]) * weight
        
        
        weight_average = sum / result_count
        average_predict = weight_average >= 0.5
        
        if average_predict == team_1_win:
            correct_counts += 1

        result.append("{5} / {6} - Game ID: {0}, Real outcome: {1}, Prediction: {2}, Weight_Average: {3}, Result: {4}".format(
            boxscore["parameters"]["GameID"],
            str(team_1_win),
            str(average_predict),
            str(weight_average),
            str(team_1_win == average_predict),
            str(count + 1),
            str(total_games)
        ))

        count += 1
    print("\n".join(result))
    print("Accuracy: " + str( float(correct_counts) / float(total_games)) )
            
            