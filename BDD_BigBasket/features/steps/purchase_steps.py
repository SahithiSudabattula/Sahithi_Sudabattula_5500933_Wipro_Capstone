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
    get_search_page(context).click_checkout()


@then("User should reach checkout page")
def step_checkout_page(context):
    logger.info("Step: verify checkout page is reached")
    assert get_search_page(context).wait_for_checkout_page(), "Checkout page was not reached"
