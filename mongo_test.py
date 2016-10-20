from __future__ import print_function
from pymongo import MongoClient


client = MongoClient('localhost', 27017)

db = client.local

nba_players = db['nba_players']

player1 = {
    "test": 45678
}

id = nba_players.insert_one(player1)

print(id)
