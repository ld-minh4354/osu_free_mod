import pandas as pd
import os
import sys


class DataAnalysis:
    def __init__(self):
        self.add_project_folder_to_pythonpath()

        self.df_freemod_plays = pd.read_csv(os.path.join("data", "data_processing", "freemod_plays.csv"))

        int_columns = self.df_freemod_plays.columns[:-1]
        self.df_freemod_plays[int_columns] = self.df_freemod_plays[int_columns].apply(pd.to_numeric, errors='coerce').astype("Int64")
        self.df_freemod_plays[self.df_freemod_plays.columns[-1]] = pd.to_numeric(self.df_freemod_plays[self.df_freemod_plays.columns[-1]], errors='coerce')

    
    def add_project_folder_to_pythonpath(self):
        project_path = os.path.abspath("")

        if project_path not in sys.path:
            sys.path.append(project_path)

    
    def frequency_between_pots(self):
        df = pd.DataFrame(columns = ["Pot 1", "Pot 2", "Pot 3", "Pot 4"], index = ["Pot 1", "Pot 2", "Pot 3", "Pot 4"])

        for index, row in self.df_freemod_plays.iterrows():
            red_pot = row["red_pot"]
            blue_pot = row["blue_pot"]
            




if __name__ == "__main__":
    data_analysis = DataAnalysis()
    data_analysis.frequency_between_pots()