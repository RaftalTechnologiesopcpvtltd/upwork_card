import undetected_chromedriver as uc
import multiprocessing
import shutil
import tempfile
import os
import time
import logging
from craglist import *
from fanatics_collect import *
from eBAY import *
from offerUp import *
from mercari import *
import traceback  # Import traceback module
import os
import sys
import django
import os
import time
import shutil
import tempfile
import traceback
import undetected_chromedriver as uc
from selenium_stealth import stealth
from fake_useragent import UserAgent

# Add the project root directory to sys.path
sys.path.append("d:/FAIZ/office work/dev project/MarketPlace")

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MarketPlace.settings")
django.setup()

# Now import the module
from landingpage.utils import *


# ========================== Fanatics Scraper ==========================
def fanatics_scraper(driver):

    try:
        # driver = fanatics_scraper_initialize_driver(driver)

        all_dropdown_links = get_dropdown_links(driver)
        all_links = get_prod_links(driver, all_dropdown_links[:2])

        all_cards_links_weekly = all_links[2]
        all_cards_links_fixed = all_links[0]
        all_cards_links_premier = all_links[1]

        weekly_prod_ids_chunks = chunk_list(get_prod_id(all_cards_links_weekly))
        fixed_prod_ids_chunks = chunk_list(get_prod_id(all_cards_links_fixed))
        premier_prod_ids_chunks = chunk_list(get_prod_id(all_cards_links_premier))

        for chunk in weekly_prod_ids_chunks:
            for product in weekly_resp(chunk):
                create_product(extract_listing_details(product))
                save_to_csv(extract_listing_details(product), filename=r"landingpage/data/fanatics_data.csv")
            time.sleep(3)

        for chunk in fixed_prod_ids_chunks:
            for product in fixed_resp(chunk):
                create_product(extract_listing_details(product))
                save_to_csv(extract_listing_details(product), filename=r"landingpage/data/fanatics_data.csv")
            time.sleep(3)

        for chunk in premier_prod_ids_chunks:
            for product in premier_resp(chunk):
                create_product(extract_listing_details(product))
                save_to_csv(extract_listing_details(product), filename=r"landingpage/data/fanatics_data.csv")
            time.sleep(3)

    except Exception as e:
        print(f"Error in Fanatics Scraper: {e}")
    
    finally:
        driver.quit()
        print("Fanatics Scraper finished.")

# ========================== Mercari Scraper ==========================
def mercari_scraper(driver):  # Accept driver as an argument

    try:
        # driver = mercari_scraper_initialize_driver(driver)

        all_card_links = extract_cards_links(driver, get_see_all_links(driver))
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

            mercari_logger.info(f"Extracted product: {product_data['Product Title']}")
            create_product(product_data)
            save_to_csv(product_data)

    except Exception as e:
        print(f"Error in Mercari Scraper: {e}")

    finally:
        driver.quit()
        print("Mercari Scraper finished.")

# ========================== Craigslist Scraper ==========================
def craglist_scraper(driver):  # Accept driver as an argument
    print("Starting Craigslist Scraper...")

    try:
        # driver = initialize_driver(driver)

        all_location_links = get_all_location(driver)
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
                        create_product(product)
                        save_to_csv(product, filename=r"landingpage/data/craglist.csv")
                        print("===============================================")
                        i += 1
                    except Exception as e:
                        craglist_logger.info(f"Error processing product: {e}")

            except Exception as e:
                craglist_logger.info(f"Error searching products: {e}")

    except Exception as e:
        print(f"Error in Craigslist Scraper: {e}")

    finally:
        driver.quit()
        print("Craigslist Scraper finished.")


# ========================== Ebbay Scraper ==========================
def ebay_scrapper():
    tokens = load_tokens()
    search_key = "Sports Trading Card"
    if tokens:
        print("Loaded Tokens:", tokens)
        refresh_token = tokens['refresh_token']
        access_token = tokens['access_token']
    search_url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={search_key}&limit=200&offset=0&filter=buyingOptions:{{FIXED_PRICE|BEST_OFFER|AUCTION}}" # Start with the first API endpoint
    i = 0
    while search_url:
        if i == 2:
            break
        else:
            i+=1
        print(f"Processing page: {search_url}")

        search_response = search_api_request(search_url, method="GET", token=access_token)  # Make API request and parse JSON
        

        if refresh_token:   
            # Later, check if the token is expired
            if 'Unauthorized' in search_response.get('error',''):
                print("Access token has expired. Refreshing token...")
                access_token = refresh_access_token(refresh_token)
                search_response = search_api_request(search_url, method="GET", token=access_token)  # Make API request and parse JSON
            else:
                print("Access token is still valid.")
        itemSummaries = search_response.get('itemSummaries')
        product_ids = get_prod_ids(itemSummaries)
        for prod_id in product_ids:
            url = f"https://api.ebay.com/buy/browse/v1/item/{prod_id}"

            response_prod = api_request_product(url, method="GET", token=access_token)
            data = get_data(response_prod)
            create_product(data)
            save_to_csv(data, filename=r"landingpage/data/Ebay_data.csv")
            time.sleep(3)
        # Extract the 'next' URL from the response
        search_url = search_response.get('next')  # Will be None if no more pages

    print("All pages processed.")

# ========================== Running Scrapers in Parallel ==========================

CHROMEDRIVER_PATH = r"landingpage/Scrappers/chromedriver.exe"

def run_scraper(scraper_func, instance_id):
    """Each browser instance runs its own unique scraping task."""
    temp_dir = tempfile.mkdtemp(prefix=f"chrome_instance_{instance_id}_")

    try:
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

        # Optional: Add proxy (if needed)
        proxy = "http://your_proxy_ip:port"  # Replace with your proxy
        # options.add_argument(f"--proxy-server={proxy}")  # Uncomment if using proxy

        print(f"[Instance {instance_id}] Running {scraper_func.__name__}...")

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

        scraper_func(driver)  # Now this works because scrapers accept a driver argument

        time.sleep(5)

    except Exception as e:
        print(f"Error in instance {instance_id}: {e}")
        print(traceback.format_exc())  # Proper traceback logging

        # Cloudflare fallback: Try using cloudscraper if Selenium fails
        print(f"[Instance {instance_id}] Attempting Cloudscraper fallback...")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"[Instance {instance_id}] Cleanup completed.")

def run_multiple_scrapers():
    """Runs all scrapers in parallel."""
    # scrapers = [fanatics_scraper, mercari_scraper, craglist_scraper]
    scrapers = [mercari_scraper]
    processes = []

    for i, scraper in enumerate(scrapers):
        p = multiprocessing.Process(target=run_scraper, args=(scraper, i))
        p.start()
        processes.append(p)

    # Run eBay scraper directly (since it does not require ChromeDriver)
    # ebay_scrapper()

    for p in processes:
        p.join()

if __name__ == "__main__":
    run_multiple_scrapers()