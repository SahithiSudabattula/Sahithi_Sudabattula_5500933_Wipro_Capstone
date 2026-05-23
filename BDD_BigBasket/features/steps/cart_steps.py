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


@when("User opens the basket")
def step_open_basket(context):
    logger.info("Step: open basket")
    search_page = get_search_page(context)
    search_page.click_basket()
    assert search_page.is_basket_opened(), f"Basket page did not open. Current URL: {context.driver.current_url}"


@then("Basket page should be opened")
def step_basket_page_opened(context):
    logger.info("Step: verify basket page is opened")
    assert get_search_page(context).is_basket_opened(), f"Basket page was not opened. Current URL: {context.driver.current_url}"


@then("Basket page should show checkout option")
def step_basket_has_checkout(context):
    logger.info("Step: verify basket page shows checkout option")
    search_page = get_search_page(context)
    assert search_page.is_checkout_available(), "Checkout button is not visible on basket page"
    assert search_page.is_checkout_enabled(), "Checkout button is visible but disabled after adding product"


@then("Checkout should not be available for empty basket")
def step_checkout_not_available(context):
    logger.info("Step: verify checkout is unavailable for empty basket")
    assert not get_search_page(context).is_checkout_enabled(), "Checkout should be blocked for empty basket"
