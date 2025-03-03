import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv
import os
import re
import logging
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
log_filename = r"Scrapper loggers/offerUp_scraper.log"
logging.basicConfig(
    filename=log_filename,
    filemode="a+",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger()

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)


def offerUp_scraper_initialize_driver():
    # Define the path to save the Chrome profile
    profile_path = os.path.join(os.getcwd(), "profile", "john")  # Profile path: ./profile/john

    # Create Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://offerup.com/search?q=sports+cards")
    return driver




def get_all_prod_links(driver):
    i = 0
    all_prod_links = []
    while i<3:
        logger.info(f"{i+1} steps")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="page-content"]/div[2]/div[3]/main/div[2]/div/div[1]/ul')))

        prod_cards = driver.find_element(By.XPATH,'//*[@id="page-content"]/div[2]/div[3]/main/div[2]/div/div[1]/ul').find_elements(By.TAG_NAME,'li')
        if not prod_cards:
            logger.info(f"{prod_cards}: No more links found. Exiting loop.")
            break

        last_href = all_prod_links[-1] if all_prod_links else None  # Get the last stored href safely

        for prod_card in prod_cards:
            href = prod_card.find_element(By.TAG_NAME,'a').get_attribute('href')
            # logger.info(href)
            if href not in all_prod_links:
                all_prod_links.append(href)
            else:
                logger.info(f"{href} is already appended")
        # if last_href and last_href == prod_cards[-1].find_element(By.TAG_NAME,'a').get_attribute("href"):
        #     logger.info("No new links found. Stopping scrolling.")
        #     break
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", prod_cards[-1])
        time.sleep(3)
        i+=1
    return all_prod_links

def save_to_csv(data, filename="data\OfferUp_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    logger.info(f"Data saved to {filename}")

def get_product(driver,all_prod_links):
    for links in all_prod_links:
        ProductImagesURLS = "-"
        ProductTitle = "-"
        ProductPrice = "-"
        Shipping = "-"
        EstArrival = "-"
        Condition = "-"
        Brand = "-"
        Category = "-"
        Updated = "-"
        Description = "-"

        driver.get(links)

        time.sleep(3)

        details_div = driver.find_element(By.XPATH, '//*[@id="page-content"]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[1]') if driver.find_elements(By.XPATH, '//*[@id="page-content"]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[1]') else "-"

        info_div = details_div.find_elements(By.TAG_NAME, "p") if details_div != "-" else "-"

        ProductTitle = details_div.find_element(By.TAG_NAME, "h1").text.strip() if details_div != "-" and details_div.find_elements(By.TAG_NAME, "h1") else "-"

        Brand = driver.find_element(By.TAG_NAME, "dd").find_element(By.TAG_NAME, "p").text if driver.find_elements(By.TAG_NAME, "dd") else "-"

        try:
            # Try to find the first description
            description_element = driver.find_element(By.XPATH, '//*[@id="page-content"]/div[2]/main/div[1]/div/div[2]/div/div[5]/div[2]/div[2]/div/p')
            Description = description_element.text.strip()
        except:
            try:
                # If the first one fails, try the alternative XPath
                description_element = driver.find_element(By.XPATH, '//*[@id="page-content"]/div[2]/main/div[1]/div/div[2]/div/div[3]/div[2]/div[2]/div/p')
                Description = description_element.text.strip()
            except:
                # If both fail, assign "-"
                Description = "-"
        # Description = driver.find_element(By.XPATH, '//*[@id="page-content"]/div[2]/main/div[1]/div/div[2]/div/div[5]/div[2]/div[2]/div/p').text.strip() if driver.find_elements(By.XPATH, '//*[@id="page-content"]/div[2]/main/div[1]/div/div[2]/div/div[5]/div[2]/div[2]/div/p') else "-"

        images_div = driver.find_element(By.XPATH,'//*[@id="page-content"]/div[2]/main/div[1]/div/div[2]/div/div[1]/div/div[1]/div[1]/div/div').find_elements(By.TAG_NAME,"img")

        ProductImagesURLS = [img.get_attribute('src') for img in images_div] if images_div else "-"

        ProductPrice = driver.find_element(By.XPATH,'//*[@id="page-content"]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[1]/div[1]/div/div/p').text.strip()

        for info in info_div:
            # logger.info(info.text.strip())
            if "$" in info.text.strip():
                if ProductPrice and "Ships" in info.text.strip():
                    Shipping = info.text.strip() if info.text.strip() else "-"
            elif "updated" in info.text.strip() or "about" in info.text.strip() or "hours" in info.text.strip() or "minutes" in info.text.strip() or "seconds" in info.text.strip():
                Updated = info.text.strip() if info.text.strip() else "-"
            elif "Condition" in info.text.strip():
                Condition = info.text.strip() if info.text.strip() else "-"
            else:
                Category = info.text.strip() if info.text.strip() else "-"

        product_data = normalize_data({
            "Website Name": "OfferUP",
            "Website URL": "https://offerup.com/",
            "Product Link": links,
            "Product Images": ProductImagesURLS,
            "Selling Type" : "Fixed",
            "Product Title": ProductTitle,
            "Product Price Currency": "$",
            "Product Price": ProductPrice,
            "Description": Description,
            "Condition": Condition,
            "Shipping Cost": Shipping if Shipping else "-",
            "Shipping Currency": "$" if Shipping else "-",
            "Estimated Arrival": EstArrival,
            "Brand": Brand,
            "Category": Category,
            "Updated": Updated,
        })

        logger.info(product_data)
        save_to_csv(product_data, filename="data\OfferUp_data.csv")

# if __name__ == "__main__":
#     logger.info("==============Start==================")

#     driver = initialize_driver()
#     all_prod_links = get_all_prod_links(driver)
#     get_product(driver,all_prod_links)
#     logger.info("==============Finished==================")