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
LOG_FILE = os.path.join("logs", "automation.log")


def before_all(context):
    # Load all CSV data once so missing or empty test data is caught before scenarios run.
    context.csv_data = CSVReader.read_all_csv_files()

    # Start every run with fresh Allure output so old results do not mix with new results.
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


def _attach_text_to_allure(text, name):
    try:
        allure.attach(
            text,
            name=name,
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception as error:
        logger.warning("Could not attach text to Allure: %s", error)


def _flush_log_handlers():
    # Flush handlers before attaching logs so the latest scenario entries are included.
    for handler in logger.handlers:
        try:
            handler.flush()
        except Exception:
            pass


def _read_log_from_position(start_position):
    # Each scenario stores its starting byte position and attaches only its own log lines.
    if not os.path.exists(LOG_FILE):
        return ""

    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as log_file:
            log_file.seek(start_position)
            return log_file.read().strip()
    except Exception as error:
        logger.warning("Could not read scenario log file: %s", error)
        return ""


def _open_allure_report(allure_command):
    try:
        subprocess.Popen(
            [allure_command, "open", ALLURE_REPORT_DIR],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info("Allure report opened automatically")
    except Exception as error:
        logger.warning("Could not open Allure report automatically: %s", error)


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
    # Hide Selenium's webdriver flag to reduce automation detection on BigBasket.
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


def _build_driver():
    browser = ConfigReader.get_browser().lower()
    headless = ConfigReader.get_headless()
    if browser == "chrome":
        return _build_chrome_driver(headless=headless)
    return _build_edge_driver(headless=headless)


def before_feature(context, feature):
    logger.info("========================================")
    logger.info("STARTING FEATURE: %s", feature.name)
    context.driver = _build_driver()
    context.driver.implicitly_wait(ConfigReader.get_implicit_wait())
    context.driver.get(ConfigReader.get_base_url())
    context.config.bigbasket_logged_in = False
    context.login_page = None
    context.search_page = None
    logger.info("Browser opened for feature: %s", feature.name)


def before_scenario(context, scenario):
    # Remember where this scenario's logs begin for per-scenario Allure attachment.
    context.log_start_position = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0
    logger.info("----------------------------------------")
    logger.info("STARTING SCENARIO: %s", scenario.name)
    context.extra_screenshots = []

def after_step(context, step):
    if hasattr(context, "driver"):
        step_name = f"{step.keyword}_{step.name}"
        path = ScreenshotUtil.capture_screenshot(context.driver, step_name)
        _attach_screenshot_to_allure(path, step_name)
        logger.info("Step screenshot saved: %s", path)

def after_scenario(context, scenario):
    logger.info("SCENARIO STATUS: %s", scenario.status)
    if hasattr(context, "driver"):
        # Attach screenshots captured inside steps first, then the final scenario screenshot.
        for path, name in getattr(context, "extra_screenshots", []):
            logger.info("Attaching saved screenshot: %s", path)
            _attach_screenshot_to_allure(path, name)

        path = ScreenshotUtil.capture_screenshot(context.driver, scenario.name)
        logger.info("Screenshot saved: %s", path)
        _attach_screenshot_to_allure(path, scenario.name)

    _flush_log_handlers()
    scenario_log = _read_log_from_position(getattr(context, "log_start_position", 0))
    if scenario_log:
        _attach_text_to_allure(scenario_log, f"{scenario.name} log")

    logger.info("SCENARIO FINISHED: %s", scenario.name)
    logger.info("----------------------------------------")


def after_feature(context, feature):
    if hasattr(context, "driver"):
        time.sleep(5)
        context.driver.quit()
        logger.info("Browser closed for feature: %s", feature.name)
    logger.info("FINISHED FEATURE: %s", feature.name)
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
        # Create a stable report.html entry point even though Allure generates a folder.
        file.write(
            "<!doctype html><html><head>"
            "<meta http-equiv='refresh' content='0; url=allure-report/index.html'>"
            "<title>Allure Report</title></head><body>"
            "<a href='allure-report/index.html'>Open Allure Report</a>"
            "</body></html>"
        )
    logger.info("Allure HTML report generated: %s", ALLURE_REPORT_DIR)
    logger.info("Report shortcut generated: %s", REPORT_SHORTCUT)
    _open_allure_report(allure_command)
