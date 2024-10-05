import pandas as pd
import os
import sys
import json
import requests
import numpy as np
from scipy.stats import norm

class ExtractFreemodPlays:
    def __init__(self, start_year, end_year):
        self.add_project_folder_to_pythonpath()

        self.raw_dataset = pd.ExcelFile(os.path.join("data", "data_processing", "raw_dataset.xlsx"))

        self.start_year = start_year
        self.end_year = end_year

        
        self.df_all_freemod_plays = pd.DataFrame(columns=["red_pot", "red_score", "red_hd", "red_hr",
                                                          "blue_pot", "blue_score", "blue_hd", "blue_hr",
                                                          "red_win_probability"])

    
    def add_project_folder_to_pythonpath(self):
        project_path = os.path.abspath("")

        if project_path not in sys.path:
            sys.path.append(project_path)

    
    def process_raw_dataset(self):
        self.df_matches = dict()
        self.df_seed = dict()
        self.df_freemod = dict()

        for year in range(self.start_year, self.end_year + 1):
            self.df_matches[year] = self.raw_dataset.parse(f"{year}_matches")
            self.df_seed[year] = self.raw_dataset.parse(f"{year}_seed")
            self.df_freemod[year] = self.raw_dataset.parse(f"{year}_freemod")
        
        self.seed = dict()
        self.freemod = dict()

        for year in range(self.start_year, self.end_year + 1):
            self.get_seed(int(year))
            self.get_freemod(int(year))
        
    
    def get_seed(self, year):
        self.seed[year] = dict()

        for index, row in self.df_seed[year].iterrows():
            self.seed[year][str(row["country"])] = int(row["seed"])


    def get_freemod(self, year):
        self.freemod[year] = dict()

        stage_list = self.df_freemod[year]["stage"].unique().tolist()

        for stage in stage_list:
            self.freemod[year][stage] = []

        for index, row in self.df_freemod[year].iterrows():
            self.freemod[year][int(row["stage"])].append(int(row["beatmap_id"]))
    

    def get_api_token(self, client_id, client_secret):
        url = "https://osu.ppy.sh/oauth/token"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "public"
        }

        json_file = requests.post(url, headers=headers, data=data)
        content = json.loads(json_file.content)
        
        self.api_token = content["access_token"]


    def get_match_json(self, match_id):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }

        json_file = requests.get(f"https://osu.ppy.sh/api/v2/matches/{match_id}", headers=headers)
        match_json = json.loads(json_file.content)

        while match_json["events"][0]["detail"]["type"] != "match-created":
            event_id = match_json["events"][0]["id"]

            json_file = requests.get(f"https://osu.ppy.sh/api/v2/matches/{match_id}?before={event_id}", headers=headers)
            match_json_add = json.loads(json_file.content)\
            
            match_json["events"] = match_json_add["events"] + match_json["events"] 

        return match_json
    

    def get_all_freemod_plays(self):
        for year in range(self.start_year, self.end_year + 1):
            for index, row in self.df_matches[year].iterrows():
                self.get_freemod_play(year=year, red_team=row["red_team"], blue_team=row["blue_team"], match_id=int(row["match_id"]), stage=int(row["stage"]))
    

    def get_freemod_play(self, year, red_team, blue_team, match_id, stage):
        red_pot = (self.seed[year][red_team] - 1) // 8 + 1
        blue_pot = (self.seed[year][blue_team] - 1) // 8 + 1

        match_json = self.get_match_json(match_id=match_id)

        for event in match_json["events"]:
            if "game" in event:
                game = event["game"]
                beatmap_id = int(game["beatmap_id"])

                if beatmap_id in self.freemod[year][stage]:
                    red_score = red_hd = red_hr = 0
                    blue_score = blue_hd = blue_hr = 0

                    for play in game["scores"]:
                        if play["match"]["team"] == "red":
                            red_score += play["score"]
                            if "HD" in play["mods"]:
                                red_hd += 1
                            if "HR" in play["mods"]:
                                red_hr += 1
                        else:
                            blue_score += play["score"]
                            if "HD" in play["mods"]:
                                blue_hd += 1
                            if "HR" in play["mods"]:
                                blue_hr += 1

                    if red_score > 0 and blue_score > 0:
                        new_row = {"red_pot": red_pot, "red_score": red_score,
                                   "red_hd": red_hd, "red_hr": red_hr,
                                   "blue_pot": blue_pot, "blue_score": blue_score,
                                   "blue_hd": blue_hd, "blue_hr": blue_hr,
                                   "red_win_probability": 0.5}
                        
                        self.df_all_freemod_plays.loc[len(self.df_all_freemod_plays)] = new_row


    def calculate_win_probability(self):
        ln_ratio_list = []

        for index, row in self.df_all_freemod_plays.iterrows():
            ln_ratio = np.log(row["red_score"] / row["blue_score"])
            ln_ratio_list.append(ln_ratio)
            ln_ratio_list.append(-ln_ratio)
        
        mu, sigma = norm.fit(ln_ratio_list)

        for index, row in self.df_all_freemod_plays.iterrows():
            ln_ratio = np.log(row["red_score"] / row["blue_score"])
            self.df_all_freemod_plays.loc[index, "red_win_probability"] = 1 - norm.cdf(-ln_ratio, loc=mu, scale=sigma)

    
    def cleaning_data(self):
        self.df_all_freemod_plays = self.df_all_freemod_plays[self.df_all_freemod_plays["blue_hr"] != 0]


    def save_freemod_plays(self):
        self.df_all_freemod_plays.to_csv(os.path.join("data", "data_processing", "freemod_plays.csv"), index=False)



if __name__ == "__main__":
    extract_freemod_plays = ExtractFreemodPlays(2019, 2023)
    extract_freemod_plays.process_raw_dataset()

    client_info_file = open(os.path.join("data", "data_processing", "client_info.txt"), "r")
    client_info = client_info_file.read().split("\n")

    extract_freemod_plays.get_api_token(client_id=client_info[0], client_secret=client_info[1])

    #extract_freemod_plays.get_freemod_match(2019, "Australia", "Finland", 56299664, 1)

    extract_freemod_plays.get_all_freemod_plays()

    extract_freemod_plays.calculate_win_probability()

    extract_freemod_plays.cleaning_data()

    extract_freemod_plays.save_freemod_plays()