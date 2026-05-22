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


@pytest.mark.usefixtures("logged_in_driver")
class TestPositiveBigBasket:

    @allure.feature("BigBasket E2E")
    @allure.story("Search Product")
    @pytest.mark.parametrize("row", rows, ids=[r["product"] for r in rows])
    def test_search_product(self, logged_in_driver, row):
        product = row["product"]
        search = SearchPage(logged_in_driver)

        logger.info(f"=== SEARCH TEST START | {product} ===")
        search.search_product(product)
        add_button = search.wait.until(EC.visibility_of_element_located(search.ADD_BUTTON))
        assert add_button.is_displayed(), f"Search results not loaded for product: {product}"
        logger.info(f"Searched: {product}")

    @allure.feature("BigBasket E2E")
    @allure.story("Add Product to Basket")
    @pytest.mark.parametrize("row", rows, ids=[r["product"] for r in rows])
    def test_add_to_basket(self, logged_in_driver, row):
        product = row["product"]
        search = SearchPage(logged_in_driver)

        logger.info(f"=== ADD TEST START | {product} ===")
        search.wait.until(EC.presence_of_element_located(search.ADD_BUTTON))
        search.click_add_button()
        basket_button = search.wait.until(EC.element_to_be_clickable(search.BASKET_BUTTON))
        assert basket_button.is_enabled(), "Product not added to basket"
        logger.info("Product added")

    @allure.feature("BigBasket E2E")
    @allure.story("Open Basket")
    @pytest.mark.parametrize("row", rows, ids=[r["product"] for r in rows])
    def test_open_basket(self, logged_in_driver, row):
        product = row["product"]
        search = SearchPage(logged_in_driver)

        logger.info(f"=== OPEN BASKET TEST START | {product} ===")
        search.wait.until(EC.presence_of_element_located(search.BASKET_BUTTON))
        search.click_basket()
        time.sleep(3)
        checkout_button = search.wait.until(EC.visibility_of_element_located(search.CHECKOUT_BUTTON))
        assert checkout_button.is_displayed(), "Basket did not open correctly"
        logger.info(f"Basket opened for {product}")

    @allure.feature("BigBasket E2E")
    @allure.story("Checkout Button Visible")
    @pytest.mark.parametrize("row", rows, ids=[r["product"] for r in rows])
    def test_checkout_button_visible(self, logged_in_driver, row):
        product = row["product"]
        search = SearchPage(logged_in_driver)

        logger.info(f"=== CHECKOUT TEST START | {product} ===")
        checkout_button = search.wait.until(EC.visibility_of_element_located(search.CHECKOUT_BUTTON))
        assert checkout_button.is_displayed(), "Checkout button not visible"
        logger.info(f"=== POSITIVE TEST PASSED | {product} added to basket ===")
