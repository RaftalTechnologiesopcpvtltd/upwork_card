import multiprocessing
import time
import logging

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from craglist import *
from fanatics_collect import *
from eBAY import *
from offerUp import *
from mercari import *
# Import all the necessary functions from your scraper files
# from craglist import (
#     search_api_request, refresh_access_token, get_prod_ids, api_request_product, get_data, save_to_csv,
#     initialize_driver, get_dropdown_links, get_prod_links, get_prod_id, chunk_list,
#     weekly_resp, fixed_resp, premier_resp, extract_listing_details, get_all_location, get_prod,
#     get_see_all_links, extract_cards_links, extract_data, get_all_prod_links, get_product
# )

# ========================== eBay Scraper ==========================
def ebay_scraper():
    logger.info("Starting eBay Scraper...")
    search_url = "https://api.ebay.com/buy/browse/v1/item_summary/search?q=Sports Trading Card&limit=200&offset=0&filter=buyingOptions:{FIXED_PRICE|BEST_OFFER|AUCTION}"
    i = 0
    while search_url:
        if i == 2:
            break
        else:
            i += 1

        logger.info(f"Processing page: {search_url}")
        search_response = search_api_request(search_url, method="GET", token=access_token)

        if refresh_token and 'Unauthorized' in search_response.get('error', ''):
            logger.info("Access token expired. Refreshing...")
            access_token = refresh_access_token(refresh_token)
            search_response = search_api_request(search_url, method="GET", token=access_token)

        product_ids = get_prod_ids(search_response.get('itemSummaries'))
        for prod_id in product_ids:
            url = f"https://api.ebay.com/buy/browse/v1/item/{prod_id}"
            response_prod = api_request_product(url, method="GET", token=access_token)
            data = get_data(response_prod)
            save_to_csv(data, filename="data/Ebay_data.csv")
            time.sleep(3)

        search_url = search_response.get('next')  # Get next page
    logger.info("eBay Scraper finished.")

# ========================== Fanatics Scraper ==========================
def fanatics_scraper():
    logger.info("Starting Fanatics Scraper...")
    driver = fanatics_scraper_initialize_driver()
    wait = WebDriverWait(driver, 10)
    time.sleep(3)
    all_dropdown_links = get_dropdown_links(driver)
    time.sleep(3)

    all_links = get_prod_links(driver,all_dropdown_links[:2])
    all_cards_links_weekly = all_links[2]
    all_cards_links_fixed = all_links[0]
    all_cards_links_premier = all_links[1]
    weekly_prod_ids = get_prod_id(all_cards_links_weekly)
    fixed_prod_ids = get_prod_id(all_cards_links_fixed)
    premier_prod_ids = get_prod_id(all_cards_links_premier)

    weekly_prod_ids_chunks = chunk_list(weekly_prod_ids)
    fixed_prod_ids_chunks = chunk_list(fixed_prod_ids)
    premier_prod_ids_chunks = chunk_list(premier_prod_ids)

    for chunk in weekly_prod_ids_chunks:
        products = weekly_resp(chunk)
        for product in products:
            data = extract_listing_details(product)
            save_to_csv(data, filename="fanatics_data.csv")
        time.sleep(3)



    for chunk in fixed_prod_ids_chunks:
        products = fixed_resp(chunk)
        for product in products:
            data = extract_listing_details(product)
            save_to_csv(data, filename="fanatics_data.csv")
        time.sleep(3)


    for chunk in premier_prod_ids_chunks:
        products = premier_resp(chunk)
        for product in products:
            data = extract_listing_details(product)
            save_to_csv(data, filename="fanatics_data.csv")
        time.sleep(3)

    driver.quit()
    logger.info("Fanatics Scraper finished.")

# ========================== Mercari Scraper ==========================
def mercari_scraper():
    logger.info("Starting Mercari Scraper...")
    driver = mercari_scraper_initialize_driver()
    try:
        all_card_links = extract_cards_links(driver, get_see_all_links(driver))
        extract_data(all_card_links, driver)
    except Exception as e:
        logger.error(f"Error in Mercari Scraper: {e}")
    finally:
        driver.quit()
        logger.info("Mercari Scraper finished.")

# ========================== Another Scraper ==========================
def offerUp_scraper():
    logger.info("Starting Other Scraper...")
    driver = offerUp_scraper_initialize_driver()
    get_product(driver, get_all_prod_links(driver))
    driver.quit()
    logger.info("Other Scraper finished.")

def craglist_scraper():
    driver = initialize_driver()
    all_location_links = get_all_location(driver)
    get_prod(driver,all_location_links)
    logger.info("==============Finished==================")
# ========================== Running Scrapers in Parallel ==========================
# import threading

if __name__ == "__main__":
    logger.info("============= Starting All Scrapers =============")

    # Create processes for each scraper
    scrapers = [
        multiprocessing.Process(target=mercari_scraper),
        multiprocessing.Process(target=fanatics_scraper),
        multiprocessing.Process(target=craglist_scraper),
        multiprocessing.Process(target=offerUp_scraper),
    ]

    # Start all processes
    for scraper in scrapers:
        scraper.start()

    # Wait for all scrapers to finish
    for scraper in scrapers:
        scraper.join()

    logger.info("============= All Scrapers Finished =============")