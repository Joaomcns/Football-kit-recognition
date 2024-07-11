from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
from tqdm import tqdm

with open('prem_teams.json') as file:
    teams_dict = json.load(file)
    
def format_url(season: str, team: str) -> str:
    base_url = 'https://www.footballkitarchive.com/'
    fc_teams = ['Arsenal','Liverpool','Chelsea']
    
    if team in fc_teams:
        return base_url + team.replace(' ','-').lower() + '-fc-' + season[:5] + season[7:] + '-kits/'
    
    return base_url + team.replace(' ','-').lower() + '-' + season[:5] + season[7:] + '-kits/'


def get_details(details: str) -> tuple:
    detail_list= []
 
    for detail in details: 
        if detail != '\n':
            detail_list.append(detail.text)

    
    return detail_list[0], detail_list[1]


def get_kits(url: str) -> pd.DataFrame:
    page = requests.get(url)      
    soup = BeautifulSoup(page.text, "html.parser")

    if soup.title.text == "404 Not Found":
        print(url)
        print("Something is wrong in the url PLEASE CHECK") 
    
    team_kits = soup.findAll("div", {"class":"kit"})

    brand, league = get_details(soup.find("ul", {"class":"section-details"}))

    rows = []
    for kit in team_kits:
        new_row = {
            "Team":kit.find("div", class_="kit-teamname").text,
            "Season-Kit":kit.find("div", class_="kit-season").text,
            "League":league,
            "Brand":brand,
            "Image":kit.img['src'] 
        }
        rows.append(new_row)
    return pd.DataFrame.from_dict(rows, orient='columns')


def write_to_csv(t_dict: dict) -> pd.DataFrame:
    empty_df = pd.DataFrame(columns=["Team", "Season-Kit", "League",  "Brand", "Image"])
    for season, teams in tqdm(t_dict.items()): 
        for team in teams:   
            url = format_url(season, team)
            empty_df = pd.concat([empty_df, get_kits(url)], ignore_index=True, axis=0)
    
    empty_df[['Season', 'Kit']] = empty_df['Season-Kit'].str.split(' ', n=1, expand=True)

    empty_df.drop('Season-Kit', axis=1, inplace=True)    
    return empty_df
    

write_to_csv(teams_dict).to_excel("Prem-Kits.xlsx", index=False)


