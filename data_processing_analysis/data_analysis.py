import pandas as pd
import os
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns


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


    def correlation(self, mod):
        # win_probability[(pot, mod count)] = average win probability
        pot_win_probability = dict()
        pot_frequency = dict()

        for pot in range(1, 8+1):
            for mod_count in range(1, 4+1):
                pot_win_probability[(pot, mod_count)] = 0
                pot_frequency[(pot, mod_count)] = 0

        print(self.df_freemod_plays)

        for index, row in self.df_freemod_plays.iterrows():
            pot = int(row["pot"])
            mod_cnt = int(row[mod])
            win_probability = row["win_probability"]

            pot_win_probability[(pot, mod_cnt)] += win_probability * 100
            pot_frequency[(pot, mod_cnt)] += 1
        
        df_correlation = pd.DataFrame(columns=["pot", "1_mod", "2_mod", "3_mod", "slope"])

        for pot in range(1, 8+1):
            if pot_frequency[(pot, 1)] * pot_frequency[(pot, 2)] * pot_frequency[(pot, 3)] * pot_frequency[(pot, 4)] > 0:
                
                win_prob_1 = pot_win_probability[(pot, 1)] / pot_frequency[(pot, 1)]
                win_prob_2 = pot_win_probability[(pot, 2)] / pot_frequency[(pot, 2)]
                win_prob_3 = pot_win_probability[(pot, 3)] / pot_frequency[(pot, 3)]
                win_prob_4 = pot_win_probability[(pot, 4)] / pot_frequency[(pot, 4)]

                points = [(1, win_prob_1), (2, win_prob_2), (3, win_prob_3), (4, win_prob_4)]
                x_values, y_values = zip(*points)
                slope, intercept = np.polyfit(x_values, y_values, 1)

                new_row = {"pot": pot,
                           "1_mod": win_prob_1, "2_mod": win_prob_2, "3_mod": win_prob_3, "4_mod": win_prob_4,
                           "slope": slope}
                
                df_correlation.loc[len(df_correlation)] = new_row
        
        points = []
        for index, row in df_correlation.iterrows():
            points.append((row["pot"], row["slope"]))
        
        x_values, y_values = zip(*points)
        slope, intercept = np.polyfit(x_values, y_values, 1)

        new_row = {"pot": "overall",
                    "1_mod": "", "2_mod": "", "3_mod": "", "4_mod": "",
                    "slope": slope}
        
        df_correlation.loc[len(df_correlation)] = new_row
        
        df_correlation.to_csv(os.path.join("data", "data_analysis", f"correlation_{mod}.csv"), index=False)




if __name__ == "__main__":
    data_analysis = DataAnalysis()
    data_analysis.correlation("hd")
    data_analysis.correlation("hr")