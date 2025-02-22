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




# Configure logging
log_filename = "Craglist_scraper.log"
logging.basicConfig(
    filename=log_filename,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger()

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)


def save_to_csv(data, filename="craglist.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    logger.info(f"Data saved to {filename}")


def initialize_driver():
    # Define the path to save the Chrome profile
    profile_path = os.path.join(os.getcwd(), "profile", "john")  # Profile path: ./profile/john
    # Create Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://geo.craigslist.org/iso/us")
    return driver

def get_all_location(driver):
    all_location  = driver.find_element(By.CLASS_NAME,"simple-page-content").find_elements(By.TAG_NAME,'a')
    all_location_links = []
    for link in all_location:
        href = link.get_attribute("href")
        all_location_links.append(href)
    print("all_location_links : ",all_location_links)
    return all_location_links

def get_prod(driver, all_location_links):
    i = 1  # Initialize i

    for web_url in all_location_links[:2]:
        logger.info(f"Going for {web_url}")
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
                        "Website Name": "craigslist",
                        "Website URL": web_url,
                        "Product Link": href,
                        "Product Title": name,
                        "Product Images": images,
                        "Product Price": price,
                    })

                    print(f"======== {i}")
                    # print(product)
                    save_to_csv(product, filename="craglist.csv")
                    print("===============================================")
                    i += 1
                except Exception as e:
                    print(f"Error processing product: {e}")

        except Exception as e:
            print(f"Error searching products: {e}")

if __name__ == "__main__":
    logger.info("==============Start==================")

    driver = initialize_driver()
    all_location_links = get_all_location(driver)
    get_prod(driver,all_location_links)
    logger.info("==============Finished==================")