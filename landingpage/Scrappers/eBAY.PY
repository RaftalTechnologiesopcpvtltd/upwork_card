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
import json
import os
from logger import *


ebay_logger = setup_logger("Ebay_scraper")

# Define the path to save the Chrome profile
profile_path = os.path.join(os.getcwd(), "profile", "john")  # Profile path: ./profile/john

# Create Chrome options
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Set the user data directory

# eBay API Credentials (Replace with your actual credentials)
# {CLIENT_ID}:{CLIENT_SECRET}
CLIENT_ID = "FaizKhan-marketpl-PRD-cdec84608-ca82d8a7"
CLIENT_SECRET = "PRD-dec846085fd4-6c50-47cd-ade3-7b87"
REDIRECT_URI_NAME = "Faiz_Khan-FaizKhan-market-mgaex"
REDIRECT_URI = "https://auth.ebay.com/oauth2/authorize?client_id=FaizKhan-marketpl-PRD-cdec84608-ca82d8a7&response_type=code&redirect_uri=Faiz_Khan-FaizKhan-market-mgaex&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery"
# REDIRECT_URI = "YOUR_REDIRECT_URI"  # Must be the same as registered on eBay Developer Portal
SCOPES = "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery"

# eBay Token URLs (Use the sandbox URL for testing)

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"

TOKEN_FILE = r"landingpage/Scrappers/tokens.json"

def save_tokens(access_token, refresh_token):
    """Save access and refresh tokens to a JSON file."""
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(TOKEN_FILE, "w") as file:
        json.dump(tokens, file, indent=4)
    print("Tokens saved successfully.")

def load_tokens():
    """Load tokens from the JSON file."""
    if not os.path.exists(TOKEN_FILE):
        print("Token file not found.")
        return None

    try:
        with open(TOKEN_FILE, "r") as file:
            tokens = json.load(file)
            return tokens
    except json.JSONDecodeError:
        print("Error reading token file. File may be corrupted.")
        return None
    

def get_authorization_code():
    """
    Step 1: Redirects the user to the eBay OAuth page to obtain the authorization code.
    The user must manually log in and approve access.
    """
    # auth_url = (
    #     f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}"
    # )

    auth_url = REDIRECT_URI
    
    ebay_logger.info("Opening the following URL in your browser for authorization:")
    ebay_logger.info(auth_url)

    # Open the authorization URL in the default web browser
    driver = webdriver.Chrome(options=chrome_options)


    ebay_logger.info(f"Chrome profile created and saved at: {profile_path}")

    # Now you can interact with the browser, for example:
    # driver.get("https://auth.ebay.com/oauth2/authorize?client_id=FaizKhan-marketpl-PRD-8d243adb8-5c9e847a&response_type=code&redirect_uri=Faiz_Khan-FaizKhan-market-gltmirf&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/sell.reputation https://api.ebay.com/oauth/api_scope/sell.reputation.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly https://api.ebay.com/oauth/api_scope/sell.stores https://api.ebay.com/oauth/api_scope/sell.stores.readonly https://api.ebay.com/oauth/scope/sell.edelivery")
    driver.get(auth_url)

    ebay_logger.info("\nAfter authorizing, eBay will redirect you to your redirect URI with a code.")
    auth_code = None
    while True:
        current_url = driver.current_url
        if "isAuthSuccessful=true" in current_url:
            ebay_logger.info("success")
            auth_code = current_url.split("code=")[1].split("&expires_in")[0]
            break
        elif "isAuthSuccessful=true" in current_url:
            ebay_logger.info("Fail")
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
        ebay_logger.info(f"\nAccess Token: {token_data['access_token']}")
        ebay_logger.info(f"Refresh Token: {token_data['refresh_token']}")
        ebay_logger.info(f"Access Token Expiry: {token_data["expires_in"]} seconds")
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        save_tokens(access_token, refresh_token)
        return token_data["access_token"], token_data["refresh_token"]
    else:
        ebay_logger.info(f"\nError retrieving tokens: {response.status_code} {response.text}")
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
        ebay_logger.info(f"\nNew Access Token: {token_data['access_token']}")
        ebay_logger.info(f"New Access Token Expiry: {token_data["expires_in"]} seconds")
        access_token = token_data["access_token"]
        save_tokens(access_token, refresh_token)
        return token_data["access_token"]
    else:
        ebay_logger.info(f"\nError retrieving tokens: {response.status_code} {response.text}")
        return None
    
def get_prod_ids(itemSummaries):
    item_ids = []
    for id in itemSummaries:
        item_ids.append(id.get('itemId'))
        # ebay_logger.info(id.get('itemId'))
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
    
def ebay_get_data(response_prod):
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

def save_to_csv(data, filename=r"data/Ebay_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    ebay_logger.info(f"Data saved to {filename}")


# if __name__ == "__main__":
#     ebay_logger.info("### eBay OAuth2 Token Handling ###\n")

#     # Step 1: Get the Authorization Code (Manual Step)
#     auth_code = get_authorization_code()

#     # Step 2: Exchange Authorization Code for Access and Refresh Tokens
#     access_token, refresh_token = exchange_code_for_tokens(auth_code)
#     ebay_logger.info("Access Token : ",access_token)
#     ebay_logger.info("Referesh Token : ",refresh_token)

# if __name__ == "__main__":
    
#     tokens = load_tokens()
#     search_key = "Sports Trading Card"
#     if tokens:
#         print("Loaded Tokens:", tokens)
#         refresh_token = tokens['refresh_token']
#         access_token = tokens['access_token']
#     search_url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={search_key}&limit=200&offset=0&filter=buyingOptions:{{FIXED_PRICE|BEST_OFFER|AUCTION}}" # Start with the first API endpoint
#     i = 0
#     while search_url:
#         if i == 2:
#             break
#         else:
#             i+=1
#         ebay_logger.info(f"Processing page: {search_url}")

#         search_response = search_api_request(search_url, method="GET", token=access_token)  # Make API request and parse JSON
        

#         if refresh_token:   
#             # Later, check if the token is expired
#             if 'Unauthorized' in search_response.get('error',''):
#                 ebay_logger.info("Access token has expired. Refreshing token...")
#                 access_token = refresh_access_token(refresh_token)
#                 search_response = search_api_request(search_url, method="GET", token=access_token)  # Make API request and parse JSON
#             else:
#                 ebay_logger.info("Access token is still valid.")
#         itemSummaries = search_response.get('itemSummaries')
#         product_ids = get_prod_ids(itemSummaries)
#         for prod_id in product_ids:
#             url = f"https://api.ebay.com/buy/browse/v1/item/{prod_id}"

#             response_prod = api_request_product(url, method="GET", token=access_token)
#             data = get_data(response_prod)
#             save_to_csv(data, filename=r"data/Ebay_data.csv")
#             time.sleep(3)
#         # Extract the 'next' URL from the response
#         search_url = search_response.get('next')  # Will be None if no more pages

#     ebay_logger.info("All pages processed.")