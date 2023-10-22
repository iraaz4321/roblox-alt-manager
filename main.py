import time
import secrets
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import pickle
import os

import chromedriver_autoinstaller


chromedriver_autoinstaller.install()

def start_drivers():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    return webdriver.Chrome()

def get_product_id():
    print("Starting conversion from catalog to product. This might take a while.")
    handled = 0
    valid = 0
    with open("catalog_id.txt", "r") as f:
        with open("product_id.txt", "w+") as fw:
            read_ids = f.read()
            list_of_ids = read_ids.split(",")
            url = "https://economy.roblox.com/v2/assets/{}/details"
            for x in list_of_ids:
                try:
                    r = requests.get(url.format(x))
                    code = r.status_code
                    if code == 400:
                        continue
                    if code == 429:
                        list_of_ids.append(x)
                        print("Waiting due to rate limits.")
                        time.sleep(10)
                        continue
                    data = r.json()
                    handled += 1
                    if data.get("IsForSale", False):
                        valid += 1
                        fw.write(f"{data['ProductId']},")
                except Exception as e:
                    print(e)
                print(f"Converted {handled} where {valid} can be purchased.")
                time.sleep(0.5)
    print("Conversion done. Feel free to buy the items now.")

def get_asset_id():
    url = "https://catalog.roblox.com/v1/search/items?category=All&limit=100&maxPrice=0&minPrice=0&cursor={}"

    cursor = ""
    found = 0
    with open("catalog_id.txt", "w+") as f:
        while True:
            r = requests.get(url.format(cursor))
            data = r.json()
            if data.get("errors") is not None:
                print("Roblox api returned an error. Converting catalog ids to product ids.")
                break

            found += len(data["data"])
            for x in data["data"]:
                f.write(f"{x['id']},")
            print("Items saved so far", found)
            if data["nextPageCursor"] is None:
                break
            cursor = data["nextPageCursor"]

            time.sleep(1)

