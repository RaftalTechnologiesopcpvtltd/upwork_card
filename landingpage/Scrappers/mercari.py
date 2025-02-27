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
log_filename = "mercari_scraper.log"
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

def initialize_driver():
    """Initialize the undetected Chrome driver with required options."""
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")  # Use "--headless=new" for newer Chrome versions

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.get("https://www.mercari.com/us/category/3511/")
    driver.save_screenshot("mercari.png")
    return driver


def get_see_all_links(driver):
    """Extract 'See All' category links from the main page."""
    try:
        driver.find_element(By.ID, "truste-consent-button").click()
    except NoSuchElementException:
        pass

    see_all_tags = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="CategoryHeader-SeeAll"]')
    see_all_headings = driver.find_elements(By.CSS_SELECTOR, 'h3[data-testid="CategoryHeader-Name"]')

    see_all_links = [
        (heading.text.strip(), link.get_attribute('href'))
        for heading, link in zip(see_all_headings, see_all_tags)
    ]
    logger.info(f"Extracted {len(see_all_links)} 'See All' category links.")
    return see_all_links


def extract_cards_links(driver, see_all_links):
    """Extract all product card links from each category page."""
    time.sleep(3)
    all_card_links = []
    print("driver : ",driver)
    print("see_all_links : ",see_all_links)

    for heading, link in see_all_links[:2]:
        driver.get(link)
        time.sleep(3)
        cards_links = []
        file_name = heading
        # i = 0

        while True:
            try:
                # Find all links
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="ProductThumbWrapper"]')))
                cards_tags = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="ProductThumbWrapper"]')
                logger.info(f"{heading}: Found {len(cards_tags)} product cards.")

                # If no links are found, stop the loop
                if not cards_tags:
                    logger.info(f"{heading}: No more links found. Exiting loop.")
                    break

                last_href = cards_links[-1] if cards_links else None  # Get the last stored href safely

                for link in cards_tags:
                    href = link.get_attribute("href")
                    if href and href not in cards_links:
                        cards_links.append(href)
                        all_card_links.append(href)

                    else:
                        logger.info(f"{href} is already in cards_links")

                # If the last link in cards_links is the same as the last one found, stop scrolling
                if last_href and last_href == cards_tags[-1].get_attribute("href"):
                    logger.info(f"{heading}: No new links found. Stopping scrolling.")
                    break

                # Scroll to the last element
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cards_tags[-1])
                time.sleep(3)  # Allow time for loading

            except Exception as e:
                logger.error(f"Error extracting cards from {heading}: {e}")
                break
            # i += 1

        # all_card_links.append(cards_links)
        save_links_to_csv(cards_links, file_name)

    return all_card_links


def clean_description(description):
    """Clean the product description by removing HTML tags and extra spaces."""
    if not description:
        return ""

    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def get_text(driver, selector, attr="text"):
    """Retrieve text or attribute from an element."""
    try:
        if attr == "text":
            return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        return driver.find_element(By.CSS_SELECTOR, selector).get_attribute(attr).strip()
    except NoSuchElementException:
        return "-"


def save_links_to_csv(cards_links, file_name):
    """Save extracted links to a CSV file."""
    csv_filename = f"{file_name}.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Links"])
        for link in cards_links:
            writer.writerow([link])

    logger.info(f"Links successfully saved to {csv_filename}")


def save_to_csv(data, filename="mercari_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    logger.info(f"Data saved to {filename}")


def extract_data(all_card_links, driver):
    """Extract product details from all product links."""
    for link in all_card_links:
        driver.get(link)
        time.sleep(5)

        try:
            images_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="InfinitePhotoCarousel"]')
        except NoSuchElementException:
            try:
                images_div = driver.find_element(By.CSS_SELECTOR,
                                                 'div[class="Product__WideWrapper-sc-366b9af2-3 jlGYfy"]')
            except NoSuchElementException:
                images_div = None

        images = [img.get_attribute('src') for img in images_div.find_elements(By.TAG_NAME, "img")] if images_div else "-"

        try:
            category_elements = driver.find_element(By.XPATH,
                                                    '//*[@id="main"]/div/div[3]/div/div[1]/div[4]/div[1]/div[7]/span/div').find_elements(
                By.TAG_NAME, 'a')
            category = [cat.text.strip() for cat in category_elements]
        except NoSuchElementException:
            category = ["-"]

        product_data = normalize_data({
            "Website Name": "MERCARI",
            "Website URL": "https://www.mercari.com/",
            "Product Link": link,
            "Product Images": images,
            "Selling Type" : "Fixed",
            "Product Title": get_text(driver, 'h1[data-testid="ItemName"]'),
            "Product Price Currency": "$",
            "Product Price": get_text(driver, 'p[data-testid="ItemPrice"]'),
            "Description": clean_description(get_text(driver, 'p[data-testid="ItemDetailsDescription"]')),
            "Condition": get_text(driver, 'p[data-testid="ItemDetailsCondition"]'),
            "Shipping Cost": get_text(driver, 'p[data-testid="ItemDetailsDelivery"]'),
            "Shipping Currency": "$",
            "Estimated Arrival": get_text(driver, 'p[data-testid="ItemDetailsEstArrival"]'),
            "Brand": get_text(driver, 'span[data-testid="ItemDetailsBrand"] a'),
            "Category": category,
            "Updated": get_text(driver, 'p[data-testid="ItemDetailExternalUpdated"]'),
        })

        logger.info(f"Extracted product: {product_data['Product Title']}")
        save_to_csv(product_data)


def main():
    """Main execution function."""
    logger.info("Starting Mercari Scraper...")

    """Main execution function."""
    logger.info("Starting Mercari Scraper...")
    
    driver = initialize_driver()
    
    try:
        see_all_links = get_see_all_links(driver)
        all_card_links = extract_cards_links(driver, see_all_links)
        extract_data(all_card_links, driver)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        driver.quit()
        logger.info("Scraper finished successfully.")


if __name__ == "__main__":
    main()
