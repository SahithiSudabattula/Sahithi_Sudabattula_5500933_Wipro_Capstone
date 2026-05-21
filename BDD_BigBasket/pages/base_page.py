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
        self.driver.get(url)

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
        element = self.wait_for_clickable(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        element.click()
        return element

    def enter_text(self, locator, text, timeout=20):
        element = self.wait_for_presence(locator, timeout)
        element.clear()
        element.send_keys(text)
        return element

