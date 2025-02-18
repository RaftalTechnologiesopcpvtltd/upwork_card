import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv
import os
import re
import logging
from bs4 import BeautifulSoup
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


def initialize_driver():
    # Define the path to save the Chrome profile
    profile_path = os.path.join(os.getcwd(), "profile", "john")  # Profile path: ./profile/john

    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Use profile
    chrome_options.add_argument("--blink-settings=imagesEnabled=true")  # Ensure images load
    chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.images": 1})  # Allow images
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection


    driver = webdriver.Chrome(options=chrome_options)
    return driver