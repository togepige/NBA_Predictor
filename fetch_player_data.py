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
seasons = ['2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16']

print("Fetching data...")

player_list = PlayerList()
count = 0
for player in player_list.info():
    player_id = player["PERSON_ID"]
    print("Number: " + str(count) + "...")
    player_career = PlayerCareer(player_id)
    player_summary = PlayerSummary(player_id)

    player["summary"] = player_summary.info()
    player["career"] = player_career.regular_season_career_totals()

    player["games"] = []
    for s in seasons:
        player_games = PlayerGameLogs( player_id, season=s )
        player["games"].extend(player_games.info())
        nba_player_games.update_many({"parameters.PlayerID": player_id, "parameters.Season": s }, {"$set": player_games.json}, upsert=True )


    nba_player_careers.update_many({"parameters.PlayerID": player_id}, {"$set": player_career.json}, upsert=True )    
    nba_player_summary.update_many({"parameters.PlayerID": player_id}, {"$set": player_summary.json}, upsert=True )
    
    nba_players.update_many({"PERSON_ID": player_id}, {"$set": player}, upsert=True)

    count += 1

print("finished, fetched " + str(len(player_list.info())) + " players data" )



