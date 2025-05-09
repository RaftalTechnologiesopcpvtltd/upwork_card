import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv
import os
import re
import logging
from bs4 import BeautifulSoup
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import re
import logging
from bs4 import BeautifulSoup
from dictionary_normanlizer import *
from logger import *
import undetected_chromedriver as uc
from selenium_stealth import stealth
from fake_useragent import UserAgent

craglist_logger = setup_logger("Craglist_scraper")

def initialize_driver():
    """Each browser instance runs its own unique scraping task."""
    

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless=new")  # New headless mode
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    # Generate a random user-agent
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    # Initialize undetected_chromedriver with the copied binary

    driver = uc.Chrome(options=options)

    # Apply selenium stealth to avoid detection
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True
    )
    return driver

def save_to_csv(data, filename=r"landingpage\data\craglist.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    craglist_logger.info(f"Data saved to {filename}")



def get_all_location(driver):
    driver.get("https://geo.craigslist.org/iso/us")
    time.sleep(5)
    driver.save_screenshot("craigslist.png")

    all_location  = driver.find_element(By.CLASS_NAME,"simple-page-content").find_elements(By.TAG_NAME,'a')
    all_location_links = []
    for link in all_location:
        href = link.get_attribute("href")
        all_location_links.append(href)
    craglist_logger.info(f"all_location_links : {all_location_links}")
    return all_location_links

def get_prod(driver, all_location_links):
    i = 1  # Initialize i

    for web_url in all_location_links[:2]:
        craglist_logger.info(f"Going for {web_url}")
        driver.get(web_url + "search/cba")

        try:
            # Wait for search input
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[enterkeyhint="search"]'))
            )
            search_input.send_keys("Sports Cards")
            search_input.send_keys(Keys.ENTER)

            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cl-search-result'))
            )

            prod_cards = driver.find_elements(By.CSS_SELECTOR, 'div.cl-search-result')
            

            for pro in prod_cards:
                try:
                    images = [img.get_attribute('src') for img in pro.find_elements(By.TAG_NAME, 'img')]

                    a_tag = pro.find_elements(By.TAG_NAME, 'a')
                    href, name = ("", "Unknown") if len(a_tag) < 2 else (a_tag[1].get_attribute('href'), a_tag[1].text)

                    price_elements = pro.find_elements(By.CLASS_NAME, 'priceinfo')
                    price = price_elements[0].text if price_elements else '-'

                    product = normalize_data({
                        "Website Name": "Craigslist",
                        "Website URL": web_url,
                        "Product Link": href,
                        "Product Images": images,
                        "Selling Type" : "Fixed",
                        "Product Title": name,
                        "Product Price Currency": "$",
                        "Product Price": price,
                    })

                    craglist_logger.info(f"======== {i}")
                    # print(product)
                    # create_product(product)
                    save_to_csv(product, filename=r"landingpage\data\craglist.csv")
                    print("===============================================")
                    i += 1
                except Exception as e:
                    craglist_logger.info(f"Error processing product: {e}")

        except Exception as e:
            craglist_logger.info(f"Error searching products: {e}")

if __name__ == "__main__":
#     craglist_logger.info("==============Start==================")

    driver = initialize_driver()
    all_location_links = get_all_location(driver)
    get_prod(driver,all_location_links)
    craglist_logger.info("==============Finished==================")