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


def get_mobile_from_data(context):
    mobile = getattr(context, "mobile", None)
    if mobile:
        return mobile

    rows = CSVReader.read_csv("login_data.csv")
    return rows[0].get("mobile", ConfigReader.get_mobile()) if rows else ConfigReader.get_mobile()


def verify_login_success(context):
    login_page = get_login_page(context)
    search_page = get_search_page(context)
    try:
        search_page.wait_for_search_box(timeout=20)
    except Exception:
        login_page.open_bigbasket()
        search_page.wait_for_search_box(timeout=20)


def ensure_logged_in(context):
    mobile = get_mobile_from_data(context)
    logger.info("Starting E2E login flow with mobile: %s", mobile)
    assert str(mobile).strip(), "Mobile number is missing"

    get_login_page(context).open_bigbasket()
    get_search_page(context)
    get_login_page(context).click_login()
    get_login_page(context).enter_mobile_email(mobile)
    get_login_page(context).click_continue()

    if not get_login_page(context).wait_for_otp_page():
        print("OTP was not detected after Continue; retrying Continue once")
        get_login_page(context).click_continue()
        assert get_login_page(context).wait_for_otp_page(), "OTP page did not load"

    get_login_page(context).wait_for_verify_and_click()
    get_login_page(context).dismiss_location_popup()
    verify_login_success(context)
    logger.info("E2E login flow completed successfully")


def try_search_and_add_product(context, product_name):
    logger.info("Trying to search and add product: %s", product_name)
    search_page = get_search_page(context)
    search_page.search_product(product_name)
    if not search_page.is_add_button_available(timeout=10):
        logger.warning("No addable product displayed for: %s", product_name)
        print(f"No addable product was displayed for: {product_name}; trying next csv product")
        return False

    search_page.click_add_button()
    logger.info("Product added to basket: %s", product_name)
    return True


@given("End to end user is logged into BigBasket")
def step_e2e_logged_into_bigbasket(context):
    logger.info("E2E step: ensure user is logged into BigBasket")
    ensure_logged_in(context)


@when("End to end user searches and adds checkout products from csv")
def step_e2e_search_and_add_checkout_products_from_csv(context):
    logger.info("E2E step: search and add checkout products from csv")
    # End-to-end checkout products are controlled from test_data/search_data.csv.
    products = CSVReader.values("search_data.csv", "product")
    added_products = []
    for product_name in products:
        if try_search_and_add_product(context, product_name):
            added_products.append(product_name)

    assert added_products, "No checkout products from search_data.csv could be added to basket"
    context.added_checkout_products = added_products
    logger.info("Checkout products added: %s", added_products)


@when("End to end user opens the basket")
def step_e2e_open_basket(context):
    logger.info("E2E step: open basket")
    get_search_page(context).click_basket()


@when("End to end user increases the product quantity")
def step_e2e_increase_quantity(context):
    logger.info("E2E step: increase product quantity")
    clicked_count = get_search_page(context).click_increment()
    assert clicked_count == 1, "Basket item quantity was not incremented"


@when("End to end user clicks Checkout button")
def step_e2e_click_checkout(context):
    logger.info("E2E step: click Checkout button")
    get_search_page(context).click_checkout()


@then("End to end user should reach checkout page")
def step_e2e_checkout_page(context):
    logger.info("E2E step: verify checkout page is reached")
    assert get_search_page(context).wait_for_checkout_page(), "Checkout page was not reached"
