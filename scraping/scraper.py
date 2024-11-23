import logging
import random
from io import BytesIO

import requests
from PIL import Image

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from scraping.scraper_utilities import calculate_final_prices, sum_table_availabilities
from scraping.scraping_selectors import ScrapingSelectorsEnum
from utilities.common import ProductPartialParams
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)

ua = UserAgent()
user_agents = [
    ua.random,
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edge/91.0.864.59"
]


def get_random_user_agent():
    return random.choice(user_agents)


def setup_driver():
    user_agent = get_random_user_agent()
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={user_agent}")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def wait_for_element(driver, selector, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
    except TimeoutException:
        logging.error(f"Element with selector {selector} not found within {timeout} seconds.")
        return None


def fetch_product_data(product_data: ProductPartialParams):
    with setup_driver() as driver:
        driver.get(product_data.url)
        try:
            set_name = ""
            card_number = 0
            pokemon_species = ""

            product_title = get_product_title(driver, ScrapingSelectorsEnum.PRODUCT_NAME.value)
            product_subtitle = get_product_subtitle(driver, ScrapingSelectorsEnum.PRODUCT_NAME.value)
            final_average, min_price, max_price = get_price_data(driver, ScrapingSelectorsEnum.TABLE_PRICES.value)
            table_availability = get_table_availability(driver, ScrapingSelectorsEnum.TABLE_AVAILABILITIES.value)

            if product_data.product_type == "Singles":
                set_name = get_text_from_element(driver, ScrapingSelectorsEnum.SET_NAME.value)
                card_number = get_text_from_element(driver, ScrapingSelectorsEnum.CARD_NUMBER.value)
                product_image = get_product_image(driver, ScrapingSelectorsEnum.SINGLES_IMAGE.value)
                if product_data.tcg_name == "Pokemon":  # gestire ste cose se non è pokemon che so diverse
                    pokemon_species = get_text_from_element(driver, ScrapingSelectorsEnum.POKEMON_SPECIES.value)
                    total_availability = get_total_availability(driver,
                                                                ScrapingSelectorsEnum.SINGLES_TOTAL_AVAILABILITY.value)
            else:
                product_image = get_product_image(driver, ScrapingSelectorsEnum.SEALED_IMAGE.value)
                total_availability = get_total_availability(driver,
                                                            ScrapingSelectorsEnum.SEALED_TOTAL_AVAILABILITY.value)

            product_data = {
                "id_url": product_data.url,
                "product_name": product_data.product_name,
                "title": product_title or "",
                "subtitle": product_subtitle or "",
                "image": product_image,
                "product_type": product_data.product_type,
                "set_name": set_name or "",
                "card_number": card_number or "",
                "language": product_data.language,
                "condition": product_data.condition or "",
                "tcg_name": product_data.tcg_name,
                "pokemon_species": pokemon_species or "",
                "avg_price": final_average,
                "min_price": min_price,
                "detailed_availability": table_availability,
                "total_availability": total_availability,
                "max_price": max_price
            }

            logging.info(f"Product data: {product_data}")
            return product_data
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"An error occurred during scraping: {e}")


def get_product_title(driver, selector):
    h1_element = wait_for_element(driver, selector)
    if h1_element:
        clean_title_text = h1_element.get_attribute("innerHTML").split("<span")[0].strip()
        return clean_title_text
    return ""


def get_product_subtitle(driver, selector):
    h1_element = wait_for_element(driver, selector)
    if h1_element:
        soup = BeautifulSoup(h1_element.get_attribute("innerHTML"), 'html.parser')
        subtitle_text = soup.find('span').get_text().strip()
        return subtitle_text
    return ""


def get_text_from_element(driver, selector):
    element = wait_for_element(driver, selector)
    return element.text if element else ""


def get_product_image(driver, selector):
    h1_element = wait_for_element(driver, selector)
    if h1_element:
        image_url = h1_element.get_attribute("src")
        headers = {
            'User-Agent': get_random_user_agent(),
            'Referer': 'https://www.cardmarket.com/it/Pokemon'
        }
        response = requests.get(image_url, headers=headers, allow_redirects=True)

        if response.status_code == 200:
            try:
                image_data = response.content
                image = Image.open(BytesIO(image_data))
                byte_io = BytesIO()
                image.save(byte_io, format='PNG')  # You can change the format to suit your need (e.g., 'JPEG', 'PNG')

                return byte_io.getvalue()
            except Exception as e:
                logging.error(f"Error processing image from {image_url}: {e}")
                return ""
    logging.warning("Image element not found")
    return ""


def get_total_availability(driver, selector):
    element = wait_for_element(driver, selector)
    return element.text if element else ""


def get_price_data(driver, selector):
    price_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    )
    final_average, minimum_price, max_price = calculate_final_prices(price_elements)
    return final_average, minimum_price, max_price


def get_table_availability(driver, selector):
    availability_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    )
    return sum_table_availabilities(availability_elements)
