import pandas as pd
import os
import sys
import json
import requests
import numpy as np
from scipy.stats import norm

class ExtractFreemodPlays:
    def __init__(self):
        self.add_project_folder_to_pythonpath()

        raw_dataset = pd.ExcelFile(os.path.join("data", "data_processing", "raw_dataset.xlsx"))

        self.df_matches = raw_dataset.parse("matches")
        self.df_seed = raw_dataset.parse("seed")
        self.df_freemod = raw_dataset.parse("freemod")

        self.tournament_list = self.df_freemod["tournament"].unique().tolist()
        
        self.df_all_freemod_plays = pd.DataFrame(columns=["red_pot", "red_score", "red_hd", "red_hr",
                                                          "blue_pot", "blue_score", "blue_hd", "blue_hr",
                                                          "red_win_probability"])

        print("Finish initialization.\n")

    
    def add_project_folder_to_pythonpath(self):
        project_path = os.path.abspath("")

        if project_path not in sys.path:
            sys.path.append(project_path)
        
        print("Finish adding protect folder to PYTHONPATH.\n")

    
    def get_seed_and_freemod(self):
        self.seed = dict()
        self.freemod = dict()

        for tournament in self.tournament_list:
            self.seed[tournament] = dict()
            self.freemod[tournament] = dict()

            stage_list = self.df_freemod[self.df_freemod["tournament"]  == tournament]["stage"].unique().tolist()

            for stage in stage_list:
                self.freemod[tournament][stage] = []


        for index, row in self.df_seed.iterrows():
            self.seed[row["tournament"]][row["team"]] = row["seed"]

        for index, row in self.df_freemod.iterrows():
            self.freemod[row["tournament"]][row["stage"]].append(row["beatmap_id"]) 

        print("Finish getting seed and freemod.\n")   
    

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

        print("Finish getting API token.\n")


    def get_match_json(self, match_id):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }

        json_file = requests.get(f"https://osu.ppy.sh/api/v2/matches/{match_id}", headers=headers)
        match_json = json.loads(json_file.content)

        if not "events" in match_json:
            return None

        while match_json["events"][0]["detail"]["type"] != "match-created":
            event_id = match_json["events"][0]["id"]

            json_file = requests.get(f"https://osu.ppy.sh/api/v2/matches/{match_id}?before={event_id}", headers=headers)
            match_json_add = json.loads(json_file.content)
            
            match_json["events"] = match_json_add["events"] + match_json["events"] 

        return match_json
    

    def get_all_freemod_plays(self):
        for index, row in self.df_matches.iterrows():
            self.get_freemod_play(tournament=row["tournament"], red_team=row["red_team"], blue_team=row["blue_team"], match_id=row["match_id"], stage=row["stage"])

            if (index + 1) % 100 == 0:
                print(f"Finished processing {index + 1} matches")
        
        print("Finish getting all freemod plays.\n")
    

    def get_freemod_play(self, tournament, red_team, blue_team, match_id, stage):
        total_teams = len(self.seed[tournament])
        pot_size = total_teams // 4

        red_pot = (self.seed[tournament][red_team] - 1) // pot_size + 1
        blue_pot = (self.seed[tournament][blue_team] - 1) // pot_size + 1

        match_json = self.get_match_json(match_id=match_id)

        if match_json == None:
            return

        for event in match_json["events"]:
            if "game" in event:
                game = event["game"]
                beatmap_id = int(game["beatmap_id"])

                if beatmap_id in self.freemod[tournament][stage]:
                    red_score = red_hd = red_hr = 0
                    blue_score = blue_hd = blue_hr = 0
                    correct_mod = True

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
                        
                        if not all(element in ["NF", "HD", "HR"] for element in play["mods"]):
                            correct_mod = False
                    
                    #print(play["mods"])
                    #print(red_score, blue_score, red_hr, red_hd, blue_hr, blue_hd, correct_mod)

                    if red_score > 0 and blue_score > 0 and red_hr > 0 and red_hd > 0 and blue_hr > 0 and blue_hd > 0 and correct_mod:
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
        
        print("Finish calculating win probability.\n")


    def save_freemod_plays(self):
        self.df_all_freemod_plays.to_csv(os.path.join("data", "data_processing", "freemod_plays.csv"), index=False)
        print("Freemod plays saved.\n")



if __name__ == "__main__":
    extract_freemod_plays = ExtractFreemodPlays()

    extract_freemod_plays.get_seed_and_freemod()

    client_info_file = open(os.path.join("data", "data_processing", "client_info.txt"), "r")
    client_info = client_info_file.read().split("\n")

    extract_freemod_plays.get_api_token(client_id=client_info[0], client_secret=client_info[1])

    #extract_freemod_plays.get_freemod_match(2019, "Australia", "Finland", 56299664, 1)

    extract_freemod_plays.get_all_freemod_plays()

    extract_freemod_plays.calculate_win_probability()

    extract_freemod_plays.save_freemod_plays()