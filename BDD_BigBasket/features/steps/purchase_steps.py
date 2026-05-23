from behave import then, when

from pages.search_page import SearchPage
from utils.logger import LogGen


logger = LogGen.loggen()


def get_search_page(context):
    search_page = getattr(context, "search_page", None)
    if search_page is None:
        search_page = SearchPage(context.driver)
        context.search_page = search_page
    return search_page


@when("User clicks Checkout button")
def step_click_checkout(context):
    logger.info("Step: click Checkout button")
    search_page = get_search_page(context)
    assert search_page.is_checkout_available(), "Checkout button is not visible before checkout click"
    assert search_page.is_checkout_enabled(), "Checkout button is disabled before checkout click"
    search_page.click_checkout()


@then("User should reach checkout page")
def step_checkout_page(context):
    logger.info("Step: verify checkout page is reached")
    assert get_search_page(context).wait_for_checkout_page(), (
        f"Checkout page was not reached. Current URL: {context.driver.current_url}"
    )
