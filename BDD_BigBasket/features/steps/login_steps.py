from behave import given, then, when

from features.steps.context_helpers import get_login_page, get_search_page
from utils.config_reader import ConfigReader
from utils.csv_reader import CSVReader
from utils.logger import LogGen


logger = LogGen.loggen()


def login_with_mobile(context, mobile):
    logger.info("Starting login flow with mobile: %s", mobile)
    assert str(mobile).strip(), "Mobile number is missing"
    # Reuse the same login sequence from full login scenarios and background setup.
    step_launch_bigbasket(context)
    step_click_login(context)
    get_login_page(context).enter_mobile_email(mobile)
    step_click_continue(context)
    if not get_login_page(context).wait_for_otp_page():
        # BigBasket sometimes ignores the first Continue click, so retry once before failing.
        print("OTP was not detected after Continue; retrying Continue once")
        step_click_continue(context)
        assert get_login_page(context).wait_for_otp_page(), "OTP page did not load"
    step_complete_otp_manually(context)
    step_login_success(context)
    logger.info("Login flow completed successfully")


@given("User launches BigBasket application")
def step_launch_bigbasket(context):
    logger.info("Step: launch BigBasket application")
    get_login_page(context).open_bigbasket()
    get_search_page(context)


@given("User is logged into BigBasket")
def step_logged_into_bigbasket(context):
    logger.info("Step: ensure user is logged into BigBasket")
    mobile = getattr(context, "mobile", None)
    if not mobile:
        # Prefer CSV mobile test data, then fall back to config.ini.
        rows = CSVReader.read_csv("login_data.csv")
        mobile = rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()
    login_with_mobile(context, mobile)


@when("User clicks on Login menu")
def step_click_login(context):
    logger.info("Step: click Login menu")
    get_login_page(context).click_login()


@when("User enters mobile number from config")
def step_enter_mobile_from_config(context):
    logger.info("Step: enter mobile number from config/csv")
    rows = CSVReader.read_csv("login_data.csv")
    mobile = getattr(context, "mobile", None)
    if not mobile:
        # Keeps the step usable even when login_data.csv is empty.
        mobile = rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()
    assert mobile.strip(), "Mobile number is missing in login_data.csv"
    get_login_page(context).enter_mobile_email(mobile)


@when('User enters mobile number "{mobile}"')
def step_enter_mobile(context, mobile):
    logger.info("Step: enter mobile number: %s", mobile)
    get_login_page(context).enter_mobile_email(mobile)


@when("User clicks Continue button")
def step_click_continue(context):
    logger.info("Step: click Continue button")
    get_login_page(context).click_continue()


@then("User should see OTP verification page")
def step_otp_page_visible(context):
    logger.info("Step: verify OTP page is visible")
    assert get_login_page(context).wait_for_otp_page(), "OTP page did not load"


@when("User completes OTP verification manually")
def step_complete_otp_manually(context):
    logger.info("Step: complete OTP verification manually")
    # OTP is intentionally manual; automation waits until the user enters it in the browser.
    login_page = get_login_page(context)
    login_page.wait_for_verify_and_click()
    login_page.dismiss_location_popup()


@then("User should login successfully")
def step_login_success(context):
    logger.info("Step: verify successful login")
    login_page = get_login_page(context)
    search_page = get_search_page(context)
    try:
        search_page.wait_for_search_box(timeout=20)
    except Exception:
        login_page.open_bigbasket()
        search_page.wait_for_search_box(timeout=20)
