# Use this file to fetch game data into local mongodb
# Currently nba_py is not working with the version 1 api because nba stats moves to version 2
# so I use requests to fetch the data with version 2 api
from __future__ import print_function
from pymongo import MongoClient
from nba_py.game import *
from nba_py.league import *
import requests

if __name__ == '__main__':

    headers = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/45.0.2454.101 Safari/537.36'),
            }

    # get player list
    seasons = ['2015-16']

    base_url = "http://stats.nba.com/stats/boxscoretraditionalv2?GameID={0}&RangeType=0&StartPeriod=0&StartRange=0&EndPeriod=0&EndRange=0"

    print("start fetching game logs...")

    # database setting
    client = MongoClient('localhost', 27017)
    db = client.local
    nba_players = db['nba_players']

    player_count = nba_players.count()
    players = nba_players.find()

    game_logs_collection = db["nba_game_logs"]

    for season in seasons:
        # check if season data has already in database
        if game_logs_collection.find({"season": season}).count() > 0:
            continue

        print("Season " + season + " starts...")
        game_ids = set()
        game_logs = GameLog(season=season, player_or_team=Player_or_Team.Team).overall()
        
        season_games = { "season": season}

        for log in game_logs:
            game_ids.add(log["GAME_ID"])
        
        season_games["ids"] = list(game_ids)
        season_games["boxscores"] = []

        print("There are:" + str(len(game_ids)) + " in this season.")
        count = 0
        for id in game_ids:
            print("{0} / {1} - ".format(count, len(game_ids) ) + "Game: " + id)
            url = base_url.format(id)
            boxscore = requests.get(url, headers=headers)
            season_games["boxscores"].append(boxscore.json())
            count += 1
        #season_games["overall"] = game_logs

        game_logs_collection.insert_one(season_games)

    print("finish fetching game logs")