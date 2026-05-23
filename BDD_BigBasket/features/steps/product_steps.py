from behave import then, when
from features.steps.context_helpers import get_search_page
from utils.csv_reader import CSVReader
from utils.logger import LogGen
from utils.screenshot_util import ScreenshotUtil


logger = LogGen.loggen()


def _search_and_add_product(context, product_name):
    logger.info("Searching and adding product: %s", product_name)
    search_page = get_search_page(context)
    search_page.search_product(product_name)
    assert search_page.is_add_button_available(), f"No addable product was displayed for: {product_name}"
    search_page.click_add_button()


def _try_search_and_add_product(context, product_name):
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


@when('User searches for product "{product_name}"')
def step_search_product(context, product_name):
    logger.info("Step: search product: %s", product_name)
    search_page = get_search_page(context)
    search_page.search_product(product_name)


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
        if _try_search_and_add_product(context, product_name):
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


@when("User searches and adds checkout products from csv")
def step_search_and_add_checkout_products_from_csv(context):
    logger.info("Step: search and add checkout products from csv")
    # End-to-end checkout products are controlled from test_data/search_data.csv.
    products = CSVReader.values("search_data.csv", "product")
    added_products = []
    for product_name in products:
        if _try_search_and_add_product(context, product_name):
            added_products.append(product_name)
    assert added_products, "No checkout products from search_data.csv could be added to basket"
    context.added_checkout_products = added_products
    logger.info("Checkout products added: %s", added_products)


@then("No add button should be displayed for the invalid search")
def step_no_add_button_for_invalid_search(context):
    logger.info("Step: verify no add button is displayed for invalid search")
    add_buttons = get_search_page(context).find_add_buttons()
    assert len(add_buttons) == 0, f"Expected no Add buttons, but found {len(add_buttons)}"
