Feature: BigBasket Negative Test Cases

  @negative @search @cart
  Scenario: Invalid search and empty basket checkout should be blocked
    Given User is logged into BigBasket
    When User searches for all invalid products from csv
    And User opens the basket
    Then Checkout should not be available for empty basket
