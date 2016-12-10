# build svc classifier model

from __future__ import print_function

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from pymongo import MongoClient

from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
import pickle
import os.path
from predictor_utils import *
from helper import *
gnb = GaussianNB()

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__))  , '../data/nb_model.pkl')

def dump():
    # database setting
    # client = MongoClient('localhost', 27017)
    # db = client.local
    db = get_db_client()
    nba_players = db['nba_players']
    compare_data_collection = db["nba_compare_data"]
    data_array = []
    data_class_array = []
    
    for data in compare_data_collection.find({}, {"_id": 0, "player_id_1": 0, "player_id": 0, "player_1_wins": 0}):
        data_array.append(order_compare_data(data)[1])

    for data_class in compare_data_collection.find({}, {"_id": 0, "player_1_wins": 1}):
        data_class_array.append(data_class["player_1_wins"])

    nb = None

    print("Begin dumping...")
    nb = gnb.fit(data_array, data_class_array)

    joblib.dump(nb, file_path)
    return nb

def get_model():
    nb = None
    if os.path.isfile(file_path):
        print("Load model from disk...")
        nb = joblib.load(file_path)
    else:
        nb = dump() 
    #print(svc.score(data_array[10000:16000], data_class_array[10000:16000]))
    return nb

if __name__ == '__main__':
    # database setting
    # client = MongoClient('localhost', 27017)
    # db = client.local
    db = get_db_client()
    nba_players = db['nba_players']
    compare_data_collection = db["nba_compare_data"]
    data_array = []
    data_class_array = []
    
    for data in compare_data_collection.find({}, {"_id": 0, "player_id_1": 0, "player_id": 0, "player_1_wins": 0}):
        data_array.append(order_compare_data(data)[1])

    for data_class in compare_data_collection.find({}, {"_id": 0, "player_1_wins": 1}):
        data_class_array.append(data_class["player_1_wins"])

    nb = None
    if os.path.isfile(file_path):
        nb = get_model()
        print(nb.score(data_array[12000:16000], data_class_array[12000:16000]))
    else:
        nb = dump()
        print(nb.score(data_array[12000:16000], data_class_array[12000:16000]))
    #clf.fit(data_array[:1000], data_class_array[:1000])

