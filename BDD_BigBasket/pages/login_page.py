import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.login_locators import LoginLocators
from pages.base_page import BasePage
from utils.config_reader import ConfigReader


class LoginPage(BasePage):
    def open_bigbasket(self):
        self.logger.info("Navigating to bigB")
        print("Navigating to bigB...")
        self.open_url(ConfigReader.get_base_url())
        WebDriverWait(self.driver, 15).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        self.logger.info("bigB homepage fully loaded")
        print("bigB homepage fully loaded")

    def click_login(self):
        self.logger.info("Clicking Login menu")
        try:
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(LoginLocators.LOGIN_BUTTON)
            )
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(LoginLocators.LOGIN_BUTTON)
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
            self.logger.info("Login menu clicked")
        except TimeoutException:
            self.logger.warning("Login menu was not clickable; using JS click fallback")
            element = self.driver.find_element(*LoginLocators.LOGIN_BUTTON)
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info("Login menu clicked via JS")
        except Exception as error:
            self.logger.error("Login button failed: %s", error)
            raise Exception(f"Login button failed: {error}") from error

    def enter_mobile_email(self, value):
        self.logger.info("Entering mobile/email: %s", value)
        print(f"Entering mobile/email: {value}")
        element = self.wait.until(EC.presence_of_element_located(LoginLocators.MOBILE_INPUT))
        element.clear()
        for char in str(value):
            element.send_keys(char)
            time.sleep(0.08)
        self.logger.info("Mobile/email entered successfully")
        print("Mobile/email entered successfully")

    def click_continue(self):
        self.logger.info("Clicking Continue button")
        print("Clicking Continue button...")
        try:
            element = self.wait.until(EC.visibility_of_element_located(LoginLocators.CONTINUE_BUTTON))
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info("Continue clicked")
            print("Continue clicked")
        except Exception as error:
            self.logger.error("Continue button failed: %s", error)
            print(f"Continue button failed: {error}")
            raise

    def wait_for_otp_page(self):
        self.logger.info("Waiting up to 30s for OTP page heading")
        print("Waiting for OTP page...")
        try:
            WebDriverWait(self.driver, 30).until(
                lambda driver: (
                    self._is_visible(LoginLocators.OTP_HEADING)
                    or self._is_present(LoginLocators.VERIFY_BUTTON)
                )
            )
            self.logger.info("OTP page detected - enter OTP manually in browser")
            print("OTP page detected - enter OTP manually in browser")
            return True
        except Exception:
            try:
                visible_text = self.driver.find_element(By.TAG_NAME, "body").text[:800]
                self.logger.warning("OTP heading NOT found. Page text:\n%s", visible_text)
                print("OTP heading not found - continuing anyway")
            except Exception as error:
                self.logger.warning("Could not read page body: %s", error)
                print(f"Could not read page body: {error}")
            return False

    def _is_visible(self, locator):
        try:
            return self.driver.find_element(*locator).is_displayed()
        except Exception:
            return False

    def _is_present(self, locator):
        try:
            return len(self.driver.find_elements(*locator)) > 0
        except Exception:
            return False

    def wait_for_verify_and_click(self):
        self.logger.info("Waiting up to 120s for Verify & Continue button")
        print("Waiting for Verify & Continue button...")
        try:
            verify_wait = WebDriverWait(self.driver, 120)
            element = verify_wait.until(EC.element_to_be_clickable(LoginLocators.VERIFY_BUTTON))
            self.logger.info("Verify & Continue clickable - clicking")
            print("Verify & Continue clickable - clicking...")
            element.click()
            self.logger.info("Verify & Continue clicked")
            print("Verify & Continue clicked")
        except Exception as error:
            try:
                visible_text = self.driver.find_element(By.TAG_NAME, "body").text[:800]
                self.logger.error("Verify button not found. Page text:\n%s", visible_text)
                print("Verify button not found - check page text")
            except Exception:
                print("Verify button not found - no page text available")
            raise error

    def dismiss_location_popup(self):
        self.logger.info("Checking for location popup after login")
        print("Checking for location popup...")
        try:
            got_it = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(LoginLocators.GOT_IT_BUTTON)
            )
            got_it.click()
            self.logger.info("Location popup dismissed - clicked 'Got it'")
            print("Location popup dismissed - clicked 'Got it'")
        except Exception:
            self.logger.info("Location popup was not displayed")
            print("No location popup appeared - continuing")

    def is_login_menu_visible(self):
        try:
            return self.driver.find_element(*LoginLocators.LOGIN_BUTTON).is_displayed()
        except Exception:
            return False
