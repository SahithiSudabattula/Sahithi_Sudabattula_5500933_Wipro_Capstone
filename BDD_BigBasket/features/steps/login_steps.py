from behave import given, then, when

from features.steps.context_helpers import get_login_page, get_search_page
from utils.config_reader import ConfigReader
from utils.csv_reader import CSVReader


def login_with_mobile(context, mobile):
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


@given("User launches BigBasket application")
def step_launch_bigbasket(context):
    get_login_page(context).open_bigbasket()
    get_search_page(context)


@given("User is logged into BigBasket")
def step_logged_into_bigbasket(context):
    mobile = getattr(context, "mobile", None)
    if not mobile:
        rows = CSVReader.read_csv("login_data.csv")
        mobile = rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()
    login_with_mobile(context, mobile)


@when("User clicks on Login menu")
def step_click_login(context):
    get_login_page(context).click_login()


@when("User enters mobile number from config")
def step_enter_mobile_from_config(context):
    rows = CSVReader.read_csv("login_data.csv")
    mobile = getattr(context, "mobile", None)
    if not mobile:
        mobile = rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()
    assert mobile.strip(), "Mobile number is missing in login_data.csv"
    get_login_page(context).enter_mobile_email(mobile)


@when('User enters mobile number "{mobile}"')
def step_enter_mobile(context, mobile):
    get_login_page(context).enter_mobile_email(mobile)


@when("User clicks Continue button")
def step_click_continue(context):
    get_login_page(context).click_continue()


@then("User should see OTP verification page")
def step_otp_page_visible(context):
    assert get_login_page(context).wait_for_otp_page(), "OTP page did not load"


@when("User completes OTP verification manually")
def step_complete_otp_manually(context):
    login_page = get_login_page(context)
    login_page.wait_for_verify_and_click()
    login_page.dismiss_location_popup()


@then("User should login successfully")
def step_login_success(context):
    login_page = get_login_page(context)
    search_page = get_search_page(context)
    try:
        search_page.wait_for_search_box(timeout=20)
    except Exception:
        login_page.open_bigbasket()
        search_page.wait_for_search_box(timeout=20)
