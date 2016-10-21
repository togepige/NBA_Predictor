HEADERS_ORDER = ["MIN", "PTS", "AST", "REB", "STL", "BLK", "TOV", "FT_PCT", "FG_PCT", "FG3_PCT", "FTM"]
CLASS_NAME = "player_1_wins"

def get_compare_data_header():
    headers = []
    for key in HEADERS_ORDER:
        headers.append(key + "_1")
        headers.append(key + "_2")
    
    return headers


def is_key_player(min):
    return min > 12

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

def build_base_compare_data(p1, p2):
    data_keys = ["MIN", "PTS", "AST", "REB", "STL", "BLK", "TOV", "FT_PCT", "FG_PCT", "FG3_PCT", "FTM"]
    compare_data = {}
    career_1 = p1["career"][0]
    career_2 = p2["career"][0]
    for key in data_keys :
        if (key in career_1) and (key in career_2):
            compare_data[key + "_1"] = career_1[key]
            compare_data[key + "_2"] = career_2[key]

    compare_data["player_id_1"] = p1["PERSON_ID"]
    compare_data["player_id_2"] = p2["PERSON_ID"]
    return compare_data 


def order_compare_data(compare_data):
    new_keys = []
    new_values = []
    for header in HEADERS_ORDER:
        key1 = header + "_1"
        key2 = header + "_2"
        if key1 in compare_data and key2 in compare_data:
            new_keys.append(key1)
            new_keys.append(key2)
            new_values.append(compare_data[key1])
            new_values.append(compare_data[key2])
    
    return (new_keys, new_values)