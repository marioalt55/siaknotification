from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from discord import Webhook
import os
import sys
import time
import datetime
import aiohttp
import asyncio

load_dotenv()

def siak_notify():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    login_url = "https://academic.ui.ac.id/main/Authentication/"
    homepage_url = "https://academic.ui.ac.id/main/Welcome/"
    logout_url = "https://academic.ui.ac.id/main/Authentication/Logout"
    siak_url = "https://academic.ui.ac.id/main/CoursePlan/CoursePlanEdit"

    # get credentials from env
    Username = os.environ["username"]
    Password = os.environ["password"]
    refresh_rate = 1
    display_name = os.environ["display_name"]

    def logout_page():
        print("Logging out!")
        driver.get(logout_url)
        time.sleep(0.1)

    def login_page():
        username = driver.find_element(By.NAME, "u")
        username.clear()
        username.send_keys(Username)
        time.sleep(0.1)

        password = driver.find_element(By.NAME, "p")
        password.clear()
        password.send_keys(Password)
        time.sleep(0.1)
        driver.find_element(By.XPATH, "//input[@value='Login']").click()
        time.sleep(2)

    def war_page():
        time.sleep(5)
        table_rows = driver.find_elements(By.XPATH, "//table[@class='box'][2]/tbody/tr[string(@id)]")

        bisa_ambil_rows = []

        for table_row in table_rows:
            kapasitas = table_row.find_element(By.XPATH, ".//td[@class='ri'][1]").text
            mahasiswa_ambil = table_row.find_element(By.XPATH, ".//td[@class='ri'][2]").text
            name = table_row.find_element(By.XPATH, ".//td[2]").text

            try:
                kapasitas = int(kapasitas)
                mahasiswa_ambil = int(mahasiswa_ambil)
                if (kapasitas > mahasiswa_ambil):
                    bisa_ambil_rows.append({
                        "name": name,
                        "kapasitas": kapasitas,
                        "mahasiswa_ambil": mahasiswa_ambil
                    })
            except ValueError:
                continue

        formatted_bisa_ambil_rows = []
        for i in range(len(bisa_ambil_rows)):
            bisa_ambil_row = bisa_ambil_rows[i]
            formatted_bisa_ambil_rows.append(f"{i+1}. {bisa_ambil_row['name']}. Kapasitas: {bisa_ambil_row['kapasitas']}, Mahasiswa yang Mengambil: {bisa_ambil_row['mahasiswa_ambil']}")

        formatted_string = 'Matkul yang bisa diambil:\n'
        formatted_string += '\n'.join(formatted_bisa_ambil_rows)
        asyncio.run(send_webhook(formatted_string))

    async def send_webhook(message):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(os.environ['discord_webhook_url'], session=session)
            await webhook.send(message)

    error = True
    scrape_not_done = True
    while(scrape_not_done):
        try:
            if(error):
                error = False
                driver.get(login_url)
            refresh_rate = 10
            if(datetime.datetime.now().minute >= 50): refresh_rate = 3
            if(datetime.datetime.now().minute >= 55 or datetime.datetime.now().minute <= 5): refresh_rate = 0.5
            time.sleep(refresh_rate)
            print(datetime.datetime.now())

            # refresh manual bre
            if(driver.current_url != "https://academic.ui.ac.id/main/Welcome/" and not "Magister Kriminologi" in driver.page_source):
                print("Trying to login bro!")
                driver.get(login_url)
                continue
            elif(driver.current_url != "https://academic.ui.ac.id/main/Welcome/"):
                login_page()
                time.sleep(refresh_rate)
                print(datetime.datetime.now())
                print("Sended login request bro!")
            if(not display_name in driver.page_source):
                print("Siak down bro!")
                time.sleep(0.2)
                driver.get(login_url)
                continue
            if("guest" in driver.page_source):
                print("Role guest bro!")
                time.sleep(0.2)
                logout_page()
                driver.get(login_url)
                continue
            print("BOI SAFELY LOGGED IN!")
            # case di homepage
            driver.get(siak_url)
            # logout, belom bisa ngisi
            if not "Basis Data" in driver.page_source:
                print("BELUM BISA NGISI")
                logout_page()
                driver.get(login_url)
                continue
            war_page()
            scrape_not_done = False
        except Exception as e:
            error = True
            asyncio.run(send_webhook("Error happened"))
            break
    print("Masuk sini pasti kan")
    driver.close()

if __name__ == "__main__":
    siak_notify()