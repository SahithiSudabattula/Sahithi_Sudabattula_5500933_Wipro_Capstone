from behave import then, when

from features.steps.context_helpers import get_search_page


@when("User clicks Checkout button")
def step_click_checkout(context):
    get_search_page(context).click_checkout()


@then("User should reach checkout page")
def step_checkout_page(context):
    assert get_search_page(context).wait_for_checkout_page(), "Checkout page was not reached"
