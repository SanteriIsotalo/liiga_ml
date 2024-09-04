from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import pandas as pd
import time

#load .env file
load_dotenv()

#disable search engine question when opening chrome 
options = webdriver.ChromeOptions()
options.add_argument("--disable-search-engine-choice-screen")
options.add_argument("--start-maximized")

driver_path = os.getenv("DRIVER_PATH")

driver = webdriver.Chrome(executable_path = driver_path, options=options)
url = 'https://liiga.fi/'
driver.get(url)

#Accepting cookies
try:
    wait = WebDriverWait(driver, 10)
    accept_cookies_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[.//span[text()='HYVÄKSY']]")))
    accept_cookies_button.click()
except (NoSuchElementException, TimeoutException):
    print("Cookies button not found.")

seasons = [2016,2017,2018,2019,2020,2021,2022,2023,2024]
max_fails = 10
current_season_index = 0
#sometimes the web page doesn't load, so we want to try again instead of skipping
while current_season_index < len(seasons):
    season = seasons[current_season_index]
    retries = 0
    failure = False
    
    if retries < max_fails:
        # list will be used to create dataframe later
        season_data = []
        save_file_season = season - 1
        for i in range(0, 15):
        #season overall
            try:
                url = f'https://liiga.fi/fi/tilastot/joukkuetilastot/kausi?tilasto=sarjataulukko&kaudesta={season}&kauteen={season}&sarja=runkosarja&sarake=Joukkue'
                driver.get(url)
                wait = WebDriverWait(driver, 15)
                time.sleep(3)      
                team_name = driver.find_element(By.ID, f"team-statistics-stat-name-{i}").text.replace("\n", "").split(".")[1].strip()
                games_played = driver.find_element(By.ID, f'team-statistics-stat-games-{i}').text.replace(" ", "")
                wins = driver.find_element(By.ID, f'team-statistics-stat-wins-{i}').text.replace(" ", "")
                ties = driver.find_element(By.ID, f'team-statistics-stat-ties-{i}').text.replace(" ", "")
                losses = driver.find_element(By.ID, f'team-statistics-stat-losses-{i}').text.replace(" ", "")
                wins_OT = driver.find_element(By.ID, f'team-statistics-stat-extraPoints-{i}').text.replace(" ", "")
                points = driver.find_element(By.ID, f'team-statistics-stat-points-{i}').text.replace(" ", "")
                points_per_game = str(round(float(points)/float(games_played),2))
                win_pct = str(round(float(wins)/float(games_played),2))
                wins_overall = float(wins) + float(wins_OT)
                win_pct_OT = str(round((wins_overall)/float(games_played),2))
                           
            except NoSuchElementException:
                print("No such element.")
                failure = True
                continue
        #5v5 
            try:
                url = f'https://liiga.fi/fi/tilastot/joukkuetilastot/kausi?tilasto=tasalukuisena&kaudesta={season}&kauteen={season}&sarja=runkosarja&sarake=Joukkue'
                driver.get(url)
                wait = WebDriverWait(driver, 15)           
                time.sleep(3)
                time_5v5 = driver.find_element(By.ID, f'team-statistics-stat-evenStrengthTime-{i}').text.replace(" ", "")
                time_pgs_5v5 = driver.find_element(By.ID, f'team-statistics-stat-timeForGoal-{i}').text.replace(" ", "")
                time_pga_5v5 = driver.find_element(By.ID, f'team-statistics-stat-timeForGoalAgainst-{i}').text.replace(" ", "")
                gs_5v5 = driver.find_element(By.ID, f'team-statistics-stat-evenStrengthGoalsFor-{i}').text.replace(" ", "")
                ga_5v5 = driver.find_element(By.ID, f'team-statistics-stat-evenStrengthGoalsAgainst-{i}').text.replace(" ", "")                          
            except NoSuchElementException:
                print("No such element.")
                failure = True
                continue        
        #power play
            try:
                url = f'https://liiga.fi/fi/tilastot/joukkuetilastot/kausi?tilasto=ylivoima&kaudesta={season}&kauteen={season}&sarja=runkosarja&sarake=Joukkue'
                driver.get(url)
                wait = WebDriverWait(driver, 15)
                time.sleep(3)
                pp_count = driver.find_element(By.ID, f'team-statistics-stat-powerplay-{i}').text.replace(" ", "")
                pp_time = driver.find_element(By.ID, f'team-statistics-stat-powerplayTime-{i}').text.replace(" ", "")
                pp_pct = driver.find_element(By.ID, f'team-statistics-stat-powerplayPercentage-{i}').text.replace(" ", "").replace('"', "").replace(",",".")
                pp_goals = driver.find_element(By.ID, f'team-statistics-stat-powerplayGoals-{i}').text.replace(" ", "")
                time_pgs = driver.find_element(By.ID, f'team-statistics-stat-timeForGoalPowerplay-{i}').text.replace(" ", "")
                                
            except NoSuchElementException:
                print("No such element.")
                failure = True
                continue        
        #penalty kill
            try:
                url = f'https://liiga.fi/fi/tilastot/joukkuetilastot/kausi?tilasto=alivoima&kaudesta={season}&kauteen={season}&sarja=runkosarja&sarake=Joukkue'
                driver.get(url)
                wait = WebDriverWait(driver, 15)
                time.sleep(3)
                pk_count = driver.find_element(By.ID, f'team-statistics-stat-penaltyKill-{i}').text.replace(" ", "")
                pk_time = driver.find_element(By.ID, f'team-statistics-stat-penaltyKillTime-{i}').text.replace(" ", "")
                pk_pct = driver.find_element(By.ID, f'team-statistics-stat-penaltyKillPercentage-{i}').text.replace(" ", "").replace('"', "").replace(",",".")
                pk_ga = driver.find_element(By.ID, f'team-statistics-stat-penaltyKillGoalsAgainst-{i}').text.replace(" ", "")
                time_pga = driver.find_element(By.ID, f'team-statistics-stat-timeForGoalAgainstPK-{i}').text.replace(" ", "")
                
            except NoSuchElementException:
                print("No such element.")
                failure = True
                continue        
        #shots
            try:
                url = f'https://liiga.fi/fi/tilastot/joukkuetilastot/kausi?tilasto=laukaukset&kaudesta={season}&kauteen={season}&sarja=runkosarja&sarake=Joukkue'
                driver.get(url)
                wait = WebDriverWait(driver, 15)
                time.sleep(3)
                shots_scored_pct = driver.find_element(By.ID, f'team-statistics-stat-shotsPercentage-{i}').text.replace(" ", "").replace(",", ".")
                shots_total = driver.find_element(By.ID, f'team-statistics-stat-shots-{i}').text.replace(" ", "")
                shots_against_total = driver.find_element(By.ID, f'team-statistics-stat-shotsAgainst-{i}').text.replace(" ", "").replace('"', "")
                shot_diff = driver.find_element(By.ID, f'team-statistics-stat-shotsDifference-{i}').text.replace(" ", "")
                shot_pct_total = driver.find_element(By.ID, f'team-statistics-stat-shotsForShotsAgainstPercentage-{i}').text.replace(" ", "").replace(",",".")
                sog_total = driver.find_element(By.ID, f'team-statistics-stat-nonBlockedShots-{i}').text.replace(" ", "")
                sog_against_total = driver.find_element(By.ID, f'team-statistics-stat-nonBlockedShotsAgainst-{i}').text.replace(" ", "")
                sog_diff = driver.find_element(By.ID, f'team-statistics-stat-nonBlockedShotsDifference-{i}').text.replace(" ", "").replace(",",".")
                sog_pct_total = driver.find_element(By.ID, f'team-statistics-stat-nonBlockedShotsForShotsAgainstPercentage-{i}').text.replace(" ", "").replace(",",".")
                save_pct = driver.find_element(By.ID, f'team-statistics-stat-savePercentage-{i}').text.replace(" ", "").replace(",",".")
                sum_shots_scored_pct_saves = str(round(float(shots_scored_pct) + float(save_pct),2))
                
            except NoSuchElementException:
                print("No such element.")
                failure = True
                continue

        #home_games
            try:
                url = f'https://liiga.fi/fi/tilastot/joukkuetilastot/kausi?tilasto=sarjataulukko&kaudesta={season}&kauteen={season}&sarja=runkosarja&ottelut=koti&sarake=Joukkue'
                driver.get(url)
                wait = WebDriverWait(driver, 15)
                time.sleep(3)
                home_wins = driver.find_element(By.ID, f"team-statistics-stat-wins-{i}").text
                home_ties = driver.find_element(By.ID, f"team-statistics-stat-ties-{i}").text
                home_losses = driver.find_element(By.ID, f"team-statistics-stat-losses-{i}").text
                home_points = driver.find_element(By.ID, f"team-statistics-stat-points-{i}").text
                
            except NoSuchElementException:
                print("No such element.")
                failure = True
                continue
        #away_games
            try:
                url = f'https://liiga.fi/fi/tilastot/joukkuetilastot/kausi?tilasto=sarjataulukko&kaudesta={season}&kauteen={season}&sarja=runkosarja&ottelut=vieras&sarake=Joukkue'
                driver.get(url)
                wait = WebDriverWait(driver, 15)
                time.sleep(3)
                away_wins = driver.find_element(By.ID, f"team-statistics-stat-wins-{i}").text
                away_ties = driver.find_element(By.ID, f"team-statistics-stat-ties-{i}").text
                away_losses = driver.find_element(By.ID, f"team-statistics-stat-losses-{i}").text
                away_points = driver.find_element(By.ID, f"team-statistics-stat-points-{i}").text
                #shows progress
                current_team = i + 1
                print(f"Team number {current_team}, {season}.")
                
            except NoSuchElementException:
                print("No such element.")
                failure = True
                continue
            #making sure all are correct type
            season_data.append([
            team_name, int(games_played), int(wins), int(ties), int(losses), int(wins_OT), int(points), float(points_per_game),
            float(win_pct), float(win_pct_OT), float(time_5v5),
            float(time_pgs_5v5), float(time_pga_5v5), int(gs_5v5), int(ga_5v5), int(pp_count), float(pp_time), float(pp_pct),
            int(pp_goals), float(time_pgs), int(pk_count), float(pk_time),
            float(pk_pct), int(pk_ga), float(time_pga), float(shots_scored_pct), int(shots_total), int(shots_against_total),
            int(shot_diff), float(shot_pct_total), int(sog_total),
            int(sog_against_total), int(sog_diff), float(sog_pct_total), float(save_pct), float(sum_shots_scored_pct_saves), int(home_wins),
            int(home_ties), int(home_losses), int(home_points),
            int(away_wins), int(away_ties), int(away_losses), int(away_points)
        ])
            
            columns = [
            'team_name', 'games_played', 'wins', 'ties', 'losses', 'wins_OT', 'points', 'points_per_game',
            'win_pct', 'win_pct_OT', 'time_5v5',
            'time_pgs_5v5', 'time_pga_5v5', 'gs_5v5', 'ga_5v5', 'pp_count', 'pp_time', 'pp_pct',
            'pp_goals', 'time_pgs', 'pk_count', 'pk_time',
            'pk_pct', 'pk_ga', 'time_pga', 'shots_scored_pct', 'shots_total', 'shots_against_total',
            'shot_diff', 'shot_pct_total', 'sog_total',
            'sog_against_total', 'sog_diff', 'sog_pct_total', 'save_pct', 'sum_shots_scored_pct_saves', 'home_wins',
            'home_ties', 'home_losses', 'home_points',
            'away_wins', 'away_ties', 'away_losses', 'away_points']
        #saving dataframe as csv
        if failure == False:
            df = pd.DataFrame(season_data, columns=columns)
            csv_file_path = os.getenv("CSV_FILE_PATH_MATCHES")
            df.to_csv(f'{csv_file_path}/{save_file_season}_{season}_season.csv', encoding='utf-8-sig', index=False)
            current_season_index += 1
        else:
            print("Something failed, trying again.")
            retries += 1
            failure=False

driver.quit()

