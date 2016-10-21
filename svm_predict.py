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
from player_utils import *
from svm_model import *

# database setting
client = MongoClient('localhost', 27017)
db = client.local
nba_players = db['nba_players']

player_count = nba_players.count()
all_players = nba_players.find()

game_logs_collection = db["nba_game_logs"]


def get_player_pairs(players, teams):
    team_1 = []
    team_2 = []
    pairs = []
    for player in player:
        if player["TEAM_ID"] == tems[0]["TEAM_ID"]:
            team_1.append(player)
        else
            team_2.append(player)

    for player_1 in team_1:
        if not is_key_player(player_1["MIN"])
            continue
        
        player_1_data = nba_players.find({"PERSON_ID": player_1["PLAYER_ID"]} )
        for player_2 in team_2:
            if not is_key_player(player_2["MIN"]):
                continue
            player_2_data = nba_players.find({"PERSON_ID": player_2["PLAYER_ID"]})
            
            if is_pos_match(player_1_data["summary"][0]["POSITION"], player_2_data["summary"][0]["POSITION"]):
                pairs.append( (player_1_data, player_2_data, player_1["MIN"], player_2["MIN"] ) ) # [player1_data, player2_data, total minutes played]

    return pairs 
              
if __name__ == '__main__':
    season = "2015-16"
    game_ids = set()
    season_games = game_logs_collection.find_one({"season": season})
    
    result = []
    total_games = 500
    correct_counts = 0
    for boxscore in season_games["boxscores"][0:total_games]:
        #scorebox = game["boxscore"]
        players = _api_scrape( boxscore, 0 ) 
        teams = _api_scrape( boxscore, 1)
        player_pairs = get_player_pairs(players, teams)
        player_predict_result = []
        total_minutes = 0
        
        team_1_win = teams["PTS"] >= teams["PTS"]

        for pair in player_pairs:
            compare_data = build_base_compare_data(compare_pair[0], compare_pair[1])
            minutes = player_pairs[2] + player_pairs[3]
            total_minutes +=  minutes # sum the minutes and calculate weight later
            svc = get_model()
            predict = svc.predict([compare_data])
            player_predict_result.append((predict, minutes))

        # calculate weight average of predict result
        sum = 0
        for r in player_predict_result:
            sum += r[0] * ( r[1] / total_minutes)
        
        average_predict = sum / len(player_predict_result) >= 0.5
        
        if average_predict == team_1_win:
            correct_counts += 1
        result.append("Game ID: {0}, Real outcome: {1}, Prediction: {2}, Result: {3}".format(
            boxscore["parameters"]["GameID"],
            str(team_1_win),
            str(average_predict),
            str(team_1_win == average_predict)
        ))
        
    print("Accuracy: " + str(correct_counts / total_games))
            
            