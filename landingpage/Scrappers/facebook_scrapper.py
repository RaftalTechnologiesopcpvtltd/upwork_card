import undetected_chromedriver as uc
import multiprocessing
import traceback  # Import traceback module
import sys
import shutil
import tempfile
from selenium_stealth import stealth
from fake_useragent import UserAgent
import requests
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json
import os
import re
import logging
from bs4 import BeautifulSoup
from dictionary_normanlizer import *
import os
import shutil
import tempfile
import undetected_chromedriver as uc
from selenium_stealth import stealth
from fake_useragent import UserAgent


from logger import *

facebook_scrapper_logger = setup_logger("facebook_scrapper_logger")


# def initializeProfile_driver():
#     # Define the ChromeDriver path (update this with your actual path)
#     CHROMEDRIVER_PATH = "chromedriver.exe"  # Change this accordingly

#     # Create a temporary directory for ChromeDriver
#     temp_dir = tempfile.mkdtemp(prefix="chrome_instance_")
#     driver_folder = os.path.join(temp_dir, "chromedriver")
#     os.makedirs(driver_folder, exist_ok=True)

#     # Copy ChromeDriver to the temp directory
#     driver_path = shutil.copy(CHROMEDRIVER_PATH, driver_folder)

#     # Use the local Chrome profile directory in your PWD
#     profile_path = os.path.join(os.getcwd(), "profile", "john")

#     # Set up Chrome options
#     options = uc.ChromeOptions()

#     options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory  # Use local profile
#     # options.add_argument(f"--profile-directory={PROFILE_NAME}")  # Ensure the correct profile is used
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--headless=new")  # New headless mode
#     options.add_argument("--window-size=1920,1080")
#     options.add_argument("--start-maximized")

#     # Generate a random user-agent
#     ua = UserAgent()
#     options.add_argument(f"user-agent={ua.random}")

#     # Initialize undetected_chromedriver with copied ChromeDriver
#     driver = uc.Chrome(driver_executable_path=driver_path, options=options)

#     # Apply Selenium Stealth
#     stealth(driver,
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True
#     )
#     return driver
def fb_login(driver):
    try:
        driver.get("https://www.facebook.com/marketplace")
        time.sleep(3)
        close_btn = driver.find_element(By.CSS_SELECTOR,'div[aria-label="Close"]')
        close_btn.click()
        time.sleep(3)
        email_input = driver.find_element(By.CSS_SELECTOR,'input[name="email"]')
        email_input.send_keys("johnhendersonsmith989@gmail.com")
        time.sleep(3)
        pasword_input = driver.find_element(By.CSS_SELECTOR,'input[name="pass"]')
        pasword_input.send_keys("Test@1234")
        time.sleep(3)
        login_btn = driver.find_element(By.CSS_SELECTOR,'div[aria-label="Log in"]').find_elements(By.TAG_NAME,'span')
        login_btn[-1].click()
        time.sleep(3)
    except:
        facebook_scrapper_logger.info("Already Login")

def get_face_prod_links(driver):
    driver.get("https://www.facebook.com/marketplace")
    search_url = driver.current_url+"/search/?query=treck%20bike"
    driver.get(search_url)
    prod_links = []
    for i in range(0,10):
        try:
            facebook_scrapper_logger.info(i)
            # Find the element (change XPath accordingly)
            element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div')))
            prod_cards = element.find_elements(By.CSS_SELECTOR,'a[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xkrqix3 x1sur9pj x1s688f x1lku1pv"]')
            # Scroll the element into view
            for href in prod_cards:
                try:
                    facebook_scrapper_logger.info("in")
                    prod_links.append(href.get_attribute('href'))
                except:
                    pass
            # Optional: Small delay to simulate real scrolling
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", prod_cards[-1])
            driver.implicitly_wait(1)

        except (NoSuchElementException, TimeoutException):
            facebook_scrapper_logger.info("No more elements found or scrolling stopped.")
            break  # Exit loop when no more elements are found
    return prod_links

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

def save_to_csv(data, filename=r"facebook_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    facebook_scrapper_logger.info(f"Data saved to {filename}")

def get_face_prod(driver,prod_links):
    for links in prod_links:
        driver.get(links)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.find("h1").text.strip()
        link = links


        # Find all images where 'alt' contains the product title
        filtered_images = [
            img.get("src") for img in soup.find_all("img")
            if img.get("alt") and title.lower() in img.get("alt").lower()
        ]
        price_info = soup.find("span",class_="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 xk50ysn xzsf02u").text.strip().split('·')
        description = clean_description(soup.find("div",class_="xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a").text.strip())
        if 'Condition' in soup.find("div",class_="x1cy8zhl x78zum5 x1qughib x1y1aw1k x4uap5 xwib8y2 xkhd6sd").text:
            condition = soup.find("span",class_="x1e558r4 xp4054r x3hqpx7").text.strip()
        price = price_info[0].strip()
        price_text = price.strip()

        # Use regex to extract the first price
        match = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d+)?', price_text)  # Find all prices like $25, $40
        if match:
            actual_price = match[0]  # First one is the actual price
        try:
            Status = price_info[1].strip()
        except:
            Status = "-"
        images = filtered_images
        # facebook_scrapper_logger.info the filtered image URLs
        prod_data = normalize_data({
            "Website Name": "Facebook",
            "Website URL": "https://www.facebook.com/marketplace",
            "Product Link": link,
            "Product Images": images,
            "Selling Type" : "Fixed",
            "Product Title": clean_description(title),
            "Product Price Currency": "$",
            "Product Price": actual_price,
            "Description": description,
            "Condition": condition,
            "Status" : Status,
        })
        save_to_csv(prod_data, filename=r"facebook_data.csv")

# if __name__ == "__main__":
#     driver = initializeProfile_driver()
#     prod_links = get_face_prod_links(driver)
#     get_face_prod(driver,prod_links)
