import undetected_chromedriver as uc
import json
import os
import time
import logging
import boto3
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from fake_useragent import UserAgent

# AWS Configuration
S3_BUCKET_NAME = "your-s3-bucket-name"
s3_client = boto3.client('s3')

# Logging
logging.basicConfig(level=logging.INFO)
fivemiles_logger = logging.getLogger("5miles_scraper")

# ========================== Initialize Headless Chrome ==========================
def init_driver():
    options = uc.ChromeOptions()
    options.binary_location = "/opt/chrome"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    # Generate a random user-agent
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    driver = uc.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    return driver

# ========================== Clean Description ==========================
def clean_description(description):
    if not description:
        return ""

    soup = BeautifulSoup(description, "html.parser")

    # Replace <br>, <p>, and <div> tags with newlines
    for br in soup.find_all(["br", "p", "div"]):
        br.replace_with("\n")

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text)  # Normalize whitespace

    return text.strip()

# ========================== Get All City Links ==========================
def get_all_city_links(driver):
    driver.get("https://www.5miles.com/all-cities")

    try:
        driver.find_element(By.CSS_SELECTOR, 'button[class="close close-cookie-modal"]').click()
    except Exception:
        pass

    city_links = []
    cities = driver.find_element(By.CSS_SELECTOR, 'div[class="seo_con container"]').find_elements(By.TAG_NAME, 'a')

    for city in cities:
        href = city.get_attribute('href')
        if href:
            city_links.append(href.strip().replace("/c/", "/cq/"))

    return city_links

# ========================== Extract Data ==========================
def extract_data(driver, city_links):
    extracted_data = []

    for link in city_links[:10]:
        driver.get(f"{link}/sport%20cards")

        try:
            data = driver.find_element(By.ID, "container").get_attribute("data-initdataitems")
            parsed_data = json.loads(data)

            for item in parsed_data:
                product_data = {
                    "Website Name": "5miles",
                    "Website URL": "https://www.5miles.com/",
                    "Product Link": f"https://www.5miles.com/item/{item['id']}/{clean_description(item['title']).replace(' ', '-')}",
                    "Product Images": [img['imageLink'] for img in item.get('images', [])],
                    "Selling Type": "Fixed",
                    "Product Title": clean_description(item['title']),
                    "Product Price Currency": "$",
                    "Product Price": item.get('local_price', "-"),
                    "Description": clean_description(item.get('desc', "")),
                }
                extracted_data.append(product_data)

        except Exception as e:
            fivemiles_logger.error(f"Error scraping {link}: {e}")

    return extracted_data

# ========================== Save to S3 ==========================
def save_to_s3(data, filename):
    try:
        json_data = json.dumps(data, indent=4)
        file_path = f"/tmp/{filename}"

        with open(file_path, "w") as file:
            file.write(json_data)

        s3_client.upload_file(file_path, S3_BUCKET_NAME, filename)
        fivemiles_logger.info(f"Uploaded {filename} to S3")

    except Exception as e:
        fivemiles_logger.error(f"Failed to upload data to S3: {e}")

# ========================== Main Scraper ==========================
def run_fivemiles_scraper():
    driver = init_driver()

    try:
        city_links = get_all_city_links(driver)
        data = extract_data(driver, city_links)
        if data:
            save_to_s3(data, "fivemiles_data.json")

    finally:
        driver.quit()

# ========================== AWS Lambda Handler ==========================
def lambda_handler(event, context):
    fivemiles_logger.info("Starting 5miles scraper...")
    run_fivemiles_scraper()

    return {
        "statusCode": 200,
        "body": json.dumps("5miles scraper executed successfully.")
    }
