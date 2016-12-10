# NBA_Predictor
This project is for my Data Mining course term project. In this project, I perform prediction based on player performance instead of team match history. This method has some benefits:
1. Assign more weight to key player by compare their average minutes played.
2. Compare each pair of players instead just compare the team match history.
3. Can be easily to special cases for example injuries, trades or DNP


# Some results
1. The SVM prediction now can get about 65% accuracy and Naive Bayes can only get about 55%.
2. The time weight and threshold in my experiment for SVM is `[(70, 1), (50, 0.85), (30, 0.5), (0, 0.15)]` and `0.5`

# Data Initialization
1. Modify the `dbconfig.json` file to configure the database setting (If you are using local mongodb without authentication, keep the username and password setting but set the value to empty string)

2. Execute `python fetch_player_data.py` to fetch all player data

3. Execute `python fetch_game_logs.py` to fetch the game logs (It will fetch all regular games from 2011~2016)

4. Execute `python generate_compare_data.py` to generate player vs player comparison data

# Usage
There are two types of classifier: SVM and Naive Bayes. Choose the one you want and execute the predict script to get the prediction result.

You can run the prediction by creating a testcase folder, passing parameters through command arguments or importing the prediction function:

## 1. Use testcase folder
1. Create a folder with `testcase_1` under folder `result`
2. Create a `parameters.json` to specify the testcase     
3. Run `python .\svm\svm_predict_helper.py`
4. You can see the summary in `summary.json` file and detail prediction result in `svm_detail` folder

  
## 2. Run with command line season and sampling size parameter
1. Run `python .\svm\svm_predict.py 2015-16 200`
2. The first parameter is the season 
3. The second parameter is the sampling size 


## 3. Import the predict function
1. Include `from svm_predict import predict_game` in your python file
2. Call `predict_game(teams, threshold, time_weight)` function
3. The first parameter is an array with two elements. Element should be in an array of tuple `[(player_id, min), (player_id, )]`. The first element is the player id and the second element is optional and is the minutes the player plays in this game
4. The second parameter is prediction threshold. It means only the prediction result(float) which is bigger that the threshold will be considered as winning
5. The third parameter is time weight. The format is `[(70, 1), (50, 0.85), (30, 0.5), (0, 0.15)]`. It means two players play more than 70 minutes will be assigned weight 1 and two players play more than 50 minutes will be assigned 0.85 weight.

## Note
1. You can use Naive Bayes classifier in the same way
2. You can have multiple testcases folder
3. You can find an example testcase under in `result` folder
