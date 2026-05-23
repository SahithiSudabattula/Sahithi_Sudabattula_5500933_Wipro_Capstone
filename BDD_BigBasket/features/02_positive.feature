Feature: BigBasket Positive Test Cases

  Background:
    Given User is logged into BigBasket

  @positive @search
  Scenario: Search positive product from csv
    When User searches for positive product from csv
    Then Product results should show add option

  @positive @cart
  Scenario: Add positive product to basket
    When User searches and adds positive products from csv
    Then Basket should contain added positive products

  @positive @cart
  Scenario: Open basket after adding positive product
    When User searches and adds positive products from csv
    And User opens the basket
    Then Basket page should be opened

  @positive @checkout
  Scenario: Checkout option should be visible for basket with product
    When User searches and adds positive products from csv
    And User opens the basket
    Then Basket page should show checkout option
