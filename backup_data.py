# back data to 
from __future__ import print_function
from pymongo import MongoClient
import json

# database setting
client = MongoClient('localhost', 27017)
db = client.local

collections = [ "nba_compare_data", "nba_game_logs", "nba_player_careers", "nba_player_games",  "nba_player_summaries", "nba_players"]

for name in collections:
    print("Start exporting " + name + " collection...")
    collection = db[name]
    data = list(collection.find({}, {"_id": 0}))
    f = open("data/" + name + ".json", "w")
    f.write(json.dumps(data))
    f.close()