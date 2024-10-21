import pandas as pd
import os
import sys


class DataCleaning:
    def __init__(self):
        self.add_project_folder_to_pythonpath()

        self.raw_dataset = pd.ExcelFile(os.path.join("data", "data_processing", "raw_dataset.xlsx"))
        
        self.df_all_freemod_plays = pd.DataFrame(columns=["red_pot", "red_score", "red_hd", "red_hr",
                                                          "blue_pot", "blue_score", "blue_hd", "blue_hr",
                                                          "red_win_probability"])

    
    def add_project_folder_to_pythonpath(self):
        project_path = os.path.abspath("")

        if project_path not in sys.path:
            sys.path.append(project_path)

    
    def extract_raw_dataset(self):
        self.df_matches = self.raw_dataset.parse(f"matches")
        self.df_seed = self.raw_dataset.parse(f"seed")
        self.df_freemod = self.raw_dataset.parse(f"freemod")

        self.tournament_list = self.df_freemod["tournament"].unique().tolist()
    

    def check_empty_field(self):
        empty_count = self.df_matches.isnull().sum().sum()
        print(f"There are {empty_count} empty values in the match dataset.")
        
        empty_count = self.df_seed.isnull().sum().sum()
        print(f"There are {empty_count} empty values in the seed dataset.")

        empty_count = self.df_freemod.isnull().sum().sum()
        print(f"There are {empty_count} empty values in the freemod dataset.")
    

    def get_unique_types(self, df, df_name):
        print(f"{df_name} dataset:")
        for col in df.columns:
            print(f"Column '{col}':", end = " ")
            unique_types = df[col].apply(type).unique()
            print(unique_types)
        
        print()

    
    def check_type(self):
        self.get_unique_types(self.df_matches, "Matches")
        self.get_unique_types(self.df_seed, "Seed")
        self.get_unique_types(self.df_freemod, "Freemod")
    

    def check_tournament_list(self):
        tournament_list_matches = set(self.df_matches["tournament"])
        tournament_list_seed = set(self.df_seed["tournament"])
        tournament_list_freemod = set(self.df_freemod["tournament"])

        if tournament_list_freemod == tournament_list_seed and tournament_list_freemod == tournament_list_matches:
            print("Tournament list is consistent between sheets.")
            self.tournament_list = tournament_list_matches
        else:
            print("Tournament list is consistent between sheets.")
        
        print()
    

    def check_tournament_stage(self):
        consistent = True
        for tournament in self.tournament_list:
            stage_list_matches = set(self.df_matches[self.df_matches["tournament"] == tournament]["stage"])
            stage_list_freemod = set(self.df_freemod[self.df_freemod["tournament"] == tournament]["stage"])

            if stage_list_matches != stage_list_freemod:
                consistent = False
                print(f"Stages of {tournament} is not consistent.")
        
        if consistent:
            print("Stages of all tournaments are consistent.")
        
        print()
    

    def check_teams_have_seeding(self):
        inconsistent = set()

        for index, row in self.df_matches.iterrows():
            tournament = row["tournament"]
            red_team = row["red_team"]
            blue_team = row["blue_team"]

            row_exists = ((self.df_seed['tournament'] == tournament) & (self.df_seed['team'] == red_team)).any()
            if not row_exists:
                inconsistent.add((tournament, red_team))
            
            row_exists = ((self.df_seed['tournament'] == tournament) & (self.df_seed['team'] == blue_team)).any()
            if not row_exists:
                inconsistent.add((tournament, blue_team))
        
        if len(inconsistent) == 0:
            print("All teams exist in seeding.")
        else:
            for instance in sorted(inconsistent):
                print(f"Team {instance[1]} in {instance[0]} does not exist in seeding.")
        
        print()
    

    def check_teams_play_match(self):
        inconsistent = set()
        for index, row in self.df_seed.iterrows():
            tournament = row["tournament"]
            team = row["team"]

            row_exists = ((self.df_matches['tournament'] == tournament) & ((self.df_matches['red_team'] == team) | (self.df_matches['blue_team'] == team))).any()
            if not row_exists:
                inconsistent.add((tournament, team))
        
        if len(inconsistent) == 0:
            print("All teams play at least 1 match.")
        else:
            for instance in sorted(inconsistent):
                print(f"Team {instance[1]} in {instance[0]} does not play any matches.")
        
        print()

    


if __name__ == "__main__":
    data_cleaning = DataCleaning()
    data_cleaning.extract_raw_dataset()

    data_cleaning.check_empty_field()
    data_cleaning.check_type()
    data_cleaning.check_tournament_list()
    data_cleaning.check_tournament_stage()
    data_cleaning.check_teams_have_seeding()
    data_cleaning.check_teams_play_match()
