from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

#load .env file
load_dotenv()

#disable search engine question when opening chrome 
options = webdriver.ChromeOptions()
options.add_argument("--disable-search-engine-choice-screen");

driver_path = os.getenv("DRIVER_PATH")

driver = webdriver.Chrome(executable_path = driver_path, options=options)
url = 'https://liiga.fi/'
driver.get(url)

# Accepting cookies
try:
    wait = WebDriverWait(driver, 10)
    accept_cookies_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[.//span[text()='HYVÄKSY']]")))
    accept_cookies_button.click()
except (NoSuchElementException, TimeoutException):
    print("Cookies button not found.")

#list will be used to create dataframe
data_list = []

#season needs to be changed manually because of game numbers
season = 2016
save_file_season = season-1

#some seasons the games have absurd game numbers. the games should be from 1 to 450
#this can't be looped, because 2015 for example has games from 7612 to 8061
for game_number in range(7612,8062):
    try:
        url = f'https://liiga.fi/fi/peli/{season}/{game_number}/tilastot'
        driver.get(url)
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    #date
    try:
        date = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID,  'game-details-final-text')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
        
    
    date = date.text
    if "JA" in date:
        date = date.replace("Päättynyt (JA) ", "")
        OT = "True"
    elif "VL" in date:
        date = date.replace("Päättynyt (VL) ", "")
        OT = "True"
    else:
        date = date.replace("Päättynyt ", "")
        OT = "False"
    date = datetime.strptime(date, "%d.%m.%Y")

    #home team
    try:
        home_team_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID,  'game-details-team-name-home')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    home_team_name = home_team_name.text

    #home team goals
    try:
        home_team_goals = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID,  "game-details-team-score-home")))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    home_team_goals = home_team_goals.text

    #visitor team goals
    try:
        away_team_goals = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID,  "game-details-team-score-away")))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    away_team_goals = away_team_goals.text
    
    #visitor team name
    try:
        away_team_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID,  'game-details-team-name-away')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    away_team_name = away_team_name.text
    
    #shots
    try:
        home_team_shots = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-left-1-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    home_team_shots = home_team_shots.text
    home_team_shots_total = home_team_shots.split(' = ')[1]
    
    try:
        away_team_shots = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-right-1-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    away_team_shots = away_team_shots.text
    away_team_shots_total = away_team_shots.split(' = ')[1]
    
    #saves (saves + goals = away sog)
    try:
        home_team_saves = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-left-2-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    home_team_saves = home_team_saves.text
    away_sog = int(home_team_saves.split(' = ')[1]) + int(away_team_goals)
    
    try:
        away_team_saves = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-right-2-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    away_team_saves = away_team_saves.text
    home_sog = int(away_team_saves.split(' = ')[1]) + int(home_team_goals)
    
    #sog%
    home_sog_pct = float(home_sog)/float(home_team_shots_total)
    away_sog_pct = float(away_sog)/float(away_team_shots_total)
    
    
    #Power play tries
    try:
        home_team_pp = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-left-6-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    home_team_pp = home_team_pp.text
    
    try:
        away_team_pp = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-right-6-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    away_team_pp = away_team_pp.text
    
    #Power play goals
    try:
        home_team_ppg = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-left-5-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    home_team_ppg = home_team_ppg.text
           
    try:
        away_team_ppg = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'comparison-value-right-5-team-key-values')))
    except (NoSuchElementException, TimeoutException):
        print(f"Game {game_number} not found.")
        continue
    away_team_ppg = away_team_ppg.text
    
    #pp%
    if int(home_team_pp) != 0:
        home_team_ppp = float(home_team_ppg)/float(home_team_pp)
    
    if int(away_team_pp) != 0:
        away_team_ppp = float(away_team_ppg)/float(away_team_pp)
    
    
    #data to dictionary
    data = {
            "date": date,
            "home_team": home_team_name,
            "home_goals": int(home_team_goals),
            "away_team": away_team_name,
            "away_goals": int(away_team_goals),
            "OT": OT,
            "home_shots": int(home_team_shots_total),
            "away_shots": int(away_team_shots_total),
            "home_sog": home_sog,
            "away_sog": away_sog,
            "home_sog_pct": home_sog_pct,
            "away_sog_pct": away_sog_pct,
            "home_pp": int(home_team_pp),
            "away_pp": int(away_team_pp),
            "home_ppg": int(home_team_ppg),
            "away_ppg": int(away_team_ppg),
            "home_ppp": home_team_ppp,
            "away_ppp": away_team_ppp
        }

    data_list.append(data)


df = pd.DataFrame(data_list)
csv_file_path = os.getenv("CSV_FILE_PATH_MATCHES")
df.to_csv(f'{csv_file_path}/{save_file_season}_{season}_matches.csv', index=False)       
driver.quit()


