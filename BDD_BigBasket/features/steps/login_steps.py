from behave import given, then, when

from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.config_reader import ConfigReader
from utils.csv_reader import CSVReader
from utils.logger import LogGen


logger = LogGen.loggen()


def get_login_page(context):
    login_page = getattr(context, "login_page", None)
    if login_page is None:
        login_page = LoginPage(context.driver)
        context.login_page = login_page
    return login_page


def get_search_page(context):
    search_page = getattr(context, "search_page", None)
    if search_page is None:
        search_page = SearchPage(context.driver)
        context.search_page = search_page
    return search_page


def login_with_mobile(context, mobile):
    logger.info("Starting login flow with mobile: %s", mobile)
    assert str(mobile).strip(), "Mobile number is missing"
    step_launch_bigbasket(context)
    step_click_login(context)
    get_login_page(context).enter_mobile_email(mobile)
    step_click_continue(context)
    if not get_login_page(context).wait_for_otp_page():
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
    title = context.driver.title.lower()
    assert "bigbasket" in title or "bigbasket" in context.driver.current_url.lower(), (
        f"BigBasket homepage was not opened. Title: '{context.driver.title}', "
        f"URL: '{context.driver.current_url}'"
    )


@given("User is logged into BigBasket")
def step_logged_into_bigbasket(context):
    logger.info("Step: ensure user is logged into BigBasket")
    if getattr(context.config, "bigbasket_logged_in", False):
        logger.info("Already logged in for this feature; reusing existing session")
        get_login_page(context).open_bigbasket()
        search_box = get_search_page(context).wait_for_search_box(timeout=20)
        assert search_box.is_displayed() and search_box.is_enabled(), "Logged-in session is not ready"
        return

    mobile = getattr(context, "mobile", None)
    if not mobile:
        rows = CSVReader.read_csv("login_data.csv")
        mobile = rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()
    login_with_mobile(context, mobile)
    context.config.bigbasket_logged_in = True


@when("User clicks on Login menu")
def step_click_login(context):
    logger.info("Step: click Login menu")
    assert get_login_page(context).is_login_menu_visible(), "Login menu is not visible on BigBasket homepage"
    get_login_page(context).click_login()


@when("User enters mobile number from config")
def step_enter_mobile_from_config(context):
    logger.info("Step: enter mobile number from config/csv")

    rows = CSVReader.read_csv("login_data.csv")
    mobile = getattr(context, "mobile", None)
    if not mobile:
        mobile = rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()
    assert mobile.strip(), "Mobile number is missing in login_data.csv"
    get_login_page(context).enter_mobile_email(mobile)
    context.mobile = mobile


@when('User enters mobile number "{mobile}"')
def step_enter_mobile(context, mobile):
    logger.info("Step: enter mobile number: %s", mobile)
    assert mobile.strip(), "Mobile number cannot be blank"
    get_login_page(context).enter_mobile_email(mobile)
    context.mobile = mobile


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
    login_page = get_login_page(context)
    login_page.wait_for_verify_and_click()
    login_page.dismiss_location_popup()


@then("User should login successfully")
def step_login_success(context):
    logger.info("Step: verify successful login")
    login_page = get_login_page(context)
    search_page = get_search_page(context)
    try:
        search_box = search_page.wait_for_search_box(timeout=20)
    except Exception:
        login_page.open_bigbasket()
        search_box = search_page.wait_for_search_box(timeout=20)
    assert search_box.is_displayed() and search_box.is_enabled(), "Login failed: search box is not ready"
