import undetected_chromedriver as uc
import shutil
import tempfile
import os
import os
import os
import shutil
import tempfile
import undetected_chromedriver as uc
from selenium_stealth import stealth
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json
import os
import re
import logging
from bs4 import BeautifulSoup
from dictionary_normanlizer import *

from logger import *

fivemiles_logger = setup_logger("5miles_scraper")



CHROMEDRIVER_PATH = r"chromedriver.exe"

def save_to_csv(data, filename=r"data/5miles_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    fivemiles_logger.info(f"Data saved to {filename}")

def initialize_driver():
    """Each browser instance runs its own unique scraping task."""
    temp_dir = tempfile.mkdtemp(prefix=f"chrome_instance_{2}_")

    driver_folder = os.path.join(temp_dir, "chromedriver")
    os.makedirs(driver_folder, exist_ok=True)
    driver_path = shutil.copy(CHROMEDRIVER_PATH, driver_folder)

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={temp_dir}")  # Unique profile
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")  # New headless mode
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    # Generate a random user-agent
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    # Initialize undetected_chromedriver with the copied binary

    driver = uc.Chrome(driver_executable_path=driver_path, options=options)

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

def get_all_city_links(driver):
    driver.get("https://www.5miles.com/all-cities")
    try:
        cookie_close_btn = driver.find_element(By.CSS_SELECTOR,'button[class="close close-cookie-modal"]').click()
    except:
        pass
    All_cities_links = []
    all_cities = driver.find_element(By.CSS_SELECTOR,'div[class="seo_con container"]').find_elements(By.TAG_NAME,'a')
    for city in all_cities:
        href = city.get_attribute('href')
        if href:
            href = href.strip().replace("/c/", "/cq/")  # Clean & Replace
            All_cities_links.append(href)
    return All_cities_links


def clean_description(description):
    """Clean the product description by removing HTML tags, <br> tags, and extra spaces."""
    if not description:
        return ""

    soup = BeautifulSoup(description, "html.parser")

    # Replace <br> and other break elements with newlines
    for br in soup.find_all(["br", "p", "div"]):  
        br.replace_with("\n")

    text = soup.get_text(separator=" ")  # Extract text while maintaining spacing
    text = re.sub(r"\s+", " ", text)  # Normalize multiple spaces/newlines to a single space
    return text.strip()

def get_data(driver,All_cities_links):
    for link in All_cities_links[:10]:
        driver.get(f"{link}/sport%20cards")
        try:
            data = driver.find_element(By.ID, "container").get_attribute("data-initdataitems")
            parsed_data = json.loads(data)  # Convert the JSON string into a Python dictionary
            for p_data in parsed_data:
                id = p_data['id']
                title = clean_description(p_data['title'])
                price = p_data['local_price']
                desc = clean_description(p_data['desc'])
                images = [img['imageLink'] for img in p_data.get('images', [])]
                product_data = normalize_data({
                    "Website Name": "5miles",
                    "Website URL": "https://www.5miles.com/",
                    "Product Link": f"https://www.5miles.com/item/{id}/{title.replace(" ","-")}",
                    "Product Images": images,
                    "Selling Type" : "Fixed",
                    "Product Title": title,
                    "Product Price Currency": "$",
                    "Product Price": price,
                    "Description": desc,
                })
                # fivemiles_logger.info(product_data)
                save_to_csv(product_data, filename=r"data/5miles_data.csv")
        except Exception as e:
            fivemiles_logger.info(f"Error in : {link} and Error is : {e}")
            # fivemiles_logger.info("===============================================")

if __name__ == "__main__":
    driver = initialize_driver()
    All_cities_links = get_all_city_links(driver)
    get_data(driver,All_cities_links)