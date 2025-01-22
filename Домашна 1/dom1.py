import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import csv
import time

CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_argument('--headless')
CHROME_OPTIONS.add_argument('--disable-gpu')
CHROME_OPTIONS.add_argument('--no-sandbox')
CHROME_OPTIONS.add_argument('--disable-dev-shm-usage')

OUTPUT_DIR = 'records_storage'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_symbols(url, browser_config):
    with webdriver.Chrome(service=Service(), options=browser_config) as browser:
        browser.get(url)
        time.sleep(3)
        soup_content = BeautifulSoup(browser.page_source, 'html.parser')
    symbols = []
    dropdown = soup_content.find("select", id="Code")
    if dropdown:
        for option in dropdown.find_all("option"):
            symbol = option.get("value")
            if symbol and symbol.isalpha():
                symbols.append(symbol.strip())
    return symbols

def get_most_recent_date(symbol):
    filepath = os.path.join(OUTPUT_DIR, f"{symbol}.csv")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        dates = [row["Датум"] for row in reader if "Датум" in row and row["Датум"]]
        return max(dates, key=lambda date: datetime.strptime(date, "%d.%m.%Y")) if dates else None

def fetch_and_save_data(symbol, recent_date):
    endpoint = 'https://www.mse.mk/mk/stats/symbolhistory/ALK'
    headers = {"Content-Type": "application/json"}
    today = datetime.now()
    collected_rows = []
    start_date = datetime.strptime(recent_date, "%d.%m.%Y") + relativedelta(days=1) if recent_date else today - relativedelta(years=5)

    while start_date <= today:
        end_date = min(start_date + relativedelta(years=1) - relativedelta(days=1), today)
        response = requests.post(endpoint, headers=headers, json={
            "FromDate": start_date.strftime("%d.%m.%Y"),
            "ToDate": end_date.strftime("%d.%m.%Y"),
            "Code": symbol
        })
        parsed_content = BeautifulSoup(response.text, 'html.parser')
        rows = parsed_content.select("#resultsTable tr")
        for row in rows:
            columns = row.find_all("td")
            if columns:
                collected_rows.append({
                    "Датум": columns[0].text.strip(),
                    "Цена": columns[1].text.strip(),
                    "Максимум": columns[2].text.strip(),
                    "Минимум": columns[3].text.strip(),
                    "Просечна цена": columns[4].text.strip(),
                    "Промена": columns[5].text.strip(),
                    "Количина": columns[6].text.strip(),
                    "Вкупен Промет": columns[8].text.strip()
                })
        start_date = end_date + relativedelta(days=1)

    output_path = os.path.join(OUTPUT_DIR, f"{symbol}.csv")
    df = pd.DataFrame(collected_rows)
    if os.path.exists(output_path):
        df.to_csv(output_path, mode="a", header=False, index=False)
    else:
        df.to_csv(output_path, index=False)

def process_symbol(symbol):
    last_date = get_most_recent_date(symbol)
    fetch_and_save_data(symbol, last_date)

def run_scraper(data_url):
    start_time = time.time()
    symbols = extract_symbols(data_url, CHROME_OPTIONS)
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_symbol, symbols)
    elapsed_time = time.time() - start_time
    print(f"Database populated in: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    url = 'https://www.mse.mk/mk/stats/symbolhistory/ALK'
    run_scraper(url)
