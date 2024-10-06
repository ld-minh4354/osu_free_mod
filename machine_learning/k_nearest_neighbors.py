import os
import sys
import pickle 
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error
from math import sqrt

class MachineLearning:
    def __init__(self):
        self.add_project_folder_to_pythonpath()

        self.df_freemod_plays = pd.read_csv(os.path.join("data", "data_processing", "freemod_plays.csv"))
        self.df_freemod_plays.columns = self.df_freemod_plays.columns.str.strip()

    
    def add_project_folder_to_pythonpath(self):
        project_path = os.path.abspath("")

        if project_path not in sys.path:
            sys.path.append(project_path)


    def get_input_output(self):
        x = self.df_freemod_plays[["red_pot", "red_hd", "red_hr", "blue_pot", "blue_hd", "blue_hr"]].values
        y = self.df_freemod_plays["red_win_probability"].values

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(x, y, test_size=0.1, random_state=67890)


    def save_ml_model(self):
        knnPickle = open(os.path.join("data", "machine_learning", "knn_model"), "wb") 
        pickle.dump(self.knn_model, knnPickle)  
        knnPickle.close()

    
    def load_ml_model(self):
        return pickle.load(open(os.path.join("data", "machine_learning", "knn_model"), "rb"))
    

    def train_ml_model(self):
        parameters = {"n_neighbors": range(1, 50), "weights": ["uniform", "distance"]}
        self.knn_model = GridSearchCV(KNeighborsRegressor(), parameters)
        self.knn_model.fit(self.X_train, self.y_train)


    def evaluate_ml_model(self):
        train_preds = self.knn_model.predict(self.X_test)
        self.rmse = sqrt(mean_squared_error(self.y_test, train_preds))

        print(f"Root Mean Squared Error: {self.rmse}")
    

    def get_rmse(self):
        return self.rmse



if __name__ == "__main__":
    machine_learnng = MachineLearning()
    machine_learnng.get_input_output()
    machine_learnng.train_ml_model()
    machine_learnng.evaluate_ml_model()