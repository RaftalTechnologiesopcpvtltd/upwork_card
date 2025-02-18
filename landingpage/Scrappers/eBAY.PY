import base64
import requests
import webbrowser
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import logging
import csv
from dictionary_normanlizer import *




# Configure logging
log_filename = "Ebay_scraper.log"
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

# Define the path to save the Chrome profile
profile_path = os.path.join(os.getcwd(), "profile", "john")  # Profile path: ./profile/john

# Create Chrome options
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory

# eBay API Credentials (Replace with your actual credentials)
# {CLIENT_ID}:{CLIENT_SECRET}
CLIENT_ID = "FaizKhan-marketpl-PRD-8d243adb8-5c9e847a"
CLIENT_SECRET = "PRD-d243adb8c21f-d6c8-4ac8-853c-a081"
REDIRECT_URI_NAME = "Faiz_Khan-FaizKhan-market-gltmirf"
REDIRECT_URI = "https://auth.ebay.com/oauth2/authorize?client_id=FaizKhan-marketpl-PRD-8d243adb8-5c9e847a&response_type=code&redirect_uri=Faiz_Khan-FaizKhan-market-gltmirf&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery"

# REDIRECT_URI = "YOUR_REDIRECT_URI"  # Must be the same as registered on eBay Developer Portal
SCOPES = "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery"

# eBay Token URLs (Use the sandbox URL for testing)
# AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"


import base64
import requests
import webbrowser
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

# Define the path to save the Chrome profile
profile_path = os.path.join(os.getcwd(), "profile", "john")  # Profile path: ./profile/john

# Create Chrome options
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory

# eBay API Credentials (Replace with your actual credentials)
# {CLIENT_ID}:{CLIENT_SECRET}
CLIENT_ID = "FaizKhan-marketpl-PRD-8d243adb8-5c9e847a"
CLIENT_SECRET = "PRD-d243adb8c21f-d6c8-4ac8-853c-a081"
REDIRECT_URI_NAME = "Faiz_Khan-FaizKhan-market-gltmirf"
REDIRECT_URI = "https://auth.ebay.com/oauth2/authorize?client_id=FaizKhan-marketpl-PRD-8d243adb8-5c9e847a&response_type=code&redirect_uri=Faiz_Khan-FaizKhan-market-gltmirf&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery"

# REDIRECT_URI = "YOUR_REDIRECT_URI"  # Must be the same as registered on eBay Developer Portal
SCOPES = "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery"

# eBay Token URLs (Use the sandbox URL for testing)
# AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"

refresh_token = "v^1.1#i^1#I^3#r^1#p^3#f^0#t^Ul4xMF8wOkVCNTJGODRFMDMzMUUwRkRFNUYzN0EyMTBGMUU3QUI0XzFfMSNFXjI2MA=="
access_token = "v^1.1#i^1#p^3#r^0#I^3#f^0#t^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"


def get_authorization_code():
    """
    Step 1: Redirects the user to the eBay OAuth page to obtain the authorization code.
    The user must manually log in and approve access.
    """
    # auth_url = (
    #     f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}"
    # )

    auth_url = REDIRECT_URI
    
    logger.info("Opening the following URL in your browser for authorization:")
    logger.info(auth_url)

    # Open the authorization URL in the default web browser
    driver = webdriver.Chrome(options=chrome_options)

    # Open any website to initialize the profile
    # driver.get("https://www.google.com")

    # Wait to ensure the profile is saved properly
    # import time
    # time.sleep(5)

    # Close the browser
    # driver.quit()

    logger.info(f"Chrome profile created and saved at: {profile_path}")

    # Now you can interact with the browser, for example:
    driver.get("https://auth.ebay.com/oauth2/authorize?client_id=FaizKhan-marketpl-PRD-8d243adb8-5c9e847a&response_type=code&redirect_uri=Faiz_Khan-FaizKhan-market-gltmirf&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery")


    logger.info("\nAfter authorizing, eBay will redirect you to your redirect URI with a code.")
    auth_code = None
    while True:
        current_url = driver.current_url
        if "isAuthSuccessful=true" in current_url:
            logger.info("success")
            auth_code = current_url.split("code=")[1].split("&expires_in")[0]
            break
        elif "isAuthSuccessful=true" in current_url:
            logger.info("Fail")
            # auth_code = current_url.split("code=")[1].split("&expires_in")[0]
            break
    
    return urllib.parse.unquote(auth_code)



