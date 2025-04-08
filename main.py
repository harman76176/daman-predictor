import os
import time
from datetime import datetime
from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MOBILE = os.getenv("MOBILE")
PASSWORD = os.getenv("PASSWORD")

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def login_and_scrape():
    driver = get_driver()
    driver.get("https://damangames.bet/#/login")
    time.sleep(5)

    try:
        # Enter mobile number and password
        driver.find_element(By.XPATH, "//input[@type='tel']").send_keys(MOBILE)
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        time.sleep(5)

        driver.get("https://damangames.bet/#/home/AllLotteryGames/WinGo?id=1")
        time.sleep(5)

        # Get the latest number
        num_div = driver.find_element(By.CLASS_NAME, "GameRecord__C-body-num")
        latest_number = num_div.text.strip()

        with open("results.csv", "a") as f:
            f.write(f"{datetime.now()},{latest_number}\n")

        driver.quit()
        return latest_number
    except Exception as e:
        driver.quit()
        return f"Error: {e}"

@app.route("/")
def index():
    result = None
    try:
        with open("results.csv", "r") as f:
            lines = f.readlines()[-10:]
        result = [line.strip().split(",") for line in lines]
    except:
        result = []

    return render_template("index.html", results=result)

if __name__ == "__main__":
    import sys
    if "--scrape" in sys.argv:
        while True:
            print("Scraping latest result...")
            print(login_and_scrape())
            time.sleep(60)
    else:
        app.run(host="0.0.0.0", port=10000)
