import subprocess
import time
import pytest
import os
import allure
import re
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import TimeoutException
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


def sanitize_screenshot_name(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


@pytest.fixture(scope="function")
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
    time.sleep(5)
    driver.quit()
    logger.info("=== WebDriver session closed ===")


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    login  = LoginPage(driver)
    search = SearchPage(driver)

    logger.info("=== LOGIN START ===")

    with allure.step("Open BigBasket"):
        login.open_bigbasket()
        logger.info("BigBasket opened")

    with allure.step("Click Login"):
        try:
            login.click_login()
            logger.info("Login clicked")
        except Exception as e:
            logger.error(f"Login button failed: {e}")
            raise

    with allure.step("Enter Mobile"):
        try:
            login.enter_mobile_email(MOBILE)
            logger.info("Mobile entered")
        except Exception as e:
            logger.error(f"Mobile entry failed: {e}")
            raise

    with allure.step("Click Continue"):
        try:
            login.click_continue()
            logger.info("Continue clicked")
        except Exception as e:
            logger.error(f"Continue failed: {e}")
            raise

    with allure.step("Wait For OTP Page"):
        otp_ready = login.wait_for_otp_page()
        assert otp_ready, "OTP page did not load — cannot proceed"
        logger.info("OTP page confirmed — enter OTP in browser now")

    with allure.step("Manual OTP Verification"):
        try:
            login.wait_for_verify_and_click()
            logger.info("OTP verified")
        except TimeoutException:
            logger.error("OTP verification timed out")
            raise

    with allure.step("Dismiss Location Popup"):
        login.dismiss_location_popup()
        logger.info("Location popup handled")

    with allure.step("Confirm Login — Wait For Search Box"):
        try:
            search.wait_for_search_box(timeout=20)
            logger.info("Login confirmed — search box visible")
        except Exception as e:
            logger.error(f"Search box not found after login: {e}")
            raise

    logger.info("=== LOGIN SUCCESS ===")
    yield driver


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and (report.passed or report.failed):
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver:
            status = "PASSED" if report.passed else "FAILED"
            test_name = sanitize_screenshot_name(item.name)
            log_message = f"Test {status}: {item.name} - capturing screenshot"
            if report.failed:
                logger.error(log_message)
            else:
                logger.info(log_message)
            take_screenshot(driver, f"{status}_{test_name}")


def pytest_sessionfinish(session, exitstatus):
    subprocess.Popen(
        ["allure", "serve", "reports/allure-results"],
        shell=True
    )