def exchange_code_for_tokens(auth_code):
    """
    Step 2: Exchanges the authorization code for an access token and refresh token.
    """
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI_NAME,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        logger.info("\nAccess Token:", token_data["access_token"])
        logger.info("Refresh Token:", token_data["refresh_token"])
        logger.info("Access Token Expiry:", token_data["expires_in"], "seconds")
        return token_data["access_token"], token_data["refresh_token"]
    else:
        logger.info("\nError retrieving tokens:", response.status_code, response.text)
        return None, None


def refresh_access_token(refresh_token):
    """
    Step 3: Uses the refresh token to obtain a new access token.
    """
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "https://api.ebay.com/oauth/api_scope",
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        logger.info("\nNew Access Token:", token_data["access_token"])
        logger.info("New Access Token Expiry:", token_data["expires_in"], "seconds")
        return token_data["access_token"]
    else:
        logger.info("\nError refreshing access token:", response.status_code, response.text)
        return None
    
def get_prod_ids(itemSummaries):
    item_ids = []
    for id in itemSummaries:
        item_ids.append(id.get('itemId'))
        # logger.info(id.get('itemId'))
    return  item_ids

def search_api_request(url, method="GET", headers=None, token=None, timeout=10):
    """
    Sends an API request with optional authentication.
    
    :param url: API endpoint URL
    :param method: HTTP method (GET, POST, PUT, DELETE, etc.)
    :param headers: Request headers (default: None)
    :param data: Form data for POST requests (default: None)
    :param params: Query parameters for GET requests (default: None)
    :param json: JSON data for POST/PUT requests (default: None)
    :param token: Bearer token for authentication (default: None)
    :param timeout: Timeout in seconds (default: 10)
    :return: Response JSON or text
    """
    try:
        if headers is None:
            headers = {}

        # Add Authorization header if token is provided
        if token:
            headers["Authorization"] = f"Bearer {token}"
            

        response = requests.request(method, url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise HTTP errors
        return response.json() if response.headers.get("Content-Type") == "application/json" else response.text
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def api_request_product(url, method="GET", headers=None, token=None, timeout=10):
    """
    Sends an API request with optional authentication.
    
    :param url: API endpoint URL
    :param method: HTTP method (GET, POST, PUT, DELETE, etc.)
    :param headers: Request headers (default: None)
    :param data: Form data for POST requests (default: None)
    :param params: Query parameters for GET requests (default: None)
    :param json: JSON data for POST/PUT requests (default: None)
    :param token: Bearer token for authentication (default: None)
    :param timeout: Timeout in seconds (default: 10)
    :return: Response JSON or text
    """
    try:
        if headers is None:
            headers = {}

        # Add Authorization header if token is provided
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.request(method, url, headers=headers,timeout=timeout)
        response.raise_for_status()  # Raise HTTP errors
        return response.json() if response.headers.get("Content-Type") == "application/json" else response.text
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
def get_data(response_prod):
    extracted_data = normalize_data({
        "Website Name": "eBay",
        "Website URL": "https://www.ebay.com/",
        "Product Link": response_prod.get("itemWebUrl"),
        "Product Title": response_prod.get("title"),
        "Product Images": [response_prod["image"]["imageUrl"]] + [
            img.get("imageUrl") for img in response_prod.get("additionalImages", [])
        ],
        "Product Availibility status": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedAvailabilityStatus"),
        "Product Availibility Quantity": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedAvailableQuantity"),
        "Product Sold Quantity": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedSoldQuantity"),
        "Product Remaining Quantity": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedRemainingQuantity"),
        "Description": response_prod.get('shortDescription'),
        "Shipping Service Code": response_prod.get("shippingOptions", [{}])[0].get("shippingServiceCode"),
        "Shipping Carrier Code": response_prod.get("shippingOptions", [{}])[0].get("shippingCarrierCode"),
        "Type": response_prod.get("shippingOptions", [{}])[0].get("type"),
        "Shipping Cost": response_prod.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value"),
        "Currency": response_prod.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("currency"),
        "Quantity Used For Estimate": response_prod.get("shippingOptions", [{}])[0].get("quantityUsedForEstimate"),
        "Min Estimated Delivery Date": response_prod.get("shippingOptions", [{}])[0].get("minEstimatedDeliveryDate"),
        "Max Estimated Delivery Date": response_prod.get("shippingOptions", [{}])[0].get("maxEstimatedDeliveryDate"),
        "Additional Shipping Cost Per Unit": response_prod.get("shippingOptions", [{}])[0].get("additionalShippingCostPerUnit", {}).get("value"),
        "Additional Shipping Cost Currency": response_prod.get("shippingOptions", [{}])[0].get("additionalShippingCostPerUnit", {}).get("currency"),
        "Shipping Cost Type": response_prod.get("shippingOptions", [{}])[0].get("shippingCostType"),
        "buyingOptions": response_prod.get("buyingOptions")[0],
        "bid_count": response_prod.get("bidCount"),
        "certified_seller": response_prod.get("seller", {}).get("username"),
        "current_bid_currency": response_prod.get("currentBidPrice", {}).get("currency"),
        "current_bid_price": response_prod.get("currentBidPrice", {}).get("value"),
        "Minimum Price to Bid": response_prod.get("minimumPriceToBid", {}).get("value"),
        "Minimum Price Currency": response_prod.get("minimumPriceToBid", {}).get("currency"),
        "Unique Bidder Count": response_prod.get("uniqueBidderCount"),
        "listing_id": response_prod.get("itemId"),
        "integer_id": response_prod.get("legacyItemId"),
        "listing_type": response_prod.get("buyingOptions"),
        "Product Price": response_prod.get("price", {}).get("value"),
        "starting_price_currency": response_prod.get("price", {}).get("currency"),
        "status": "Active" if response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedAvailabilityStatus") == "IN_STOCK" else "Unavailable",
        "Condition": response_prod.get("condition"),
        "conditionId": response_prod.get("conditionId"),
        "conditionDescriptors": response_prod.get("conditionDescriptors", [{}])[0].get("name"),
        "condition_values": response_prod.get("conditionDescriptors", [{}])[0].get("values", [{}])[0].get("content"),
        "condition_additional_info": response_prod.get("conditionDescriptors", [{}])[0].get("values", [{}])[0].get("additionalInfo"),
        "returnTerms_returnsAccepted": response_prod.get("returnTerms", {}).get("returnsAccepted"),
        "returnTerms_refundMethod": response_prod.get("returnTerms", {}).get("refundMethod"),
        "returnTerms_returnShippingCostPayer": response_prod.get("returnTerms", {}).get("returnShippingCostPayer"),
        "returnTerms_returnPeriod_value": response_prod.get("returnTerms", {}).get("returnPeriod", {}).get("value"),
        "returnTerms_returnPeriod_unit": response_prod.get("returnTerms", {}).get("returnPeriod", {}).get("unit"),
        "paymentMethods": [
            method.get("paymentMethodType") for method in response_prod.get("paymentMethods", [])
        ],
    })
    return extracted_data

def save_to_csv(data, filename="Ebay_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    logger.info(f"Data saved to {filename}")


# if __name__ == "__main__":
#     logger.info("### eBay OAuth2 Token Handling ###\n")

#     # Step 1: Get the Authorization Code (Manual Step)
#     auth_code = get_authorization_code()

#     # Step 2: Exchange Authorization Code for Access and Refresh Tokens
#     access_token, refresh_token = exchange_code_for_tokens(auth_code)
#     logger.info("Access Token : ",access_token)
#     logger.info("Referesh Token : ",refresh_token)

if __name__ == "__main__":
    

    search_url = "https://api.ebay.com/buy/browse/v1/item_summary/search?q=Sports Trading Card&limit=200&offset=0&filter=buyingOptions:{FIXED_PRICE|BEST_OFFER|AUCTION}"  # Start with the first API endpoint
    i = 0
    while search_url:
        if i == 2:
            break
        else:
            i+=1
        logger.info("Processing page:", search_url)

        search_response = search_api_request(search_url, method="GET", token=access_token)  # Make API request and parse JSON
        if refresh_token:   
            # Later, check if the token is expired
            if 'Unauthorized' in search_response.get('error',''):
                logger.info("Access token has expired. Refreshing token...")
                access_token = refresh_access_token(refresh_token)
                search_response = search_api_request(search_url, method="GET", token=access_token)  # Make API request and parse JSON
            else:
                logger.info("Access token is still valid.")
        itemSummaries = search_response.get('itemSummaries')
        product_ids = get_prod_ids(itemSummaries)
        for prod_id in product_ids:
            url = f"https://api.ebay.com/buy/browse/v1/item/{prod_id}"

            response_prod = api_request_product(url, method="GET", token=access_token)
            data = get_data(response_prod)
            save_to_csv(data, filename="Ebay_data.csv")
            time.sleep(3)
        # Extract the 'next' URL from the response
        search_url = search_response.get('next')  # Will be None if no more pages

    logger.info("All pages processed.")