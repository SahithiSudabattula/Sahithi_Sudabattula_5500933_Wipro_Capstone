from behave import given, then, when

from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.config_reader import ConfigReader
from utils.csv_reader import CSVReader
from utils.logger import LogGen
from utils.screenshot_util import ScreenshotUtil


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

    get_login_page(context).open_bigbasket()
    get_search_page(context)
    get_login_page(context).click_login()
    get_login_page(context).enter_mobile_email(mobile)
    get_login_page(context).click_continue()

    if not get_login_page(context).wait_for_otp_page():
        # BigBasket sometimes ignores the first Continue click, so retry once before failing.
        print("OTP was not detected after Continue; retrying Continue once")
        get_login_page(context).click_continue()
        assert get_login_page(context).wait_for_otp_page(), "OTP page did not load"

    # OTP is intentionally manual; automation waits until the user enters it in the browser.
    get_login_page(context).wait_for_verify_and_click()
    get_login_page(context).dismiss_location_popup()
    verify_login_success(context)
    logger.info("Login flow completed successfully")


def get_mobile_from_data(context):
    mobile = getattr(context, "mobile", None)
    if mobile:
        return mobile

    # Prefer CSV mobile test data, then fall back to config.ini.
    rows = CSVReader.read_csv("login_data.csv")
    return rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()


def ensure_logged_in(context):
    login_with_mobile(context, get_mobile_from_data(context))


def verify_login_success(context):
    login_page = get_login_page(context)
    search_page = get_search_page(context)
    try:
        search_page.wait_for_search_box(timeout=20)
    except Exception:
        login_page.open_bigbasket()
        search_page.wait_for_search_box(timeout=20)


def try_search_and_add_product(context, product_name):
    logger.info("Trying to search and add product: %s", product_name)
    search_page = get_search_page(context)
    search_page.search_product(product_name)
    if not search_page.is_add_button_available(timeout=10):
        # CSV rows can contain unavailable products; skip them and continue with the next row.
        logger.warning("No addable product displayed for: %s", product_name)
        print(f"No addable product was displayed for: {product_name}; trying next csv product")
        return False

    search_page.click_add_button()
    logger.info("Product added to basket: %s", product_name)
    return True


@given("User launches BigBasket application")
def step_launch_bigbasket(context):
    logger.info("Step: launch BigBasket application")
    get_login_page(context).open_bigbasket()
    get_search_page(context)


@given("User is logged into BigBasket")
def step_logged_into_bigbasket(context):
    logger.info("Step: ensure user is logged into BigBasket")
    ensure_logged_in(context)


@when("User clicks on Login menu")
def step_click_login(context):
    logger.info("Step: click Login menu")
    get_login_page(context).click_login()


@when("User enters mobile number from config")
def step_enter_mobile_from_config(context):
    logger.info("Step: enter mobile number from config/csv")
    mobile = get_mobile_from_data(context)
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
    get_login_page(context).wait_for_verify_and_click()
    get_login_page(context).dismiss_location_popup()


@then("User should login successfully")
def step_login_success(context):
    logger.info("Step: verify successful login")
    verify_login_success(context)


@when('User searches for product "{product_name}"')
def step_search_product(context, product_name):
    logger.info("Step: search product: %s", product_name)
    get_search_page(context).search_product(product_name)


@when("User searches for positive product from csv")
def step_search_positive_product_from_csv(context):
    logger.info("Step: search first positive product from csv")
    products = CSVReader.values("positive_data.csv", "product")
    product_name = products[0]
    context.current_product = product_name
    get_search_page(context).search_product(product_name)


@when("User searches and adds positive products from csv")
def step_search_and_add_positive_products_from_csv(context):
    logger.info("Step: search and add positive products from csv")
    # Parameterized positive products come from test_data/positive_data.csv.
    products = CSVReader.values("positive_data.csv", "product")
    added_products = []
    for product_name in products:
        context.current_product = product_name
        if try_search_and_add_product(context, product_name):
            added_products.append(product_name)

    assert added_products, "No positive products from positive_data.csv could be added to basket"
    context.added_positive_products = added_products
    logger.info("Positive products added: %s", added_products)


@when("User searches for invalid product from csv")
def step_search_invalid_product_from_csv(context):
    logger.info("Step: search invalid product from csv")
    rows = CSVReader.read_csv("negative_data.csv")
    invalid_rows = [
        row for row in rows
        if row.get("test_type") == "invalid_search" and row.get("product", "").strip()
    ]
    assert invalid_rows, "negative_data.csv must contain invalid_search product"
    get_search_page(context).search_product(invalid_rows[0]["product"])


@when("User searches for all invalid products from csv")
def step_search_all_invalid_products_from_csv(context):
    logger.info("Step: search all invalid products from csv")
    rows = CSVReader.read_required_csv("negative_data.csv")
    # Only rows marked invalid_search are used for the invalid product search scenario.
    invalid_products = [
        row.get("product", "").strip()
        for row in rows
        if row.get("test_type") == "invalid_search" and row.get("product", "").strip()
    ]
    assert invalid_products, "negative_data.csv must contain invalid_search product"

    search_page = get_search_page(context)
    for product_name in invalid_products:
        logger.info("Validating invalid search product: %s", product_name)
        search_page.search_product(product_name)
        add_buttons = search_page.find_add_buttons()
        assert len(add_buttons) == 0, (
            f"Expected no Add buttons for invalid product '{product_name}', "
            f"but found {len(add_buttons)}"
        )
        screenshot_name = f"NEGATIVE_invalid_search_{product_name}"
        path = ScreenshotUtil.capture_screenshot(context.driver, screenshot_name)
        # Store extra screenshots so environment.py can attach them after the scenario.
        extra_screenshots = getattr(context, "extra_screenshots", [])
        extra_screenshots.append((path, screenshot_name))
        context.extra_screenshots = extra_screenshots
        logger.info("Invalid search screenshot saved: %s", path)
        print(f"Invalid search screenshot saved: {path}")


@when("User adds the first product to basket")
def step_add_first_product(context):
    logger.info("Step: add first product to basket")
    search_page = get_search_page(context)
    assert search_page.is_add_button_available(), "No addable product was displayed"
    search_page.click_add_button()


@when("User searches and adds these products to basket")
def step_search_and_add_multiple_products(context):
    logger.info("Step: search and add products from feature table")
    search_page = get_search_page(context)
    # Supports Gherkin tables with a product_name column.
    for row in context.table:
        product_name = row["product_name"]
        logger.info("Searching table product: %s", product_name)
        search_page.search_product(product_name)
        assert search_page.is_add_button_available(), f"No addable product was displayed for: {product_name}"
        search_page.click_add_button()


@then("No add button should be displayed for the invalid search")
def step_no_add_button_for_invalid_search(context):
    logger.info("Step: verify no add button is displayed for invalid search")
    add_buttons = get_search_page(context).find_add_buttons()
    assert len(add_buttons) == 0, f"Expected no Add buttons, but found {len(add_buttons)}"


@when("User opens the basket")
def step_open_basket(context):
    logger.info("Step: open basket")
    get_search_page(context).click_basket()


@then("Basket page should show checkout option")
def step_basket_has_checkout(context):
    logger.info("Step: verify basket page shows checkout option")
    assert get_search_page(context).is_checkout_available(), "Basket did not open correctly"


@then("Checkout should not be available for empty basket")
def step_checkout_not_available(context):
    logger.info("Step: verify checkout is unavailable for empty basket")
    assert not get_search_page(context).is_checkout_enabled(), "Checkout should be blocked for empty basket"
