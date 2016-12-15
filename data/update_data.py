from __future__ import print_function
from pymongo import MongoClient

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from nba_py import constants
from nba_py.player import *
from nba_py.league import *
from nba_py.game import *
from nba_py.team import *

from helper import *
# This module contains all data update functions

# default parameters:
default_seasons = ['2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16', '2016-17']

db = get_db_client() # from helper to import the mongo db client

nba_players = db['players']
nba_games = db["games"]
nba_teams = db["teams"]

"""
Update one player data
"""
def update_one_player(player, seasons):
    player_id = player["PERSON_ID"]
    player_career = PlayerCareer(player_id)
    player_summary = PlayerSummary(player_id)
    player_games = []
    for game_season in seasons: 
        #print(game_season)
        player_games_regular = PlayerGameLogs(player_id, season=game_season, season_type=constants.SeasonType.Regular)
        player_games_playoff = PlayerGameLogs(player_id, season=game_season, season_type=constants.SeasonType.Playoffs)
        #print(player_games_regular)
        player_games.extend(player_games_regular.info())
        player_games.extend(player_games_playoff.info())
    
    player["summary"] = player_summary.info()[0]

    if len(player_career.regular_season_career_totals()):
        player["career_regular"] = player_career.regular_season_career_totals()[0]

    if len(player_career.post_season_career_totals()):
        player["career_regular"] = player_career.post_season_career_totals()[0]

    player["games"] = player_games
    
    nba_players.update_one({"PERSON_ID": player_id}, {"$set": player}, upsert=True)

"""
update player data for sepcified seasons
"""
def update_players(seasons=default_seasons):


    print("Begin updating players data..")
    count = 0

    player_id_set = set()
    all_players_for_season = PlayerList(only_current=0).info() # include retired 

    #players_info = all_players_for_season.info()
    for player in all_players_for_season:
        if player["PERSON_ID"] in player_id_set :
            pass
        else:
            player_id_set.add(player["PERSON_ID"])
            update_one_player(player, seasons)

        count += 1
        print("Finished update player " + str(count) + "/" + str(len(all_players_for_season)))
    
    print("Total players: " + str(count))
"""
update game data for sepcified season
"""
def update_games(seasons=default_seasons):


    print("Begin updating games data..")
    count = 0

    for season in seasons:
        count = 0
        game_logs_regular = GameLog(season=season, player_or_team=constants.Player_or_Team.Team, season_type=constants.SeasonType.Regular).overall()
        game_logs_playoff = GameLog(season=season, player_or_team=constants.Player_or_Team.Team, season_type=constants.SeasonType.Playoffs).overall()
        
        game_ids = set()
        
        for game in game_logs_playoff:
            game_ids.add(game["GAME_ID"])
        
        for game in game_logs_regular:
            game_ids.add(game["GAME_ID"])
        
        for game_id in game_ids:
            # check if the game data has already in database
            if nba_games.find({"GAME_ID": game_id}).count() > 0:
                pass
            else:
                try:
                    boxscore_summary = BoxscoreSummary(game_id)
                    boxscore_detail = Boxscore(game_id)
                
                    game = {}
                    game["GAME_ID"] = game_id
                    game["summary"] = boxscore_summary.game_summary()[0]
                    game["info"] = boxscore_summary.game_info()[0]

                    game["player_stats"] = boxscore_detail.player_stats()
                    game["team_stats"] = boxscore_detail.team_stats()

                    nba_games.insert_one(game)
                except:
                    pass
                

            count += 1
            print("Season: " + season + ". Finished update game " + str(count) + "/" + str(len(game_ids)))
    
    print("Total games: " + str(count))

"""
update team data for specified season
"""
def update_teams(season=default_seasons[:-1]):
    team_list = TeamList().info()
    count = 0
    print("Begin updating team data...")
    for team in team_list:
        team_id = team["TEAM_ID"]
        team_summary = TeamSummary(team_id, season=season).info()[0]
        team["summary"] = team_summary
        nba_teams.update_one({"TEAM_ID": team_id}, {"$set": team}, upsert=True)
        count += 1
        print("Finished team: " + str(count))

if __name__ == '__main__':
    data_type = sys.argv[1]
    if len(sys.argv) >= 3:
        seasons = [ sys.argv[2] ]
    else:
        seasons = default_seasons
    
    if data_type == "player":
        update_players(seasons=seasons)
    elif data_type == "game":
        update_games(seasons=seasons)
    elif data_type == "team":
        update_teams(season=seasons[:-1])