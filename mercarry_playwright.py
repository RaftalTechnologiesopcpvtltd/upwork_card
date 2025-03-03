import asyncio
from playwright.async_api import async_playwright
import csv
import os
import re
import logging
from bs4 import BeautifulSoup
from dictionary_normanlizer import *
from logger import *

mercari_logger = setup_logger("Mercari_scraper")

async def get_see_all_links(page):
    """Extract 'See All' category links from the main page."""
    await page.goto("https://www.mercari.com/us/category/3511/")
    await page.wait_for_timeout(5000)

    try:
        consent_button = await page.query_selector("#truste-consent-button")
        if consent_button:
            await consent_button.click()
    except:
        pass

    see_all_tags = await page.query_selector_all('a[data-testid="CategoryHeader-SeeAll"]')
    see_all_headings = await page.query_selector_all('h3[data-testid="CategoryHeader-Name"]')

    see_all_links = [
        (await heading.inner_text(), await link.get_attribute('href'))
        for heading, link in zip(see_all_headings, see_all_tags)
    ]
    mercari_logger.info(f"Extracted {len(see_all_links)} 'See All' category links.")
    return see_all_links

async def extract_cards_links(page, see_all_links):
    """Extract all product card links from each category page."""
    all_card_links = []
    mercari_logger.info(f"see_all_links : {see_all_links}")

    for heading, link in see_all_links[:2]:
        await page.goto(link)
        await page.wait_for_timeout(3000)
        cards_links = []
        
        while True:
            try:
                await page.wait_for_selector('a[data-testid="ProductThumbWrapper"]', timeout=10000)
                cards_tags = await page.query_selector_all('a[data-testid="ProductThumbWrapper"]')
                mercari_logger.info(f"{heading}: Found {len(cards_tags)} product cards.")

                if not cards_tags:
                    mercari_logger.info(f"{heading}: No more links found. Exiting loop.")
                    break

                last_href = cards_links[-1] if cards_links else None 

                for link in cards_tags:
                    href = await link.get_attribute("href")
                    if href and href not in cards_links:
                        cards_links.append(href)
                        all_card_links.append(href)
                    else:
                        mercari_logger.info(f"{href} is already in cards_links")

                if last_href and last_href == await cards_tags[-1].get_attribute("href"):
                    mercari_logger.info(f"{heading}: No new links found. Stopping scrolling.")
                    break

                await cards_tags[-1].scroll_into_view_if_needed()
                await page.wait_for_timeout(3000)

            except Exception as e:
                mercari_logger.error(f"Error extracting cards from {heading}: {e}")
                break

    return all_card_links

def clean_description(description):
    """Clean the product description by removing HTML tags and extra spaces."""
    if not description:
        return ""

    soup = BeautifulSoup(description, "html.parser")
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()

async def get_text(page, selector, attr="text"):
    """Retrieve text or attribute from an element."""
    try:
        element = await page.query_selector(selector)
        if element:
            return (await element.text_content()).strip() if attr == "text" else (await element.get_attribute(attr)).strip()
    except:
        return "-"
    return "-"

def save_links_to_csv(cards_links, file_name):
    """Save extracted links to a CSV file."""
    csv_filename = f"{file_name}.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Links"])
        for link in cards_links:
            writer.writerow([link])

    mercari_logger.info(f"Links successfully saved to {csv_filename}")

def save_to_csv(data, filename=r"data/mercari_data.csv"):
    """Save product data to a CSV file."""
    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    mercari_logger.info(f"Data saved to {filename}")

async def extract_data(all_card_links, page):
    """Extract product details from all product links."""
    for link in all_card_links:
        await page.goto(link)
        await page.wait_for_timeout(5000)

        images_div = await page.query_selector('div[data-testid="InfinitePhotoCarousel"]')
        if not images_div:
            images_div = await page.query_selector('div[class="Product__WideWrapper-sc-366b9af2-3 jlGYfy"]')

        images = [await img.get_attribute('src') for img in await images_div.query_selector_all("img")] if images_div else "-"

        category_elements = await page.query_selector_all('//*[@id="main"]/div/div[3]/div/div[1]/div[4]/div[1]/div[7]/span/div/a')
        category = [await cat.text_content() for cat in category_elements] if category_elements else ["-"]

        product_data = normalize_data({
            "Website Name": "MERCARI",
            "Website URL": "https://www.mercari.com/",
            "Product Link": link,
            "Product Images": images,
            "Selling Type": "Fixed",
            "Product Title": await get_text(page, 'h1[data-testid="ItemName"]'),
            "Product Price Currency": "$",
            "Product Price": await get_text(page, 'p[data-testid="ItemPrice"]'),
            "Description": clean_description(await get_text(page, 'p[data-testid="ItemDetailsDescription"]')),
            "Condition": await get_text(page, 'p[data-testid="ItemDetailsCondition"]'),
            "Shipping Cost": await get_text(page, 'p[data-testid="ItemDetailsDelivery"]'),
            "Shipping Currency": "$",
            "Estimated Arrival": await get_text(page, 'p[data-testid="ItemDetailsEstArrival"]'),
            "Brand": await get_text(page, 'span[data-testid="ItemDetailsBrand"] a'),
            "Category": category,
            "Updated": await get_text(page, 'p[data-testid="ItemDetailExternalUpdated"]'),
        })

        mercari_logger.info(f"Extracted product: {product_data['Product Title']}")
        save_to_csv(product_data)

async def main():
    """Main execution function."""
    mercari_logger.info("Starting Mercari Scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            see_all_links = await get_see_all_links(page)
            all_card_links = await extract_cards_links(page, see_all_links)
            await extract_data(all_card_links, page)
        except Exception as e:
            mercari_logger.error(f"An error occurred: {e}")
        finally:
            await browser.close()
            mercari_logger.info("Scraper finished successfully.")

if __name__ == "__main__":
    asyncio.run(main())
