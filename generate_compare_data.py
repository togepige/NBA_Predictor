# Use this file to generate player vs player compare data

from __future__ import print_function
from pymongo import MongoClient
from predictor_utils import *
from helper import *

def get_game_index_map(player):
    map = {}
    for index, game in enumerate(player["games"]):
        key = game["Game_ID"]
        map[key] = index

    return map 

def get_pos(player):
    return player["summary"][0]["POSITION"]


if __name__ == '__main__':
    # database setting
    # client = MongoClient('localhost', 27017)
    # db = client.local
    db = get_db_client()
    
    nba_players = db['nba_players']

    player_count = nba_players.count()
    players = nba_players.find()

    compare_data_collection = db["nba_compare_data"]
    count = 0
    print("Generating player compare data...")
    for i in range(player_count):
        player_1 = players[i]
        # filter player who plays less than 12 minutes per game
        if not is_key_player(player_1["career"][0]["MIN"]):
            continue
        
        pos_1 = get_pos(player_1)
        player_games_1_map = get_game_index_map(player_1)
        for j in range(i + 1, player_count):
            player_2 = players[j]
            pos_2 = get_pos(player_2)

            if not is_key_player(player_2["career"][0]["MIN"]):
                continue

            if not is_pos_match(pos_1, pos_2):
                continue
            
            print(str(count) + ": " + player_1["DISPLAY_FIRST_LAST"] + " vs " + player_2["DISPLAY_FIRST_LAST"])

            # compare match history and generate compare data
            player_games_2_map = get_game_index_map(player_2)
            compare_data = build_base_compare_data(player_1, player_2)

            player_1_wins = 0
            player_2_wins = 0
            # add game history to compare_data
            for key in player_games_1_map:
                if key in player_games_2_map:
                    game = player_1["games"][player_games_1_map[key]]
                    if game["WL"] == "W":
                        player_1_wins += 1
                    else:
                        player_2_wins += 1
            
            compare_data["wins_count_1"] = player_1_wins
            compare_data["wins_count_2"] = player_2_wins

            if player_1_wins >= player_2_wins:
                compare_data["player_1_wins"] = 1
            else:
                compare_data["player_1_wins"] = 0

            compare_data_collection.update_one({"player_id_1": compare_data["player_id_1"], "player_id_2": compare_data["player_id_2"]}, {"$set": compare_data}, upsert = True)

            count += 1
    print("Data generated...")