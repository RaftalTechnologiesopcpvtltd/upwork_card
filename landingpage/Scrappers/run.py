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
from Fivemiles import *
from facebook_scrapper import *
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
        time.sleep(3)

        all_links = get_prod_links(driver,all_dropdown_links[1:3])
        all_cards_links_weekly = all_links[2]
        all_cards_links_fixed = all_links[0]
        all_cards_links_premier = all_links[1]
        weekly_prod_ids = get_prod_id(all_cards_links_weekly)
        print("weekly_prod_ids :",weekly_prod_ids)
        fixed_prod_ids = get_prod_id(all_cards_links_fixed)
        premier_prod_ids = get_prod_id(all_cards_links_premier)

        weekly_prod_ids_chunks = chunk_list(weekly_prod_ids)
        print("weekly_prod_ids_chunks :",weekly_prod_ids_chunks)
        fixed_prod_ids_chunks = chunk_list(fixed_prod_ids)
        premier_prod_ids_chunks = chunk_list(premier_prod_ids)

        for chunk in weekly_prod_ids_chunks:
            products = weekly_resp(chunk)
            for product in products:
                create_product(extract_listing_details(product))
                save_to_csv(extract_listing_details(product), filename=r"landingpage/data/fanatics_data.csv")
            time.sleep(3)

        for chunk in fixed_prod_ids_chunks:
            products = fixed_resp(chunk)
            for product in products:
                create_product(extract_listing_details(product))
                save_to_csv(extract_listing_details(product), filename=r"landingpage/data/fanatics_data.csv")
            time.sleep(3)

        for chunk in premier_prod_ids_chunks:
            products = premier_resp(chunk)
            for product in products:
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
            ebay_data = ebay_get_data(response_prod)
            create_product(ebay_data)
            save_to_csv(ebay_data, filename=r"landingpage/data/Ebay_data.csv")
            time.sleep(3)
        # Extract the 'next' URL from the response
        search_url = search_response.get('next')  # Will be None if no more pages

    print("All pages processed.")

# ========================== 5Miles Scraper ==========================
def five_miles_scrapper(driver):
    All_cities_links = get_all_city_links(driver)
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
                create_product(product_data)
                save_to_csv(product_data, filename=r"landingpage/data/5miles_data.csv")
        except Exception as e:
            fivemiles_logger.info(f"Error in : {link} and Error is : {e}")
            # fivemiles_logger.info("===============================================")


def offerUp_scrapper(driver):
    all_prod_links = get_all_prod_links(driver)
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
        create_product(product_data)
        save_to_csv(product_data, filename=r"landingpage/data/OfferUp_data.csv")

# ========================== Facebook Scraper ==========================
def facebook_scrapper(driver):
    #all fb code will be added
    try:
        fb_login(driver)
    except:
        pass
    
    prod_links = get_face_prod_links(driver)
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
        # Print the filtered image URLs
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
        save_to_csv(prod_data, filename=r"landingpage/data/facebook_data.csv")
        create_product(prod_data)

# ========================== Running Scrapers in Parallel ==========================

CHROMEDRIVER_PATH = r"landingpage/Scrappers/chromedriver.exe"
def run_fb_scraper(scraper_func, instance_id):
    try:
        # Create a temporary directory for ChromeDriver
        temp_dir = tempfile.mkdtemp(prefix="chrome_instance_")
        driver_folder = os.path.join(temp_dir, "chromedriver")
        os.makedirs(driver_folder, exist_ok=True)

        # Copy ChromeDriver to the temp directory
        driver_path = shutil.copy(CHROMEDRIVER_PATH, driver_folder)

        # Use the local Chrome profile directory in your PWD
        # Get the script's directory
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(SCRIPT_DIR, "profile", "john")


        # Set up Chrome options
        options = uc.ChromeOptions()

        options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory  # Use local profile
        # options.add_argument(f"--profile-directory={PROFILE_NAME}")  # Ensure the correct profile is used
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless=new")  # New headless mode
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        # Generate a random user-agent
        ua = UserAgent()
        options.add_argument(f"user-agent={ua.random}")

        # Initialize undetected_chromedriver with copied ChromeDriver
        driver = uc.Chrome(driver_executable_path=driver_path, options=options)

        # Apply Selenium Stealth
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
    # scrapers = [five_miles_scrapper,fanatics_scraper,craglist_scraper,offerUp_scrapper,facebook_scrapper]
    scrapers = [facebook_scrapper]
    processes = []

    for i, scraper in enumerate(scrapers):
        if 'facebook' in scraper.__name__:
            p = multiprocessing.Process(target=run_fb_scraper, args=(scraper, i))
        else:
            p = multiprocessing.Process(target=run_scraper, args=(scraper, i))
        p.start()
        processes.append(p)

    # Run eBay scraper directly (since it does not require ChromeDriver)
    # ebay_scrapper()

    for p in processes:
        p.join()

if __name__ == "__main__":
    run_multiple_scrapers()