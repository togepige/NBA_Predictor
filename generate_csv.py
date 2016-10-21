# generate compare data csv file for weka

from __future__ import print_function
from pymongo import MongoClient
from predictor_utils import *

if __name__ == '__main__':
    # database setting
    client = MongoClient('localhost', 27017)
    db = client.local
    nba_players = db['nba_players']
    compare_data_collection = db["nba_compare_data"]

    compare_data = compare_data_collection.find({}, {"_id": 0, "player_id_1": 0, "player_id": 0})
    file = open("data/compare_data.csv", "w")

    header = ", ".join(get_compare_data_header()) + ", player_1_wins"

    file.write(header + "\n")

    for data in compare_data:
        order_data = order_compare_data(data)
        line = ", ".join(str(x) for x in order_data[1]) + ", " + str(data["player_1_wins"])
        file.write(line + "\n")

    file.close()