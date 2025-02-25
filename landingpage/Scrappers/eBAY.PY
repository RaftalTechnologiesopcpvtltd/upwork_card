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
access_token = "v^1.1#i^1#r^0#I^3#f^0#p^3#t^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"


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
    if "FIXED" in response_prod.get("buyingOptions")[0]:
        selling_type = "Fixed Price"
    else:
        selling_type = "Auction"

    extracted_data = normalize_data({
        "Website Name": "eBay",
        "Website URL": "https://www.ebay.com/",
        "Product Link": response_prod.get("itemWebUrl"),
        "Product Images": [response_prod["image"]["imageUrl"]] + [
            img.get("imageUrl") for img in response_prod.get("additionalImages", [])
        ],
        "Selling Type" : selling_type,
        "Product Title": response_prod.get("title"),
        "Product Price Currency": response_prod.get("price", {}).get("currency"),
        "Product Price": response_prod.get("price", {}).get("value"),
        "Current Bid Price": response_prod.get("currentBidPrice", {}).get("value"),
        "Current Bid Currency": response_prod.get("currentBidPrice", {}).get("currency"),
        "Current Bid Count": response_prod.get("bidCount"),
        "Description": response_prod.get('shortDescription'),
        "Condition": response_prod.get("condition"),
        "Condition Id": response_prod.get("conditionId"),
        "Condition Descriptors": response_prod.get("conditionDescriptors", [{}])[0].get("name"),
        "Condition Values": response_prod.get("conditionDescriptors", [{}])[0].get("values", [{}])[0].get("content"),
        "Condition Additional Info": response_prod.get("conditionDescriptors", [{}])[0].get("values", [{}])[0].get("additionalInfo"),
        "Product Availibility status": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedAvailabilityStatus"),
        "Product Availibility Quantity": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedAvailableQuantity"),
        "Product Sold Quantity": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedSoldQuantity"),
        "Product Remaining Quantity": response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedRemainingQuantity"),
        "Shipping Service Code": response_prod.get("shippingOptions", [{}])[0].get("shippingServiceCode"),
        "Shipping Carrier Code": response_prod.get("shippingOptions", [{}])[0].get("shippingCarrierCode"),
        "Shipping Type": response_prod.get("shippingOptions", [{}])[0].get("type"),
        "Shipping Cost": response_prod.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value"),
        "Shipping Currency": response_prod.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("currency"),
        "Additional Shipping Cost Per Unit": response_prod.get("shippingOptions", [{}])[0].get("additionalShippingCostPerUnit", {}).get("value"),
        "Additional Shipping Cost Currency": response_prod.get("shippingOptions", [{}])[0].get("additionalShippingCostPerUnit", {}).get("currency"),
        "Shipping Cost Type": response_prod.get("shippingOptions", [{}])[0].get("shippingCostType"),
        "Quantity Used For Estimate": response_prod.get("shippingOptions", [{}])[0].get("quantityUsedForEstimate"),
        "Min Estimated Delivery Date": response_prod.get("shippingOptions", [{}])[0].get("minEstimatedDeliveryDate"),
        "Max Estimated Delivery Date": response_prod.get("shippingOptions", [{}])[0].get("maxEstimatedDeliveryDate"),
        "buying Options": response_prod.get("buyingOptions")[0],
        "Certified Seller": response_prod.get("seller", {}).get("username"),
        "Minimum Price to Bid": response_prod.get("minimumPriceToBid", {}).get("value"),
        "Minimum Price Currency": response_prod.get("minimumPriceToBid", {}).get("currency"),
        "Unique Bidder Count": response_prod.get("uniqueBidderCount"),
        "Listing Id": response_prod.get("itemId"),
        "Integer Id": response_prod.get("legacyItemId"),
        "Listing Type": response_prod.get("buyingOptions"),
        "Status": "Active" if response_prod.get("estimatedAvailabilities", [{}])[0].get("estimatedAvailabilityStatus") == "IN_STOCK" else "Unavailable",
        "ReturnTerms returns Accepted": response_prod.get("returnTerms", {}).get("returnsAccepted"),
        "ReturnTerms refund Method": response_prod.get("returnTerms", {}).get("refundMethod"),
        "ReturnTerms return Shipping Cost Payer": response_prod.get("returnTerms", {}).get("returnShippingCostPayer"),
        "ReturnTerms return Period Value": response_prod.get("returnTerms", {}).get("returnPeriod", {}).get("value"),
        "ReturnTerms return Period Unit": response_prod.get("returnTerms", {}).get("returnPeriod", {}).get("unit"),
        "Payment Methods": [
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