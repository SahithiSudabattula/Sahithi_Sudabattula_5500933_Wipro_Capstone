from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from pages.base_page import BasePage
import time


class SearchPage(BasePage):

    SEARCH_BOX      = (By.XPATH, "//input[@type='search' or contains(@placeholder,'Search') or contains(@class,'search')]")
    ADD_BUTTON      = (By.XPATH, "(//button[contains(text(),'Add') or contains(text(),'ADD')])[1]")
    BASKET_BUTTON   = (By.XPATH, "(//a[contains(@href,'basket') or contains(@href,'cart')] | //button[contains(@aria-label,'basket') or contains(@aria-label,'cart')])[1]")
    # CHECKOUT_BUTTON = (By.XPATH, "(//button[contains(text(),'Proceed to Checkout') or contains(text(),'Checkout')])[1]")
    CHECKOUT_BUTTON = (By.XPATH,"//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'checkout')]")
    ADDRESS_DIV     = (By.XPATH, "(//div[contains(@class,'address-item') or contains(@class,'AddressCard')])[1]")

    def __init__(self, driver):
        super().__init__(driver)

    def wait_for_search_box(self, timeout=20):
        print(f"Waiting for search box (timeout={timeout}s)...")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.SEARCH_BOX)
            )
            print("Search box ready")
            return element
        except TimeoutException:
            raise TimeoutException("Search box not found within timeout")

    def search_product(self, product_name):
        print(f"Searching for product: {product_name}")
        if "bigbasket.com" not in self.driver.current_url or "checkout" in self.driver.current_url:
            self.driver.get("https://www.bigbasket.com/")
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        element = self.wait_for_search_box()
        element.clear()
        element.send_keys(product_name)
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//ul[contains(@class,'suggest') or contains(@class,'autocomplete')]")
                )
            )
            print("Autocomplete appeared")
        except Exception:
            print("Autocomplete not detected — submitting directly")
        element.send_keys(Keys.ENTER)
        print(f"Search submitted: {product_name}")

    def safe_click(self, locator, name="element"):
        for attempt in range(1, 4):
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(locator)
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                time.sleep(0.5)
                element.click()
                print(f"{name} clicked")
                return
            except StaleElementReferenceException:
                print(f"{name} stale on attempt {attempt}, retrying...")
                time.sleep(1)
            except Exception as e:
                print(f"{name} normal click failed, using JS click: {e}")
                try:
                    element = self.driver.find_element(*locator)
                    self.driver.execute_script("arguments[0].click();", element)
                    print(f"{name} clicked via JS")
                    return
                except Exception:
                    time.sleep(1)
        raise Exception(f"Failed to click {name} after retries")

    def click_add_button(self):
        print("Clicking Add button...")
        self.safe_click(self.ADD_BUTTON, "Add button")

    def click_basket(self):
        print("Clicking Basket button...")
        self.safe_click(self.BASKET_BUTTON, "Basket button")

    def click_increment(self):
        print("Clicking Increment button...")
        self.safe_click((By.XPATH, "(//button[contains(.,'+')])[1]"), "Increment button")
        print("Quantity incremented successfully")

    def click_checkout(self):
        print("Clicking Checkout button...")
        self.safe_click(self.CHECKOUT_BUTTON, "Checkout button")


    def select_address(self):
        print("Selecting saved delivery address...")
        try:
            address = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(self.ADDRESS_DIV)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", address)
            time.sleep(0.5)
            address.click()
            print("Address selected successfully")
            time.sleep(2)
        except Exception as e:
            print(f"Address selection failed (may not be required): {e}")

    # def click_remove_all(self):
    #     remove_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'Remove')]")
    #     for btn in remove_buttons:
    #         btn.click()
