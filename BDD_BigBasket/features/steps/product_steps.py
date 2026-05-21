from behave import then, when

from pages.search_page import SearchPage


@when('User searches for product "{product_name}"')
def step_search_product(context, product_name):
    context.search_page = getattr(context, "search_page", SearchPage(context.driver))
    context.search_page.search_product(product_name)


@when("User adds the first product to basket")
def step_add_first_product(context):
    context.search_page.click_add_button()


@then("No add button should be displayed for the invalid search")
def step_no_add_button_for_invalid_search(context):
    add_buttons = context.search_page.find_add_buttons()
    assert len(add_buttons) == 0, f"Expected no Add buttons, but found {len(add_buttons)}"

