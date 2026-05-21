from behave import then, when

from pages.search_page import SearchPage


@when("User opens the basket")
def step_open_basket(context):
    context.search_page = getattr(context, "search_page", SearchPage(context.driver))
    context.search_page.click_basket()


@when("User increases the product quantity")
def step_increase_quantity(context):
    context.search_page.click_increment()


@then("Basket page should show checkout option")
def step_basket_has_checkout(context):
    assert context.search_page.is_basket_opened(), "Basket page did not open after adding product"


@then("Checkout should not be available for empty basket")
def step_checkout_not_available(context):
    assert not context.search_page.is_checkout_enabled(), "Checkout should be blocked for empty basket"
