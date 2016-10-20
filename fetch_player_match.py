from __future__ import print_function
from pymongo import MongoClient
from nba_py.player import *


# database setting
client = MongoClient('localhost', 27017)
db = client.local
nba_players = db['nba_players']

nba_player_careers = db['nba_player_careers']
nba_player_games = db['nba_player_games']

nba_player_careers.delete_many({})
nba_player_games.delete_many({})

seasons = ["2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16"]

print("fetching players' career and games data...")

for player in nba_players.find():
    # player summary:
    player_career = PlayerCareer(player["PERSON_ID"])
    player_games = PlayerGameLogs(player["PERSON_ID"])
    
    player["games"] = player_games.info()
    player["career"] = player_career.regular_season_career_totals()
    
    player.pop("_id")

    nba_players.update_one({"PERSON_ID": player["PERSON_ID"]}, {"$set": player})

    nba_player_careers.insert_one(player_career.json)
    nba_player_games.insert_one(player_games.json)

print("finished, fetched " + " players' career and games data" )

    
