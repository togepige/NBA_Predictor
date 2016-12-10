from __future__ import print_function, division

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from pymongo import MongoClient
from helper import *
from nba_py.game import *
from nba_py.league import *
from nba_py import _api_scrape
from numpy.random import *


HEADERS_ORDER = ["MIN", "PTS", "AST", "REB", "STL", "BLK", "TOV", "FT_PCT", "FG_PCT", "FG3_PCT", "FTM"]
CLASS_NAME = "player_1_wins"
default_threshold = 0.5
default_time_weight= [(70, 1), (50, 0.85), (30, 0.5), (0, 0.15)]

db = get_db_client()
nba_players = db['nba_players']
player_count = nba_players.count()
all_players = nba_players.find()
game_logs_collection = db["nba_game_logs"]

def get_player_comparison(teams):
    team_1 = teams[0]
    team_2 = teams[1]
    comparison = []
    
    for player_1 in team_1:
        player_1_id = player_1[0]
        player_1_data = nba_players.find_one({"PERSON_ID": player_1_id }, {"games": 0} )
        if player_1_data is None:
            continue
        
        player_1_min = player_1_data["career"][0]["MIN"]
        # if the play mintues is set by user
        if len(player_1) < 2:
            player_1_min = player_1[1]
        
        if not is_key_player(player_1_min):
            continue

        for player_2 in team_2:
            player_2_id = player_2[0]
            player_2_data = nba_players.find_one({"PERSON_ID": player_2_id }, {"games": 0} )
            if player_2_data is None:
                continue
            player_2_min = player_2_data["career"][0]["MIN"]
            # if the play mintues is set by user
            if len(player_2) < 2:
                player_2_min = player_2[1]
            
            if is_pos_match(player_1_data["summary"][0]["POSITION"], player_2_data["summary"][0]["POSITION"]):
                comparison.append( (player_1_data, player_2_data, player_1_min, player_2_min) ) # [player1_data, player2_data, total minutes played]
            
    return comparison

def get_compare_data_header():
    headers = []
    for key in HEADERS_ORDER:
        headers.append(key + "_1")
        headers.append(key + "_2")
    
    return headers


def is_key_player(min):
    return min > 12

# possible position values:
# Center, Forward-Guard, Forward-Center, Guard, Forward, Guard-Forward, Center-Forward
# Divide them into two groups: Guard and Forward

def is_pos_match(pos1, pos2):
    pos1_real = pos1.split('-')[0]
    pos2_real = pos2.split('-')[0]
    
    if pos1_real == pos2_real:
        return True
    if pos1_real == "Forward" and pos2_real == "Center":
        return True
    if pos1_real == "Center" and pos2_real == "Forward":
        return True
        
    return False

def get_real_pos(pos):
    pos_temp = pos.split('-')[0]
    if pos_temp == "Guard":
        return "Guard"
    elif pos_temp == "Forward" or pos_temp == "Center":
        return "Forward"
    return ""

def build_base_compare_data(p1, p2):
    data_keys = ["MIN", "PTS", "AST", "REB", "STL", "BLK", "TOV", "FT_PCT", "FG_PCT", "FG3_PCT", "FTM"]
    compare_data = {}
    career_1 = p1["career"][0]
    career_2 = p2["career"][0]
    for key in data_keys :
        if (key in career_1) and (key in career_2):
            compare_data[key + "_1"] = career_1[key]
            compare_data[key + "_2"] = career_2[key]

    compare_data["player_id_1"] = p1["PERSON_ID"]
    compare_data["player_id_2"] = p2["PERSON_ID"]
    return compare_data 


def order_compare_data(compare_data):
    new_keys = []
    new_values = []
    for header in HEADERS_ORDER:
        key1 = header + "_1"
        key2 = header + "_2"
        if key1 in compare_data and key2 in compare_data:
            new_keys.append(key1)
            new_keys.append(key2)
            new_values.append(compare_data[key1])
            new_values.append(compare_data[key2])
    
    return (new_keys, new_values)





