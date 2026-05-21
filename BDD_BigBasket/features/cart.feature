Feature: BigBasket Cart Functionality

  Background:
    Given User launches BigBasket application

  @smoke @cart
  Scenario Outline: Search product and add it to basket
    When User searches for product "<product_name>"
    And User adds the first product to basket
    And User opens the basket
    Then Basket page should show checkout option

    Examples:
      | product_name |
      | milk         |

  @negative @cart
  Scenario: Empty basket should block checkout
    When User opens the basket
    Then Checkout should not be available for empty basket
