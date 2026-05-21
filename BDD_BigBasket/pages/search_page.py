import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.search_locators import SearchLocators
from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class SearchPage(BasePage):
    def wait_for_search_box(self, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(SearchLocators.SEARCH_BOX)
        )

    def search_product(self, product_name):
        if "bigbasket.com" not in self.driver.current_url or "checkout" in self.driver.current_url:
            self.driver.get(ConfigReader.get_base_url())
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

        search_box = self.wait_for_search_box(timeout=20)
        search_box.clear()
        search_box.send_keys(product_name)
        time.sleep(1)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)

    def safe_click(self, locator, name="element"):
        last_error = None
        for attempt in range(1, 4):
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(locator)
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element,
                )
                time.sleep(0.5)
                element.click()
                return
            except StaleElementReferenceException as error:
                last_error = error
                time.sleep(1)
            except Exception as error:
                last_error = error
                try:
                    element = self.driver.find_element(*locator)
                    self.driver.execute_script("arguments[0].click();", element)
                    return
                except Exception:
                    time.sleep(1)
        raise Exception(f"Failed to click {name}") from last_error

    def click_add_button(self):
        self.safe_click(SearchLocators.ADD_BUTTON, "Add button")

    def click_basket(self):
        basket = self._first_visible_element(SearchLocators.BASKET_BUTTON, timeout=20)
        self.driver.execute_script("arguments[0].click();", basket)
        time.sleep(3)

    def click_increment(self):
        self.safe_click(SearchLocators.INCREMENT_BUTTON, "Increment button")

    def click_checkout(self):
        button = self._top_visible_element(SearchLocators.CHECKOUT_BUTTON, timeout=20)
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(2)

    def _first_visible_element(self, locator, timeout=20):
        WebDriverWait(self.driver, timeout).until(
            lambda driver: any(element.is_displayed() for element in driver.find_elements(*locator))
        )
        for element in self.driver.find_elements(*locator):
            if element.is_displayed():
                return element
        raise TimeoutException(f"No visible element found for locator: {locator}")

    def _top_visible_element(self, locator, timeout=20):
        WebDriverWait(self.driver, timeout).until(
            lambda driver: any(element.is_displayed() for element in driver.find_elements(*locator))
        )
        visible_elements = [
            element for element in self.driver.find_elements(*locator)
            if element.is_displayed()
        ]
        return min(visible_elements, key=lambda element: element.location.get("y", 999999))

    def find_add_buttons(self):
        time.sleep(3)
        return self.driver.find_elements(*SearchLocators.ALL_ADD_BUTTONS)

    def is_checkout_available(self):
        try:
            self.wait_for_presence(SearchLocators.CHECKOUT_BUTTON, timeout=15)
            return True
        except TimeoutException:
            return False

    def is_basket_opened(self):
        try:
            self.wait_for_presence(SearchLocators.BASKET_CONTENT, timeout=15)
            return True
        except TimeoutException:
            return False

    def is_checkout_enabled(self):
        buttons = self.driver.find_elements(*SearchLocators.CHECKOUT_BUTTON)
        return bool(buttons) and buttons[0].is_enabled()

    def wait_for_checkout_page(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.url_contains("checkout"))
            return "checkout" in self.driver.current_url
        except TimeoutException:
            return False
