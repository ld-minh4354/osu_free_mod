import pandas as pd
import os
import sys


class DataAnalysis:
    def __init__(self):
        self.add_project_folder_to_pythonpath()
        self.df_freemod_plays = pd.read_csv(os.path.join("data", "data_processing", "freemod_plays.csv"))
        self.df_freemod_plays.columns = self.df_freemod_plays.columns.str.strip()

    
    def add_project_folder_to_pythonpath(self):
        project_path = os.path.abspath("")

        if project_path not in sys.path:
            sys.path.append(project_path)
    

    def basic_statistics(self):
        print(self.df_freemod_plays.describe())

    
    def frequency_between_pots(self):
        df = pd.DataFrame(columns = ["Pot 1", "Pot 2", "Pot 3", "Pot 4"], index = ["Pot 1", "Pot 2", "Pot 3", "Pot 4"])
        df.values[:] = 0

        for index, row in self.df_freemod_plays.iterrows():
            red_pot = int(row["red_pot"])
            blue_pot = int(row["blue_pot"])

            if red_pot > blue_pot:
                red_pot, blue_pot = blue_pot, red_pot
            
            df.loc[f"Pot {red_pot}", f"Pot {blue_pot}"] += 1

        df.to_csv(os.path.join("data", "data_analysis", "frequency_between_pots.csv"), index=True)

    
    def frequency_mod_choices(self):
        df = pd.DataFrame(columns = ["1 HD", "2 HD", "3 HD", "4 HD"], index = ["1 HR", "2 HR", "3 HR", "4 HR"])
        df.values[:] = 0

        for index, row in self.df_freemod_plays.iterrows():
            red_hr = int(row["red_hr"])
            red_hd = int(row["red_hd"])
            blue_hr = int(row["blue_hr"])
            blue_hd = int(row["blue_hd"])

            df.loc[f"{red_hr} HR", f"{red_hd} HD"] += 1
            df.loc[f"{blue_hr} HR", f"{blue_hd} HD"] += 1
        
        df.to_csv(os.path.join("data", "data_analysis", "frequency_mod_choices.csv"), index=True)



if __name__ == "__main__":
    data_analysis = DataAnalysis()