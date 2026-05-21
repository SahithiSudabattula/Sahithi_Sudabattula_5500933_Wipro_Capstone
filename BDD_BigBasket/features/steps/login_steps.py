from behave import given, then, when

from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.config_reader import ConfigReader


@given("User launches BigBasket application")
def step_launch_bigbasket(context):
    context.login_page = LoginPage(context.driver)
    context.search_page = SearchPage(context.driver)
    context.login_page.open_bigbasket()


@given("User is logged into BigBasket")
def step_logged_into_bigbasket(context):
    step_launch_bigbasket(context)
    step_click_login(context)
    step_enter_mobile_from_config(context)
    step_click_continue(context)
    if context.login_page.wait_for_otp_page():
        step_complete_otp_manually(context)
    step_login_success(context)


@when("User clicks on Login menu")
def step_click_login(context):
    context.login_page.click_login()


@when("User enters mobile number from config")
def step_enter_mobile_from_config(context):
    context.login_page.enter_mobile_email(ConfigReader.get_mobile())


@when('User enters mobile number "{mobile}"')
def step_enter_mobile(context, mobile):
    context.login_page.enter_mobile_email(mobile)


@when("User clicks Continue button")
def step_click_continue(context):
    context.login_page.click_continue()


@then("User should see OTP verification page")
def step_otp_page_visible(context):
    assert context.login_page.wait_for_otp_page(), "OTP page did not load"


@when("User completes OTP verification manually")
def step_complete_otp_manually(context):
    context.login_page.wait_for_verify_and_click()
    context.login_page.dismiss_location_popup()


@then("User should login successfully")
def step_login_success(context):
    context.search_page.wait_for_search_box(timeout=20)
