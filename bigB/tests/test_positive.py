import time
import pytest
import allure
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.search_page import SearchPage
from utils.csv_reader import CSVReader
from utils.logger import LogGen

logger = LogGen.loggen()

rows = CSVReader.read_csv("positive_data.csv")


@allure.feature("BigBasket E2E")
@allure.story("Positive: Search and Add to Basket")
@pytest.mark.parametrize("row", rows, ids=[r["product"] for r in rows])
def test_positive_search_and_basket(logged_in_driver, row):
    product = row["product"]
    driver = logged_in_driver
    search = SearchPage(driver)

    logger.info(f"=== POSITIVE TEST START | {product} ===")
    print(f"=== POSITIVE TEST START | {product} ===")

    # Search for product
    try:
        search.search_product(product)
        logger.info(f"Searched: {product}")
        print(f"Searched: {product}")
        # validation: Add button should be visible when search results load
        add_button = search.wait.until(EC.visibility_of_element_located(search.ADD_BUTTON))
        assert add_button.is_displayed(), f"Search results not loaded for product: {product}"
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise

    # Click Add button
    try:
        search.wait.until(EC.presence_of_element_located(search.ADD_BUTTON))
        search.click_add_button()
        logger.info("Product added")
        print("Product added")
        # validation: basket button should be clickable after adding
        basket_button = search.wait.until(EC.element_to_be_clickable(search.BASKET_BUTTON))
        assert basket_button.is_enabled(), "Product not added to basket"
    except TimeoutException:
        logger.error("Add button not found")
        raise

    # Open Basket
    try:
        search.wait.until(EC.presence_of_element_located(search.BASKET_BUTTON))
        search.click_basket()
        time.sleep(3)
        logger.info(f"=== POSITIVE TEST PASSED | {product} added to basket ===")
        print(f"=== POSITIVE TEST PASSED | {product} added to basket ===")
        checkout_button = search.wait.until(EC.visibility_of_element_located(search.CHECKOUT_BUTTON))
        assert checkout_button.is_displayed(), "Basket did not open correctly"
    except TimeoutException:
        logger.error("Basket button not found")
        raise
