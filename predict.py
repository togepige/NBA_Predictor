from __future__ import print_function, division

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from pymongo import MongoClient
from helper import *

from naive_bayes import naive_bayes_model
from svm import svm_model

from numpy.random import *
from nba_py.game import *
from nba_py.league import *
from nba_py import _api_scrape
from predictor_utils import *

db = get_db_client()
nba_players = db['nba_players']
player_count = nba_players.count()
all_players = nba_players.find()
game_logs_collection = db["nba_game_logs"]

default_threshold = 0.5
default_time_weight= [(70, 1), (50, 0.85), (30, 0.5), (0, 0.15)]


model_cache = {
    "svm": svm_model.get_model(),
    "nb": naive_bayes_model.get_model(),
}

# predict a game 
# parameters:
#   players: [
#       [(player_id_1, ), (player_id_2, )]
#       [(player_id_3,), (player_id_4, )]
#   ]  
def predict_game(model, teams, threshold=default_threshold, time_weight=default_time_weight):
    # get player career comparison data 
    predict_model = None
    if model == "svm":
        predict_model = model_cache["svm"]
    elif model == "nb":
        predict_model = model_cache["nb"]

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

    
def predict_season_result(model, season, sample_size=500, threshold=default_threshold, time_weight=default_time_weight ):
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
        
        prediction = predict_game(model, [team_1, team_2], threshold, time_weight)
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

if __name__ == '__main__':
    season = "2015-16"
    model = "SVM"

    if len(sys.argv) >= 4:
        season = sys.argv[1]
        sample_size = int(sys.argv[2])
        model = sys.argv[3]
    else:
        print("Required arguments: season model")
        sys.exit()
    
    result = predict_season_result(model, season, sample_size=sample_size)

    #print(str(result))
