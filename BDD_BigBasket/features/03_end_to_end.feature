Feature: BigBasket End To End Checkout

  @regression @checkout
  Scenario: Login search csv products and navigate to checkout
    Given User is logged into BigBasket
    When User searches and adds checkout products from csv
    And User opens the basket
    And User clicks Checkout button
    Then User should reach checkout page