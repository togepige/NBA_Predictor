from __future__ import print_function, division

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from svm_predict import predict_season_result
import os
import json


root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__))  , '../result/')

threshold_list = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]


def generate_result_file(result, season, time_weight_index, threshold, base_path):
    detail_path = os.path.join(base_path, "svm_detail/")
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


max_accuracy = 0
max_parameter = {}

for item in os.listdir(root_dir):
    summaries = []
    path = os.path.join(root_dir, item)
    if os.path.isdir(path) and item.startswith("testcase_"): # check if it is a testcase folder
        parameters_path = os.path.join(path, "parameters.json")
        with open(parameters_path) as parameters_file:    
            parameters = json.load(parameters_file)
            sample_size = parameters["sample_size"]
            
            # generate results
            for threshold in threshold_list:
                for time_weight_index, time_weight in enumerate(parameters["time_weight"]):
                    accuracy_sum = 0
                    for season in parameters["seasons"]:
                        # get prediction result
                        result = predict_season_result(season, sample_size = sample_size, threshold= threshold, time_weight = time_weight)
                        generate_result_file(result, season, time_weight_index, threshold, path)
                        accuracy_sum += result[0]
                    
                    # compare to the current max accuracy
                    accuracy_average = accuracy_sum / len(parameters["seasons"])
                    summary = {
                            "threshold": threshold,
                            "time_weight": time_weight,
                            "accuracy": accuracy_average
                    }
                    summaries.append(summary)
                        

    summaries.sort(key=lambda x: x["accuracy"], reverse=True)
    summary_file_path = os.path.join(path, "svm_summary.json")
    with open(summary_file_path, "w") as summary_file:
        summary_file.write(json.dumps(summaries, indent=4))