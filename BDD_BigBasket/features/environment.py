import os
import shutil
import subprocess
import time

import allure
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

from utils.config_reader import ConfigReader
from utils.csv_reader import CSVReader
from utils.logger import LogGen
from utils.screenshot_util import ScreenshotUtil


logger = LogGen.loggen()
ALLURE_RESULTS_DIR = os.path.join("reports", "allure-results")
ALLURE_REPORT_DIR = os.path.join("reports", "allure-report")
REPORT_SHORTCUT = os.path.join("reports", "report.html")


def before_all(context):
    context.csv_data = CSVReader.read_all_csv_files()

    if os.path.exists(ALLURE_RESULTS_DIR):
        shutil.rmtree(ALLURE_RESULTS_DIR)
    if os.path.exists(ALLURE_REPORT_DIR):
        shutil.rmtree(ALLURE_REPORT_DIR)
    if os.path.exists(REPORT_SHORTCUT):
        os.remove(REPORT_SHORTCUT)

    os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    _write_allure_environment()


def _write_allure_environment():
    environment_path = os.path.join(ALLURE_RESULTS_DIR, "environment.properties")
    with open(environment_path, "w", encoding="utf-8") as file:
        file.write("Project=BDD_BigBasket\n")
        file.write("Application=BigBasket\n")
        file.write(f"Browser={ConfigReader.get_browser()}\n")
        file.write(f"BaseURL={ConfigReader.get_base_url()}\n")


def _attach_screenshot_to_allure(path, name):
    try:
        with open(path, "rb") as image:
            allure.attach(
                image.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
    except Exception as error:
        logger.warning("Could not attach screenshot to Allure: %s", error)


def _build_edge_driver(headless=False):
    options = EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)
    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Edge(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def _build_chrome_driver(headless=False):
    options = ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)


def before_scenario(context, scenario):
    logger.info("========================================")
    logger.info("STARTING SCENARIO: %s", scenario.name)
    context.extra_screenshots = []

    browser = ConfigReader.get_browser().lower()
    headless = ConfigReader.get_headless()
    implicit_wait = ConfigReader.get_implicit_wait()

    if browser == "chrome":
        context.driver = _build_chrome_driver(headless=headless)
    else:
        context.driver = _build_edge_driver(headless=headless)

    context.driver.implicitly_wait(implicit_wait)
    context.driver.get(ConfigReader.get_base_url())
    logger.info("Browser opened for scenario: %s", scenario.name)


def after_scenario(context, scenario):
    logger.info("SCENARIO STATUS: %s", scenario.status)
    should_capture = scenario.status == "failed" or "negative" in scenario.effective_tags
    if should_capture and hasattr(context, "driver"):
        for path, name in getattr(context, "extra_screenshots", []):
            logger.info("Attaching saved screenshot: %s", path)
            _attach_screenshot_to_allure(path, name)

        path = ScreenshotUtil.capture_screenshot(context.driver, scenario.name)
        logger.info("Screenshot saved: %s", path)
        _attach_screenshot_to_allure(path, scenario.name)

    if hasattr(context, "driver"):
        time.sleep(5)
        context.driver.quit()
    logger.info("Browser closed")
    logger.info("========================================")


def after_all(context):
    allure_command = shutil.which("allure")
    if not allure_command:
        logger.warning("Allure command line tool is not installed or not in PATH")
        return

    os.makedirs("reports", exist_ok=True)
    result = subprocess.run(
        [
            allure_command,
            "generate",
            ALLURE_RESULTS_DIR,
            "--clean",
            "-o",
            ALLURE_REPORT_DIR,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.warning("Allure HTML report generation failed: %s", result.stderr)
        return

    with open(REPORT_SHORTCUT, "w", encoding="utf-8") as file:
        file.write(
            "<!doctype html><html><head>"
            "<meta http-equiv='refresh' content='0; url=allure-report/index.html'>"
            "<title>Allure Report</title></head><body>"
            "<a href='allure-report/index.html'>Open Allure Report</a>"
            "</body></html>"
        )
    logger.info("Allure HTML report generated: %s", ALLURE_REPORT_DIR)
    logger.info("Report shortcut generated: %s", REPORT_SHORTCUT)
