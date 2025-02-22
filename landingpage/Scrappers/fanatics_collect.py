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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import json
from dictionary_normanlizer import *

# Configure logging
log_filename = "fanatics_scraper.log"
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
    # Define the path to save the Chrome profile
    profile_path = os.path.join(os.getcwd(), "profile", "john")  # Profile path: ./profile/john

    # Create Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.fanaticscollect.com/")
    return driver

def get_dropdown_links(driver):
    all_dropdown_links = []
    sports_card = driver.find_element(By.XPATH,'//*[@id="header-menu"]/div[4]/div[2]/div')
    all_links = sports_card.find_elements(By.TAG_NAME,'a')
    for link in all_links:
        all_dropdown_links.append(link.get_attribute('href').split('&')[0])
        # print(link.get_attribute('href').split('&')[0])
    return all_dropdown_links

def get_prod_id(all_cards_links):
    prod_id = []
    for card_link in all_cards_links:
        pattern = r"/([a-f0-9\-]+)/"
        pattern_type = r"/([a-zA-Z0-9\-]+)/"

        # Search for the pattern
        match_id = re.search(pattern,card_link)
        match = re.search(pattern_type,card_link)

        # Extract the ID if found
        if match_id:
            extracted_id = match_id.group(1)
            type = match.group(1)
            if type == "fixed":
                type = f"{type}_price"

            prod_id.append({"id": extracted_id, "type": type.upper()})
            print({"id": extracted_id, "type": type.upper()})
    return prod_id


def get_prod_links(driver,all_dropdown_links):
    buying_option = ['WEEKLY','FIXED','PREMIER']
    all_cards_links_weekly = []
    all_cards_links_fixed = []
    all_cards_links_premier = []
    for dropdown_link in all_dropdown_links[:2]:
        for bo in buying_option[:1]:
            for i in range(1, 3):
                driver.get(f"{dropdown_link}&type={bo}&page={i}")
                time.sleep(10)    
            
                page_source = driver.page_source
                # Parse with BeautifulSoup
                soup = BeautifulSoup(page_source, "html.parser")
                cards_links_div=soup.find_all('div',{'class':'h-[100px] mobOnly:h-fit'})
                # Extract links from the card grid
                for card_link in cards_links_div:
                    href = card_link.find('a').get('href')
                    if bo == "WEEKLY":
                        all_cards_links_weekly.append(href)
                    elif bo == "FIXED":
                        all_cards_links_fixed.append(href)
                    elif bo == "PREMIER":
                        all_cards_links_premier.append(href)
    return all_cards_links_fixed,all_cards_links_premier,all_cards_links_weekly

def premier_resp(premier_prod_ids):
    url = "https://app.fanaticscollect.com/graphql"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8",
        # "authorization": "YOUR_AUTHORIZATION_HEADER",  # Replace with actual authorization value
        "content-type": "application/json",
        "origin": "https://www.fanaticscollect.com",
        "priority": "u=1, i",
        "referer": "https://www.fanaticscollect.com/",
        "sec-ch-ua": "\"Not(A:Brand)\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-platform": "WEB",
        # "x-session-id": "5240274b-027d-43a5-b375-de895055c186"  # Replace with actual session ID
    }

    payload = {
        "operationName": "webListingsQuery",
        "variables": {
            "listingIds": premier_prod_ids,
            "isAuction": True
        },
        "query": """
        query webListingsQuery($listingIds: [CollectListingIdInput]!, $isAuction: Boolean!) {
            collectListings(listingIds: $listingIds) {
                ...MarketplaceIndexListing
                __typename
            }
        }

        fragment Money on Money {
            amountInCents
            currency
            __typename
        }

        fragment ListingStates on CollectListingStates {
            userMaxBid {
                ...Money
                __typename
            }
            userCanBuy
            userBidStatus
            isClosed
            isFanaticsAuthentic
            isGreatPrice
            lastWindowWhenBidWasReceived
            isWatching
            __typename
        }

        fragment MarketplaceIndexListing on CollectListing {
            __typename
            id
            title
            integerId
            listingType
            imageSets {
                medium
                small
                thumbnail
                __typename
            }
            subtitle
            marketplaceEyeAppeal
            startingPrice {
                ...Money
                __typename
            }
            status
            lotString
            isOwner
            favoritedCount
            states {
                ...ListingStates
                __typename
            }
            collectSales {
                soldDate
                soldFor {
                    ...Money
                    __typename
                }
                __typename
            }
            slug
            certifiedSeller
            ... @include(if: $isAuction) {
                currentBid {
                    ...Money
                    __typename
                }
                bidCount
                highestBidder
                auction {
                    __typename
                    id
                }
                __typename
            }
            ... @skip(if: $isAuction) {
                buyNowPrice {
                    ...Money
                    __typename
                }
                previousAskingPrice {
                    ...Money
                    __typename
                }
                allowOffers
                __typename
            }
        }
        """
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload) if data else None)

        # Raise an error for bad status codes (4xx, 5xx)
        response.raise_for_status()

        data = response.json()

        products = data['data']['collectListings']

        return products  # Return response as JSON
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Return error as JSON response
    
