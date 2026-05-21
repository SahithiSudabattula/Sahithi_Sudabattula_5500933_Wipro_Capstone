import time
import pytest
import os
import allure
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from utils.logger import LogGen
from pages.login_page import LoginPage
from pages.search_page import SearchPage

logger = LogGen.loggen()
MOBILE = "9030652433"

def take_screenshot(driver, name):
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    path = os.path.join(screenshots_dir, f"{name}.png")
    driver.save_screenshot(path)
    logger.info(f"Screenshot saved: {path}")
    with open(path, "rb") as f:
        allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)

# ─── Fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def driver():
    logger.info("=== Setting up Edge WebDriver ===")
    options = EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)

    driver = webdriver.Edge(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    logger.info("Edge WebDriver initialized with anti-detection flags")
    driver.get("https://www.bigbasket.com/")
    logger.info("bigB homepage opened")
    yield driver
    logger.info("Quitting WebDriver")
    time.sleep(10)
    driver.quit()
    logger.info("=== WebDriver session closed ===")

@pytest.fixture(scope="session")
def logged_in_driver(driver):
    login  = LoginPage(driver)
    search = SearchPage(driver)

    logger.info("=== LOGIN START ===")
    login.open_bigbasket()
    login.click_login()
    login.enter_mobile_email(MOBILE)
    login.click_continue()
    otp_ready = login.wait_for_otp_page()
    assert otp_ready, "OTP page did not load — cannot proceed"
    login.wait_for_verify_and_click()
    login.dismiss_location_popup()
    search.wait_for_search_box(timeout=20)
    logger.info("=== LOGIN SUCCESS ===")
    yield driver



# ─── Negative Test 1: Invalid Search ─────────────────────────────────────────
@allure.story("Negative — Invalid Product Search")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("product", ["rftDfhwthdfvadwAEFDC"])
def test_negative_invalid_search(logged_in_driver, product):
    driver = logged_in_driver
    search = SearchPage(driver)

    logger.info(f"=== NEGATIVE TEST (invalid search) START | {product} ===")
    print(f"=== NEGATIVE TEST START | {product} ===")

    search.search_product(product)
    logger.info(f"Searched: {product}")
    print(f"Searched: {product}")

    time.sleep(3)
    take_screenshot(driver, f"NEGATIVE_invalid_search_{product}")

    # Validation: no Add buttons should be present
    add_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Add')]")
    assert len(add_buttons) == 0, f"Expected no results but found {len(add_buttons)} Add buttons"

# ─── Negative Test 2: Empty Basket Checkout ──────────────────────────────────
@allure.story("Negative — Empty Basket Checkout")
@allure.severity(allure.severity_level.CRITICAL)
def test_negative_empty_basket_checkout(logged_in_driver):
    driver = logged_in_driver
    search = SearchPage(driver)

    logger.info("=== NEGATIVE TEST (empty basket) START ===")
    print("=== NEGATIVE TEST (empty basket) START ===")

    search.click_basket()
    time.sleep(3)
    take_screenshot(driver, "NEGATIVE_empty_basket")

    # Validation: checkout button should not be enabled
    checkout_btns = driver.find_elements(By.XPATH, "//button[contains(text(),'Checkout')]")
    assert len(checkout_btns) == 0 or not checkout_btns[0].is_enabled(), \
        "Expected checkout to be blocked on empty basket"

    logger.info("=== NEGATIVE TEST PASSED | Empty basket checkout blocked ===")
    print("=== NEGATIVE TEST PASSED | Empty basket checkout blocked ===")


