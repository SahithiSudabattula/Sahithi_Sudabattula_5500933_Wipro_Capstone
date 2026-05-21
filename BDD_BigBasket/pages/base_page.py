from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import LogGen


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.logger = LogGen.loggen()

    def open_url(self, url):
        self.logger.info("Opening URL: %s", url)
        print(f"Opening URL: {url}")
        self.driver.get(url)
        self.logger.info("URL opened: %s", url)
        print(f"URL opened: {url}")

    def find_element(self, locator):
        self.logger.info("Finding element: %s", locator)
        print(f"Finding element: {locator}")
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.logger.info("Element found: %s", locator)
        print(f"Element found: {locator}")
        return element

    def wait_for_presence(self, locator, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_visible(self, locator, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_clickable(self, locator, timeout=20):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def click_element(self, locator, timeout=20):
        self.logger.info("Clicking element: %s", locator)
        print(f"Clicking element: {locator}")
        element = self.wait_for_clickable(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        element.click()
        self.logger.info("Element clicked: %s", locator)
        print(f"Element clicked: {locator}")
        return element

    def enter_text(self, locator, text, timeout=20):
        self.logger.info("Entering text '%s' into element: %s", text, locator)
        print(f"Entering text '{text}' into element: {locator}")
        element = self.wait_for_presence(locator, timeout)
        element.clear()
        element.send_keys(text)
        self.logger.info("Text entered: %s", text)
        print(f"Text entered: {text}")
        return element

    def wait_for_element(self, locator, timeout=20):
        self.logger.info("Waiting for element: %s (timeout=%ss)", locator, timeout)
        print(f"Waiting for element: {locator} (timeout={timeout}s)")
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        self.logger.info("Element ready: %s", locator)
        print(f"Element ready: {locator}")
        return element
