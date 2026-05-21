import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.login_locators import LoginLocators
from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class LoginPage(BasePage):
    def open_bigbasket(self):
        self.open_url(ConfigReader.get_base_url())
        WebDriverWait(self.driver, 15).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def click_login(self):
        try:
            element = self.wait_for_presence(LoginLocators.LOGIN_BUTTON, timeout=20)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(LoginLocators.LOGIN_BUTTON)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            element.click()
        except TimeoutException:
            element = self.driver.find_element(*LoginLocators.LOGIN_BUTTON)
            self.driver.execute_script("arguments[0].click();", element)

    def enter_mobile_email(self, value):
        element = self.wait_for_presence(LoginLocators.MOBILE_INPUT, timeout=20)
        element.clear()
        for char in str(value):
            element.send_keys(char)
            time.sleep(0.05)

    def click_continue(self):
        element = self.wait_for_visible(LoginLocators.CONTINUE_BUTTON, timeout=20)
        self.driver.execute_script("arguments[0].click();", element)

    def wait_for_otp_page(self):
        try:
            self.wait_for_visible(LoginLocators.OTP_HEADING, timeout=30)
            return True
        except Exception:
            return False

    def wait_for_verify_and_click(self):
        element = WebDriverWait(self.driver, 120).until(
            EC.element_to_be_clickable(LoginLocators.VERIFY_BUTTON)
        )
        element.click()

    def dismiss_location_popup(self):
        try:
            self.click_element(LoginLocators.GOT_IT_BUTTON, timeout=10)
        except Exception:
            self.logger.info("Location popup was not displayed")
