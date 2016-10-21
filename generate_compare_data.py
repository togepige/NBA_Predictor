from __future__ import print_function
from pymongo import MongoClient


def build_base_compare_data(p1, p2):
    data_keys = ["MIN", "PTS", "AST", "REB", "STL", "BLK", "TOV", "FT_PCT", "FG_PCT", "FG3_PCT", "FTM"]
    compare_data = {}
    career_1 = p1["career"][0]
    career_2 = p2["career"][0]
    for key in data_keys:
        compare_data[key + "_1"] = career_1[key]
        compare_data[key + "_2"] = career_2[key]

    compare_data["player_id_1"] = p1["PERSON_ID"]
    compare_data["player_id_2"] = p2["PERSON_ID"]
    return compare_data 

def get_game_index_map(player):
    map = {}
    for index, game in enumerate(player["games"]):
        key = game["Game_ID"]
        map[key] = index

    return map 

def get_pos(player):
    return player["summary"][0]["POSITION"]

def is_key_player(player):
    return player["career"][0]["MIN"] > 12

# possible position values:
# Center, Forward-Guard, Forward-Center, Guard, Forward, Guard-Forward, Center-Forward
# Divide them into two groups: Guard and Forward

def is_pos_match(pos1, pos2):
    pos1_real = pos1.split('-')[0]
    pos2_real = pos2.split('-')[0]
    
    if pos1_real == pos2_real:
        return True
    if pos1_real == "Forward" and pos2_real == "Center":
        return True
    if pos1_real == "Center" and pos2_real == "Forward":
        return True
    
    return False

def get_real_pos(pos):
    pos_temp = pos.split('-')[0]
    if pos_temp == "Guard":
        return "Guard"
    elif pos_temp == "Forward" or pos_temp == "Center":
        return "Forward"
    return ""
    

# database setting
client = MongoClient('localhost', 27017)
db = client.local
nba_players = db['nba_players']

player_count = nba_players.count()
players = nba_players.find()

compare_data_collection = db["nba_compare_data"]


print("Generating player compare data...")
for i in range(player_count):
    player_1 = players[i]
    # filter player who plays less than 12 minutes per game
    if not is_key_player(player_1):
        continue

    pos_1 = get_pos(player_1)
    player_games_1_map = get_game_index_map(player_1)
    for j in range(i + 1, player_count):
        player_2 = players[j]
        pos_2 = get_pos(player_2)

        if not is_key_player(player_2):
            continue

        if not is_pos_match(pos_1, pos_2):
            continue
        
        # compare match history and generate compare data
        player_games_2_map = get_game_index_map(player_2)
        compare_data = build_base_compare_data(player_1, player_2)
        # compare_data["wins_1"] = 0
        # compare_data["wins_2"] = 1
        
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
        
        if player_1_wins >= player_2_wins:
            compare_data["player_1_wins"] = 1
        else:
            compare_data["player_1_wins"] = 0

        compare_data_collection.update_one({"player_id_1": compare_data["player_id_1"], "player_id_2": compare_data["player_id_2"]}, {"$set": compare_data}, upsert = True)

print("Data generated...")