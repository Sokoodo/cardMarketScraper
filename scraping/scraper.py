from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def fetch_product_data(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        h1_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "body > main > div.page-title-container.d-flex.align-items-center.text-break > div.flex-grow-1 > h1"))
        )
        clean_title_text = h1_element.get_attribute("innerHTML").split("<span")[0].strip()

        price_elements = WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".article-table .table-body .article-row .col-offer .price-container"))
        )

        final_average, minimum_price = calculate_final_prices(price_elements)

        product_data = {
            "product_title": clean_title_text,
            "average_price": final_average,
            "minimum_price": minimum_price
        }

        print("Product title:", product_data["product_title"])
        print("Average price:", product_data["average_price"])
        print("Minimum price:", product_data["minimum_price"])

    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()


def calculate_final_prices(price_elements):
    prices = []
    for element in price_elements:
        try:
            price_text = element.text.replace("€", "").replace(",", ".").strip()
            price = float(price_text)
            prices.append(price)
        except ValueError:
            continue

    initial_average = sum(prices) / len(prices) if prices else 0
    filtered_prices = filter_prices(prices, initial_average)
    final_average_price = sum(filtered_prices) / len(filtered_prices) if filtered_prices else 0

    if len(filtered_prices) >= 2:
        min_prices = sorted(filtered_prices)[:2]  # Prendi i due prezzi minimi
        minimum_price = sum(min_prices) / 2
    else:
        minimum_price = filtered_prices[0] if filtered_prices else 0

    return final_average_price, minimum_price


def filter_prices(prices, initial_average):
    return [price for price in prices if (1 / 7) * initial_average <= price <= 5 * initial_average]
