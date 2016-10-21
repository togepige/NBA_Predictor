# build svc classifier model

from __future__ import print_function
from pymongo import MongoClient

from sklearn import svm
from sklearn.model_selection import KFold, cross_val_score
from sklearn.externals import joblib
import pickle
import os.path
from predictor_utils import *


def train():
    # database setting
    client = MongoClient('localhost', 27017)
    db = client.local
    nba_players = db['nba_players']
    compare_data_collection = db["nba_compare_data"]
    data_array = []
    data_class_array = []
    
    for data in compare_data_collection.find({}, {"_id": 0, "player_id_1": 0, "player_id": 0, "player_1_wins": 0}):
        data_array.append(order_compare_data(data)[1])

    for data_class in compare_data_collection.find({}, {"_id": 0, "player_1_wins": 1}):
        data_class_array.append(data_class["player_1_wins"])

    svc = None

    print("Begin training...")
    svc = svm.SVC( cache_size=1500)
    k_fold = KFold( n_splits = 3 )
    #scores = cross_val_score(svc, data_array[:10000], data_class_array[:10000], cv = k_fold, n_jobs = -1)
    svc.fit(data_array, data_class_array)
    #print(svc.score(data_array[15000:16000], data_class_array[15000:16000]))
    #pickle.dump( svc, open( "svc_model.pkl", "wb" ) )
    joblib.dump(svc, 'data/svc_model.pkl')
    return svc

def get_model():
    svc = None
    if os.path.isfile("data/svc_model.pkl"):
        print("Load model from disk...")
        svc = joblib.load('data/svc_model.pkl')
    else:
        svc = train() 
    #print(svc.score(data_array[10000:16000], data_class_array[10000:16000]))
    return svc

if __name__ == '__main__':
    # database setting
    client = MongoClient('localhost', 27017)
    db = client.local
    nba_players = db['nba_players']
    compare_data_collection = db["nba_compare_data"]
    data_array = []
    data_class_array = []
    
    for data in compare_data_collection.find({}, {"_id": 0, "player_id_1": 0, "player_id": 0, "player_1_wins": 0}):
        data_array.append(order_compare_data(data)[1])

    for data_class in compare_data_collection.find({}, {"_id": 0, "player_1_wins": 1}):
        data_class_array.append(data_class["player_1_wins"])

    svc = None
    if os.path.isfile("data/svc_model.pkl"):
        svc = get_model()
        print(svc.score(data_array[12000:16000], data_class_array[12000:16000]))
    else:
        svc = train()
        print(svc.score(data_array[12000:16000], data_class_array[12000:16000]))
    #clf.fit(data_array[:1000], data_class_array[:1000])