def log_in(driver, user, password=None):
    if os.path.isfile(f"cookies\\{user}.pkl") or password is None:
        cookies = pickle.load(open(f"cookies\\{user}.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
    else:
        driver.find_element(By.ID, "login-username").send_keys(user)
        driver.find_element(By.ID, "login-password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "btn-cta-lg").click()
        driver.find_element(By.ID, "login-button").click()

def save_user(user, password):
    with open("users.txt", "a") as f:
        f.write(f"{user}.{password}\n")

def read_users():
    with open("users.txt", "r") as f:
        return f.readlines()

def get_cookies(driver, user, password):
    url = "https://www.roblox.com/login"
    driver.get(url)
    log_in(driver, user, password)
    wait = WebDriverWait(driver, 600)
    wait.until(
        lambda driver: driver.current_url != url)
    pickle.dump(driver.get_cookies(), open(f"cookies\\{user}.pkl", "wb"))


def buy_items_by_control(driver):
    bundle = "https://www.roblox.com/bundles/{}/"
    buy_url = "https://www.roblox.com/{}/{}/"
    with open("catalog_id.txt", "r") as f:
        ids = f.read().split(",")
        for x in ids:
            if len(x) <= 3:
                item_type = "bundles"
            else:
                item_type = "catalog"
            url = buy_url.format(item_type, x)
            print(url)
            driver.get(url)
            try:
                driver.find_element(By.CLASS_NAME, "PurchaseButton").click()
                driver.find_element(By.XPATH, '//button[normalize-space()="Get Now"]').click()
            except:
                print("item owned or not free")

def create_account(driver, user="", password=""):
    driver.get("https://www.roblox.com/")
    if password == "":
        possible = "".join((string.ascii_letters, string.digits))
        password = "".join(secrets.choice(possible) for i in range(32))
    driver.find_element(By.CLASS_NAME, "btn-cta-lg").click()

    #  date
    days = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
            "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22",
            "23", "24", "25", "26", "27", "28"]
    driver.find_element(By.ID, "MonthDropdown").click()
    driver.find_element(By.CSS_SELECTOR, "option[value='Jan']").click()
    driver.find_element(By.ID, "DayDropdown").click()
    driver.find_element(By.CSS_SELECTOR, "option[value='{}']".format(secrets.choice(days))).click()
    driver.find_element(By.ID, "YearDropdown").click()
    driver.find_element(By.CSS_SELECTOR, "option[value='{}']".format(secrets.choice(range(1940, 2000)))).click()

    #  sign in
    driver.find_element(By.ID, "signup-username").send_keys(user)
    driver.find_element(By.ID, "signup-password").send_keys(password)
    driver.find_element(By.ID, "MaleButton").click()


    wait = WebDriverWait(driver, 600)
    wait.until(
        lambda driver: driver.current_url != "https://www.roblox.com/")

    pickle.dump(driver.get_cookies(), open(f"cookies\\{user}.pkl", "wb"))



def main(driver):
    while True:
        print("roblox alt manager")
        print("*" * 20)
        print("1: add new account")
        print("2: login")
        print("3: create new account")
        print("4: Update assets list")
        print("*" * 20)
        chosen = input("Choose: ")
        if chosen == "1":
            user = input("username: ")
            password = input("password: ")
            save_user(user, password)
            get_cookies(driver, user, password)
        if chosen == "2":
            lines = read_users()
            for i, line in enumerate(lines):
                print(f"{i}.  {line.strip().split('.')[0]}")
            acc = int(input("choose account: "))
            driver.get("https://www.roblox.com/login")
            log_in(driver, lines[acc].strip().split('.')[0], lines[acc].strip().split('.')[1])
            print("*" * 20)
            print("1: buy all free items")
            print("*" * 20)
            second_choice = input("choose: ")
            if second_choice == "1":
                buy_items_by_control(driver)
            else:
                pass
        if chosen == "3":
            user = input("User: ")
            password = input("password: ")
            create_account(driver, user, password)
        if chosen == "4":
            get_asset_id()
            get_product_id()
main(start_drivers())



def buy_items():
    cookie = "_BE48997273ADDDB403B1D4D7582C3FC90D3147C4A89E483C0D807BF3156697740FE0F6827E081EBAA5FD506A3AAAF169D2746B4D2ACC266DF39E90151846811DFB5444847EA71A173CB66FF6DF14180A68F82966025D54EAA33D9617088863EB9F1A100408AAE878FC0FF5D958F56E9E339BA8D27F86C1851C89470D7A9216B03E0DFF70AFCEE4FAEB9F17446CD0ABF7670737B55F0391D8402BA9A3D847D47371B0DDC2B33347B761FD87584A3960DCA97A0029F3E53778A6DFC7B98A2D89A0030A88C756475691EA180BD48A84D573D039CC9AD394FF27B7A46517D474AF29D6A94B6CF9518078987411B6D5C99DBCE0A439C8F0E7B287485A988B3C0CE6534587FC24D29CE3FC4E218E5D20FBA5DAF9F2C980EC86E1663B1E18B8B3F399F5E29521C0D54DB39FFD942B994FB41CFB8B99014DEA618A653BE19DC96F6FA41EB4F693FE"
    with requests.Session() as req:
        req.cookies['.ROBLOSECURITY'] = cookie
        try:
            r= req.post("https://auth.roblox.com/")
            token = r.headers["x-csrf-token"]
            r = req.post("https://auth.roblox.com/", headers = {"x-csrf-token": token})
            print(r.json())
        except Exception as e:
            print(e)
            input('Invalid Cookie! Can''t run scraper.\nPress enter to exit...')
            exit()

        headers = {
            "X-CSRF-TOKEN": token,
        }

        payload = {
            "expectedSellerId": 1,
            "expectedCurrency": 1,
            "expectedPrice": 0
        }
        url = "https://economy.roblox.com/v1/purchases/products/1229509932"
        r = req.post(url, headers={"X-CSRF-TOKEN": token}, data=payload)
        print(r.text)
        if r.status_code == 200:
            print("Successfully bought item")

        print(r.status_code)

