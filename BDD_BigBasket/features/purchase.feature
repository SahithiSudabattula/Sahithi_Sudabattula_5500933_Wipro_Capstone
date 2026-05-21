Feature: BigBasket Checkout Functionality

  @regression @checkout
  Scenario Outline: Search product and navigate to checkout
    Given User is logged into BigBasket
    When User searches for product "<product_name>"
    And User adds the first product to basket
    And User opens the basket
    And User increases the product quantity
    And User clicks Checkout button
    Then User should reach checkout page

    Examples:
      | product_name |
      | rice         |

  @negative @search
  Scenario: Invalid product search should show no addable products
    Given User launches BigBasket application
    When User searches for product "rftDfhwthdfvadwAEFDC"
    Then No add button should be displayed for the invalid search
