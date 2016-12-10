from __future__ import print_function, division

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from predict import *
import os
import json
from helper import *


root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__))  , 'result/')
threshold_list = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]

db = get_db_client()
prediction_result_collection = db['nba_prediction_result']


model = "svm"

def generate_result_file(result, season, time_weight_index, threshold, base_path):
    detail_path = os.path.join(base_path, model + "_detail/")
    if not os.path.exists(detail_path):
        os.mkdir(detail_path)
    
    
    output_file_name = "{0}_{1}_{2}.csv".format(str(season), str(time_weight_index), str(threshold)[2:])
    output_file_path = os.path.join(detail_path, output_file_name)
    with open(output_file_path, "w") as output_file:
        output_file.write("Game ID, Prediction Value, Prediction Result, Real Result, Correct \n")
        
        for game in result[1]:
            output_file.write( "{0}, {1}, {2}, {3}, {4}\n".format(
                game[0],
                str(game[1]),
                str(game[2]),
                str(game[3]),
                str(game[4])
            )
        )

def extract_result(result, season, time_weight, threshold):
    prediction = []

    def extract_player(pred):
        return map(lambda pc: pc[2], pred["player_comparison"])

    for pred in result[1]:
        temp = pred[5]
        temp["player_comparison"] = extract_player(temp)
        prediction.append(temp)
    #print(prediction)
    prediction_result = {
        "model": model,
        "threshold": threshold,
        "season": season,
        "time_weight": str(time_weight),
        "prediction": prediction,
        "accuracy": result[0]
    }

    return prediction_result

max_accuracy = 0
max_parameter = {}


if len(sys.argv) < 2:
    print("Please specify the prediction model")
    sys.exit()

model = sys.argv[1]

for item in os.listdir(root_dir):
    summaries = []
    path = os.path.join(root_dir, item)
    if os.path.isdir(path) and item.startswith("testcase_"): # check if it is a testcase folder
        parameters_path = os.path.join(path, "parameters.json")
        with open(parameters_path) as parameters_file:    
            parameters = json.load(parameters_file)
            parameters["model"] = model
            sample_size = parameters["sample_size"]
            
            db_record = { "parameters": parameters, "testcases": [], "summaries":[]}

            # generate results
            for threshold in threshold_list:
                for time_weight_index, time_weight in enumerate(parameters["time_weight"]):
                    accuracy_sum = 0
                    testcase_result = []
                    for season in parameters["seasons"]:
                        # get prediction result
                        result = predict_season_result(model, season, sample_size = sample_size, threshold= threshold, time_weight = time_weight)
                        generate_result_file(result, season, time_weight_index, threshold, path)
                        #save_to_db(result, season, time_weight, threshold)
                        accuracy_sum += result[0]
                        testcase_result.append(extract_result(result, season, time_weight, threshold))
                    # compare to the current max accuracy
                    accuracy_average = accuracy_sum / len(parameters["seasons"])
                    summary = {
                            "threshold": threshold,
                            "time_weight": time_weight,
                            "accuracy": accuracy_average,
                            "model": model
                    }
                    db_record["summaries"].append({
                        "summary": summary,
                        "testcases": testcase_result 
                    })
                    summaries.append(summary)
            prediction_result_collection.insert_one(db_record)
                
    summaries.sort(key=lambda x: x["accuracy"], reverse=True)
    summary_file_path = os.path.join(path, model + "_summary.json")
    with open(summary_file_path, "w") as summary_file:
        summary_file.write(json.dumps(summaries, indent=4))