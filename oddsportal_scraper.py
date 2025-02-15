from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from PIL import Image
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import csv
import re
import pandas as pd

#load .env file
load_dotenv()

#disable search engine question when opening chrome 
options = webdriver.ChromeOptions()
options.add_argument("--disable-search-engine-choice-screen")
options.add_argument("--start-maximized")

driver_path = os.getenv("DRIVER_PATH")

driver = webdriver.Chrome(executable_path = driver_path, options=options)

#format for example "2023-2024"
scrape_year = "2023-2024"

#changes the date so that it matches other datafiles dd-mm-yyyy
def convert_date_format(date_str):
    date_obj = datetime.strptime(date_str, '%d %b %Y')
    new_date_str = date_obj.strftime('%d-%m-%Y').lower()
    return new_date_str

for page in range(1,12):
    url = f"https://www.oddsportal.com/hockey/finland/liiga-{scrape_year}/results/#/page/{page}"
    #url = f"https://www.oddsportal.com/hockey/finland/liiga/results/#/page/{page}" #current year different url
    driver.get(url)
    wait = WebDriverWait(driver, 3)
    time.sleep(2)
    #site sometimes bugs and doesn't load the table, so refreshing
    driver.refresh()
    #doesn't load the table if doesn't scroll up
    driver.execute_script("window.scrollTo(0, 0);")


    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[3]/div[4]/div[1]/div[1]'))
        )
        time.sleep(6)
        
        #scrolling to reveal the whole table
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(6)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(6)
        #scraping the elements and turning them into a text
        elements = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[3]/div[4]/div[1]/div[1]'))
        )
        scraped_text = elements.text 
        
    except TimeoutException:
        print("Elementtiä ei löytynyt annetussa ajassa.")

#games are now in a text that contains each element in a different row, changing to list
scraped_list = scraped_text.split('\n')

#this is needed only for the current season, because it contains text like "tomorrow" instead of date
#scraped_list = scraped_list[20:]
#print(scraped_list)

#delete all random text like "Hockey", "/", "Finland" etc.
scraped_list = [row for row in scraped_list if "Hockey" not in row and "/" not in row and "Finland" not in row
                and "–" not in row and "B's" not in row and "OT" not in row and "pen." not in row and "Liiga" not in row]

#removes 1X2 from the list
indices_to_remove = set()
for i in range(len(scraped_list) - 2):
    if scraped_list[i] == "1" and scraped_list[i+1] == "X" and scraped_list[i+2] == "2":
        indices_to_remove.update([i, i+1, i+2])
        
scraped_list = [item for idx, item in enumerate(scraped_list) if idx not in indices_to_remove]


#2020 year contains cancelled and awarded matches so i'll remove those words
new_list = []
i = 0
while i < len(scraped_list):
    row = scraped_list[i]
    if row == "award.":
        new_list.append(row)
        new_list.append("-")  
        new_list.append("-")
        i += 1 
    elif row == "canc.":
        new_list.append(row)
        new_list.append("-")
    else:
        new_list.append(row)
    i += 1

scraped_list = new_list

#adding dates for each game
#years
year_1 = scrape_year.split("-")[0]
year_2 = scrape_year.split("-")[1]

def is_date(string):
    """Tarkistaa, sisältääkö merkkijono päivämäärän."""
    return year_1 in string or year_2 in string

updated_list = []
current_date = None

i = 0
while i < len(scraped_list):
    # Tarkista onko nykyinen alkio päivämäärä
    if is_date(scraped_list[i]):
        current_date = scraped_list[i]  # Tallenna nykyinen päivämäärä
        i += 10  # Hypätään 10 alkiota eteenpäin
        # Varmista, ettemme mene listan yli
        if i >= len(scraped_list):
            break
        # Jos seuraava kymmenes alkio ei ole päivämäärä, lisää nykyinen päivämäärä sen eteen
        if not is_date(scraped_list[i]):
            scraped_list.insert(i, current_date)
    else:
        # Jos ei ole päivämäärä (ei pitäisi tapahtua tässä logiikassa), siirry seuraavaan
        i += 1

#delete play offs
i=0
while i < len(scraped_list):
        if 'Play Offs' in scraped_list[i]:
            # Remove the item and the next 9 items
            del scraped_list[i:i+10]
        else:
            i += 1

#fix dates
def convert_dates_every_tenth_item(list):
    for i in range(0, len(list), 10):  # Start at index 0, end at the end of the list, step by 10
        try:
            # Attempt to convert every 10th item assuming it's a date
            list[i] = datetime.strptime(list[i], '%d %b %Y').strftime('%d-%m-%Y')
        except ValueError:
            # If conversion fails (not a date), skip the item
            continue
    return list

# Convert the dates in your list assuming every 10th item is a date
scraped_list = convert_dates_every_tenth_item(scraped_list)
print(scraped_list)

#csv
headers = ['date', 'time', 'home_team', 'home_goals', 'away_goals', 'away_team', 'bet_1', 'bet_X', 'bet_2', 'bet_site_count']

csv_file_path = os.getenv(f"CSV_FILE_PATH_ODDS")

# Write the data to a CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    
    # Assuming each game's data spans 10 elements in the list
    for i in range(0, len(scraped_list), 10):
        writer.writerow(scraped_list[i:i+10])

###delete 2 columns from file, because they are useless + fail when the dates are the same on different pages
# Lue CSV-tiedosto DataFrameen
df = pd.read_csv(f"{csv_file_path}/{scrape_year}")

# Poista 'time' ja 'bet_site_count' sarakkeet
df = df.drop(['time', 'bet_site_count'], axis=1)

# Tallenna muokattu DataFrame uudelleen CSV-tiedostoon
df.to_csv(csv_file_path, index=False)


driver.close()
