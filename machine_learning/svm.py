import os
import sys
import pickle 
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import NuSVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import root_mean_squared_error
from math import sqrt

class SVMModel:
    def __init__(self):
        self.add_project_folder_to_pythonpath()

        self.df_freemod_plays = pd.read_csv(os.path.join("data", "data_processing", "freemod_plays.csv"))
        self.df_freemod_plays.columns = self.df_freemod_plays.columns.str.strip()

        print("Finish initialization.\n")

    
    def add_project_folder_to_pythonpath(self):
        project_path = os.path.abspath("")

        if project_path not in sys.path:
            sys.path.append(project_path)


    def get_input_output(self):
        x = self.df_freemod_plays[["pot", "stage", "hd", "hr"]].values
        y = self.df_freemod_plays["win_probability"].values

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(x, y, test_size=0.2, random_state=67890)

        scaler = StandardScaler().fit(self.X_train)
        self.X_train = scaler.transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)

        print("Finish getting inputs and outputs.\n")

        print(type(self.X_test[0]))


    def train_ml_model(self):
        parameters = {"kernel": ["linear", "rbf", "poly"]}
        self.model = GridSearchCV(NuSVR(), parameters)
        self.model.fit(self.X_train, self.y_train)

        print("Finish training model.\n")


    def evaluate_ml_model(self):
        train_preds = self.model.predict(self.X_test)
        self.rmse = sqrt(root_mean_squared_error(self.y_test, train_preds))

        print(self.model.predict(np.array([np.array([1, 6, 3, 3])])))

        print(f"Root Mean Squared Error: {self.rmse:.5f}")

        matching_positions = ((train_preds > 0.5) & (self.y_test > 0.5)) | ((train_preds < 0.5) & (self.y_test < 0.5))
        percentage = np.sum(matching_positions) / train_preds.size * 100

        print(f"Percentage of Match Outcomes Predicted Correctly: {percentage:.2f}")
    

    def get_rmse(self):
        return self.rmse



if __name__ == "__main__":
    model = SVMModel()
    model.get_input_output()
    model.train_ml_model()
    model.evaluate_ml_model()