from __future__ import print_function
from pymongo import MongoClient
from nba_py.player import *

# database setting
client = MongoClient('localhost', 27017)
db = client.local


nba_players = db['nba_players']
nba_player_careers = db['nba_player_careers']
nba_player_games = db['nba_player_games']
nba_player_summary = db['nba_player_summaries']

# nba_players.delete_many({})
# nba_player_careers.delete_many({})
# nba_player_games.delete_many({})
# nba_player_summary

# get player list

print("Fetching data...")

player_list = PlayerList()
for player in player_list.info():
    player_id = player["PERSON_ID"]
    player_career = PlayerCareer(player_id)
    player_games = PlayerGameLogs(player_id)
    player_summary = PlayerSummary(player_id)

    player["games"] = player_games.info()
    player["summary"] = player_summary.info()
    player["career"] = player_career.regular_season_career_totals()

    nba_players.update_one({"PERSON_ID": player_id}, {"$set": player}, upsert=True)
    nba_player_careers.update_one({"parameters.PlayerID": player_id}, {"$set": player_career.json}, upsert=True )
    nba_player_games.update_one({"parameters.PlayerID": player_id}, {"$set": player_games.json}, upsert=True )
    nba_player_summary.update_one({"parameters.PlayerID": player_id}, {"$set": player_summary.json}, upsert=True )


print("finished, fetched " + str(len(player_list.info())) + " players data" )



