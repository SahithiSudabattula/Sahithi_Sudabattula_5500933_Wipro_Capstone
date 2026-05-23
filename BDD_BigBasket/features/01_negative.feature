Feature: BigBasket Negative Test Cases

  Background:
    Given User is logged into BigBasket

  @negative @search
  Scenario: Invalid product search should not show add button
    When User searches for all invalid products from csv
    Then No add button should be displayed for the invalid search

  @negative @cart
  Scenario: Empty basket checkout should be blocked
    When User opens the basket
    Then Checkout should not be available for empty basket