# predict a game 
# parameters:
#   players: [
#       [(player_id_1, ), (player_id_2, )]
#       [(player_id_3,), (player_id_4, )]
#   ]  
def predict_game(predict_model, teams, threshold=default_threshold, time_weight=default_time_weight):
    # get player career comparison data 

    comparison = get_player_comparison(teams)
    total_minutes = 0
    player_predict_result = []
    
    for pair in comparison:
        # generate comparison data for prediction
        compare_data = build_base_compare_data(pair[0], pair[1])
        minutes = pair[2] + pair[3]
        total_minutes += minutes # sum the minutes and calculate weight later
        values = order_compare_data(compare_data)[1]

        predict = predict_model.predict([ values ])
        player_predict_result.append((predict[0], minutes, {
            "player_1_name": pair[0]["DISPLAY_FIRST_LAST"],
            "player_2_name": pair[1]["DISPLAY_FIRST_LAST"],
            "player_1_win": predict[0],
            "minutes": minutes
        })) # result format: [prediction, total_minutes]
    
    # calculate weight average of predict result
    sum = 0.0
    result_count = len(player_predict_result)
    for r in player_predict_result:
        weight_value = 1
        for weight in time_weight:
            if r[1] >= weight[0]:
                weight_value = weight[1]
                break
        r[2]["weight"] = weight_value
        sum += float(r[0]) * weight_value


    #weight_average = sum / result_count
    weight_average = sum / result_count
    average_predict = weight_average >= threshold
    
    return (weight_average, average_predict, player_predict_result)

    
def predict_season_result(season, sample_size=500, threshold=default_threshold, time_weight=default_time_weight ):
    game_ids = set()
    season_games = game_logs_collection.find_one({"season": season})
    result = []
    sample_indices = choice(len(season_games["boxscores"]), sample_size)
    correct_counts = 0
    count = 0

    prediction_result = []
    for game_index in sample_indices:
        boxscore = season_games["boxscores"][game_index]
        print("Predict {0} / {1} - {2}".format(count + 1, sample_size, boxscore["parameters"]["GameID"]))
        players = _api_scrape( boxscore, 0 )
        teams = _api_scrape( boxscore, 1)
        team_1 = []
        team_2 = []
        
        for player in players:
            if player["TEAM_ID"] == teams[0]["TEAM_ID"]:
                team_1.append((player["PLAYER_ID"], player["MIN"]))
            else:
                team_2.append((player["PLAYER_ID"], player["MIN"]))
        
        prediction = predict_game([team_1, team_2], threshold, time_weight)
        weight_average = prediction[0]
        average_predict = prediction[1]
        team_1_win = teams[0]["PTS"] >= teams[1]["PTS"]

        if average_predict == team_1_win:
            correct_counts += 1
        

        prediction_result.append([boxscore["parameters"]["GameID"], weight_average, average_predict, team_1_win, team_1_win == average_predict,
            {
                "team_1_name": teams[0]["TEAM_NAME"],
                "team_2_name": teams[1]["TEAM_NAME"],
                "weight_average": weight_average,
                "average_prediction": average_predict,
                "result": team_1_win,
                "correctness": team_1_win == average_predict,
                "player_comparison": prediction[2]
            }
        ])
        result.append("{5} / {6} - Game ID: {0}, Real outcome: {1}, Prediction: {2}, Weight_Average: {3}, Result: {4}".format(
            boxscore["parameters"]["GameID"],
            str(team_1_win),
            str(average_predict),
            str(weight_average),
            str(team_1_win == average_predict),
            str(count + 1),
            str(sample_size)
        ))

        count += 1

    accuracy = float(correct_counts) / float(sample_size)
    print("\n".join(result))
    print("Accuracy: " + str(accuracy) )
    return (accuracy, prediction_result)