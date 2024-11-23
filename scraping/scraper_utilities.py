from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def calculate_final_prices(price_elements):
    prices = []
    for element in price_elements:
        try:
            price_text = element.text.replace(".", "").replace(",", ".").replace("€", "").strip()
            price = float(price_text)
            prices.append(price)
        except ValueError:
            continue

    if not prices:
        return 0, 0, 0  # No valid prices available

    initial_average = sum(prices) / len(prices) if prices else 0
    filtered_prices = filter_prices(prices, initial_average)

    if not filtered_prices:
        return 0, 0, 0

    final_average_price = sum(filtered_prices) / len(filtered_prices)
    max_price = max(filtered_prices)
    sorted_prices = sorted(filtered_prices)

    if len(sorted_prices) >= 2:
        minimum_price = sum(sorted_prices[:2]) / 2
    else:
        minimum_price = sorted_prices[0]

    return round(final_average_price, 2), round(minimum_price, 2), round(max_price, 2)


def filter_prices(prices, initial_average):
    return [price for price in prices if (1 / 9) * initial_average <= price <= 5 * initial_average]


def try_table_expansion(driver):
    try:
        expand_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#loadMoreButton"))
        )
        if expand_button:
            expand_button.click()
    except Exception:
        print(
            "Pulsante di espansione non è stato trovato. Procedo senza espandere la tabella.")


def sum_table_availabilities(availabilities_from_table):
    final_availability = 0
    for av in availabilities_from_table:
        try:
            final_availability += int(av.text)
        except ValueError:
            continue
    return final_availability
