from __future__ import print_function
from pymongo import MongoClient



# database setting
client = MongoClient('localhost', 27017)
db = client.local
nba_players = db['nba_players']
compare_data_collection = db["nba_compare_data"]

compare_data = compare_data_collection.find({}, {"_id": 0, "player_id_1": 0, "player_id": 0})
file = open("compare_data.csv", "w")

first_data = compare_data[0]
header = ", ".join(first_data.keys())

file.write(header + "\n")

for data in compare_data:
    line = ", ".join(str(x) for x in data.values())
    file.write(line + "\n")

file.close()