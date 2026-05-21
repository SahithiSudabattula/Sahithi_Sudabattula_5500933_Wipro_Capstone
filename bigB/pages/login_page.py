from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from pages.base_page import BasePage


class LoginPage(BasePage):
    LOGIN_BUTTON = (By.XPATH, "//button[contains(., 'Login')]")
    MOBILE_INPUT     = (By.ID, "multiform")
    CONTINUE_BUTTON  = (By.XPATH, "//button[contains(text(),'Continue')]")
    OTP_HEADING      = (By.XPATH, "//*[contains(text(),'Enter OTP')]")
    VERIFY_BUTTON    = (By.XPATH, "//button[contains(text(),'Verify & Continue') or contains(text(),'Verify and Continue') or contains(text(),'Verify')]")
    GOT_IT_BUTTON    = (By.XPATH, "//button[contains(text(),'Got it') or contains(text(),'GOT IT') or contains(text(),'Got It')]")

    def __init__(self, driver):
        super().__init__(driver)

    def open_bigbasket(self):
        self.logger.info("Navigating to bigB")
        print("Navigating to bigB...")
        self.open_url("https://www.bigbasket.com/")
        WebDriverWait(self.driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self.logger.info("bigB homepage fully loaded")
        print("bigB homepage fully loaded")

    def click_login(self):
        try:
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(self.LOGIN_BUTTON)
            )
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.LOGIN_BUTTON)
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
        except TimeoutException:
            element = self.driver.find_element(*self.LOGIN_BUTTON)
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            raise Exception(f"Login button failed: {e}")

    def enter_mobile_email(self, value):
        self.logger.info(f"Entering mobile/email: {value}")
        print(f"Entering mobile/email: {value}")
        element = self.wait.until(EC.presence_of_element_located(self.MOBILE_INPUT))
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
            element = self.wait.until(EC.visibility_of_element_located(self.CONTINUE_BUTTON))
            self.driver.execute_script("arguments[0].click();", element)  # JS click fallback
            self.logger.info("Continue clicked")
            print("Continue clicked")
        except Exception as e:
            self.logger.error(f"Continue button failed: {e}")
            print(f"Continue button failed: {e}")
            raise

    def wait_for_otp_page(self):
        self.logger.info("Waiting up to 30s for OTP page heading")
        print("Waiting for OTP page...")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located(self.OTP_HEADING)
            )
            self.logger.info("OTP page detected — enter OTP manually in browser")
            print("OTP page detected — enter OTP manually in browser")
            return True
        except Exception:
            try:
                visible_text = self.driver.find_element(By.TAG_NAME, "body").text[:800]
                self.logger.warning(f"OTP heading NOT found. Page text:\n{visible_text}")
                print("OTP heading not found — continuing anyway")
            except Exception as e:
                self.logger.warning(f"Could not read page body: {e}")
                print(f"Could not read page body: {e}")
            return False

    def wait_for_verify_and_click(self):
        self.logger.info("Waiting up to 120s for Verify & Continue button")
        print("Waiting for Verify & Continue button...")
        try:
            verify_wait = WebDriverWait(self.driver, 120)
            element = verify_wait.until(EC.element_to_be_clickable(self.VERIFY_BUTTON))
            self.logger.info("Verify & Continue clickable — clicking")
            print("Verify & Continue clickable — clicking...")
            element.click()
            self.logger.info("Verify & Continue clicked")
            print("Verify & Continue clicked")
        except Exception as e:
            try:
                visible_text = self.driver.find_element(By.TAG_NAME, "body").text[:800]
                self.logger.error(f"Verify button not found. Page text:\n{visible_text}")
                print("Verify button not found — check page text")
            except Exception:
                print("Verify button not found — no page text available")
            raise

    def dismiss_location_popup(self):
        self.logger.info("Checking for location popup after login")
        print("Checking for location popup...")
        try:
            got_it = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.GOT_IT_BUTTON)
            )
            got_it.click()
            self.logger.info("Location popup dismissed — clicked 'Got it'")
            print("Location popup dismissed — clicked 'Got it'")
        except Exception:
            self.logger.info("No location popup appeared — continuing")
            print("No location popup appeared — continuing")
