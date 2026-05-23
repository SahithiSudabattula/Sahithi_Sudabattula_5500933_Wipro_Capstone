Feature: BigBasket End To End Checkout

  @regression @checkout
  Scenario: Login search single csv product and navigate to checkout
    Given User is logged into BigBasket
    When User searches and adds one checkout product from csv
    And User opens the basket
    And User clicks Checkout button
    Then User should reach checkout page
