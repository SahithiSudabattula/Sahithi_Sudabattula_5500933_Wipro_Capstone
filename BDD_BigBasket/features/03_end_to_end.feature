Feature: BigBasket End To End Checkout

  @regression @checkout
  Scenario: Login search csv products and navigate to checkout
    Given End to end user is logged into BigBasket
    When End to end user searches and adds checkout products from csv
    And End to end user opens the basket
    And End to end user increases the product quantity
    And End to end user clicks Checkout button
    Then End to end user should reach checkout page
