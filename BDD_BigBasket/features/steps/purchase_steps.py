from behave import then, when

from pages.search_page import SearchPage


@when("User clicks Checkout button")
def step_click_checkout(context):
    context.search_page = getattr(context, "search_page", SearchPage(context.driver))
    context.search_page.click_checkout()


@then("User should reach checkout page")
def step_checkout_page(context):
    assert context.search_page.wait_for_checkout_page(), "Checkout page was not reached"

