from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import LogGen

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.logger = LogGen.loggen()

    def open_url(self, url):
        self.logger.info(f"Opening URL: {url}")
        print(f"Opening URL: {url}")
        self.driver.get(url)
        self.logger.info(f"URL opened: {url}")
        print(f"URL opened: {url}")

    def find_element(self, locator):
        self.logger.info(f"Finding element: {locator}")
        print(f"Finding element: {locator}")
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.logger.info(f"Element found: {locator}")
        print(f"Element found: {locator}")
        return element

    def click_element(self, locator):
        self.logger.info(f"Clicking element: {locator}")
        print(f"Clicking element: {locator}")
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        self.logger.info(f"Element clicked: {locator}")
        print(f"Element clicked: {locator}")

    def enter_text(self, locator, text):
        self.logger.info(f"Entering text '{text}' into element: {locator}")
        print(f"Entering text '{text}' into element: {locator}")
        element = self.wait.until(EC.presence_of_element_located(locator))
        element.clear()
        element.send_keys(text)
        self.logger.info(f"Text entered: {text}")
        print(f"Text entered: {text}")

    def wait_for_element(self, locator, timeout=20):
        self.logger.info(f"Waiting for element: {locator} (timeout={timeout}s)")
        print(f"Waiting for element: {locator} (timeout={timeout}s)")
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        self.logger.info(f"Element ready: {locator}")
        print(f"Element ready: {locator}")
        return element
