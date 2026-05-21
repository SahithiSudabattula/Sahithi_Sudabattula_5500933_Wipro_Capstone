Feature: BigBasket Positive Test Cases

  Background:
    Given User is logged into BigBasket

  @smoke @cart
  Scenario: Search all positive products from csv and add them to basket
    When User searches and adds positive products from csv
    And User opens the basket
    Then Basket page should show checkout option