def weekly_resp(weekly_prod_ids):
    url = "https://app.fanaticscollect.com/graphql"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8",
        # "authorization": "YOUR_AUTHORIZATION_HEADER",  # Replace with actual authorization value
        "content-type": "application/json",
        "origin": "https://www.fanaticscollect.com",
        "priority": "u=1, i",
        "referer": "https://www.fanaticscollect.com/",
        "sec-ch-ua": "\"Not(A:Brand)\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-platform": "WEB",
        # "x-session-id": "5240274b-027d-43a5-b375-de895055c186"  # Replace with actual session ID
    }

    payload = {
        "operationName": "webListingsQuery",
        "variables": {
            "listingIds": weekly_prod_ids,
            "isAuction": True
        },
        "query": """
        query webListingsQuery($listingIds: [CollectListingIdInput]!, $isAuction: Boolean!) {
            collectListings(listingIds: $listingIds) {
                ...MarketplaceIndexListing
                __typename
            }
        }

        fragment Money on Money {
            amountInCents
            currency
            __typename
        }

        fragment ListingStates on CollectListingStates {
            userMaxBid {
                ...Money
                __typename
            }
            userCanBuy
            userBidStatus
            isClosed
            isFanaticsAuthentic
            isGreatPrice
            lastWindowWhenBidWasReceived
            isWatching
            __typename
        }

        fragment MarketplaceIndexListing on CollectListing {
            __typename
            id
            title
            integerId
            listingType
            imageSets {
                medium
                small
                thumbnail
                __typename
            }
            subtitle
            marketplaceEyeAppeal
            startingPrice {
                ...Money
                __typename
            }
            status
            lotString
            isOwner
            favoritedCount
            states {
                ...ListingStates
                __typename
            }
            collectSales {
                soldDate
                soldFor {
                    ...Money
                    __typename
                }
                __typename
            }
            slug
            certifiedSeller
            ... @include(if: $isAuction) {
                currentBid {
                    ...Money
                    __typename
                }
                bidCount
                highestBidder
                auction {
                    __typename
                    id
                }
                __typename
            }
            ... @skip(if: $isAuction) {
                buyNowPrice {
                    ...Money
                    __typename
                }
                previousAskingPrice {
                    ...Money
                    __typename
                }
                allowOffers
                __typename
            }
        }
        """
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Raise an error for bad status codes (4xx, 5xx)
        response.raise_for_status()

        data = response.json()

        products = data['data']['collectListings']

        return products  # Return response as JSON
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Return error as JSON response


def fixed_resp(fixed_prod_ids):
    url = "https://app.fanaticscollect.com/graphql"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8",
        # "authorization": "",  # Add your authorization token here
        "content-type": "application/json",
        "origin": "https://www.fanaticscollect.com",
        "priority": "u=1, i",
        "referer": "https://www.fanaticscollect.com/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-platform": "WEB",
        # "x-session-id": "5240274b-027d-43a5-b375-de895055c186"
    }

    payload = {
        "operationName": "webListingsQuery",
        "variables": {
            "listingIds": fixed_prod_ids,
            "isAuction": False
        },
        "query": """
            query webListingsQuery($listingIds: [CollectListingIdInput]!, $isAuction: Boolean!) {
                collectListings(listingIds: $listingIds) {
                    ...MarketplaceIndexListing
                    __typename
                }
            }
            fragment Money on Money {
                amountInCents
                currency
                __typename
            }
            fragment ListingStates on CollectListingStates {
                userMaxBid {
                    ...Money
                    __typename
                }
                userCanBuy
                userBidStatus
                isClosed
                isFanaticsAuthentic
                isGreatPrice
                lastWindowWhenBidWasReceived
                isWatching
                __typename
            }
            fragment MarketplaceIndexListing on CollectListing {
                __typename
                id
                title
                integerId
                listingType
                imageSets {
                    medium
                    small
                    thumbnail
                    __typename
                }
                subtitle
                marketplaceEyeAppeal
                startingPrice {
                    ...Money
                    __typename
                }
                status
                lotString
                isOwner
                favoritedCount
                states {
                    ...ListingStates
                    __typename
                }
                collectSales {
                    soldDate
                    soldFor {
                        ...Money
                        __typename
                    }
                    __typename
                }
                slug
                certifiedSeller
                ... @include(if: $isAuction) {
                    currentBid {
                        ...Money
                        __typename
                    }
                    bidCount
                    highestBidder
                    auction {
                        __typename
                        id
                    }
                    __typename
                }
                ... @skip(if: $isAuction) {
                    buyNowPrice {
                        ...Money
                        __typename
                    }
                    previousAskingPrice {
                        ...Money
                        __typename
                    }
                    allowOffers
                    __typename
                }
            }
        """
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Raise an error for bad status codes (4xx, 5xx)
        response.raise_for_status()

        data = response.json()

        products = data['data']['collectListings']

        return products  # Return response as JSON
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}  # Return error as JSON response
    

    
def extract_listing_details(response):
    try:
        current_bid_amount = response.get("currentBid", {}).get("amountInCents", 0) / 100
    except TypeError:
        current_bid_amount = "N/A"

    try:
        user_max_bid = response.get("states", {}).get("userMaxBid", {}).get("amountInCents", 0) / 100
    except TypeError:
        user_max_bid = "N/A"

    try:
        starting_price = response.get("startingPrice", {}).get("amountInCents", 0) / 100
    except TypeError:
        starting_price = "N/A"

    listing_type = response.get("listingType")
    if "WEEKLY" in listing_type:
        type = "weekly"
    elif "FIXED" in listing_type:
        type = "fixed"
    elif "PREMIER" in listing_type:
        type = "premier"

    return normalize_data({
        "Website Name": "fanaticscollect",
        "Website URL": "https://www.fanaticscollect.com/",
        "Product Link": f"https://www.fanaticscollect.com/{type}/{response.get('id')}/{response.get('slug')}",
        "Product Title": response.get("title"),
        "Product Images": [img.get("medium") for img in response.get("imageSets", []) if img.get("medium")],
        "auction_id": response.get("auction", {}).get("id"),
        "bid_count": response.get("bidCount"),
        "certified_seller": response.get("certifiedSeller"),
        "current_bid": current_bid_amount,
        "current_bid_currency": response.get("currentBid", {}).get("currency"),
        "favorited_count": response.get("favoritedCount"),
        "highest_bidder": response.get("highestBidder"),
        "listing_id": response.get("id"),
        "integer_id": response.get("integerId"),
        "is_owner": response.get("isOwner"),
        "listing_type": response.get("listingType"),
        "lot_string": response.get("lotString"),
        "slug": response.get("slug"),
        "Product Price": starting_price,
        "starting_price_currency": response.get("startingPrice", {}).get("currency"),
        "is_closed": response.get("states", {}).get("isClosed"),
        "user_bid_status": response.get("states", {}).get("userBidStatus"),
        "user_max_bid": user_max_bid,
        "status": response.get("status"),
    })


def save_to_csv(data, filename="fanatics_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    logger.info(f"Data saved to {filename}")


def chunk_list(data_list, chunk_size=100):
    """
    Splits a list into smaller chunks of the specified size.

    :param data_list: List of items to be chunked
    :param chunk_size: Number of items per chunk (default: 100)
    :return: List of chunks (each chunk is a list)
    """
    return [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]



def main():    
    driver = initialize_driver()
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


main()