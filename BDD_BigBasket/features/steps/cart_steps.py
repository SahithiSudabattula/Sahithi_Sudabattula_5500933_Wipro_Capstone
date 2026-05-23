from behave import then, when
from features.steps.context_helpers import get_search_page
from utils.logger import LogGen


logger = LogGen.loggen()


@when("User opens the basket")
def step_open_basket(context):
    logger.info("Step: open basket")
    get_search_page(context).click_basket()


@when("User increases the product quantity")
def step_increase_quantity(context):
    logger.info("Step: increase product quantity")
    clicked_count = get_search_page(context).click_increment()
    assert clicked_count == 1, "Basket item quantity was not incremented"


@then("Basket page should show checkout option")
def step_basket_has_checkout(context):
    logger.info("Step: verify basket page shows checkout option")
    search_page = get_search_page(context)
    assert search_page.is_checkout_available(), "Basket did not open correctly"


@then("Checkout should not be available for empty basket")
def step_checkout_not_available(context):
    logger.info("Step: verify checkout is unavailable for empty basket")
    assert not get_search_page(context).is_checkout_enabled(), "Checkout should be blocked for empty basket"
