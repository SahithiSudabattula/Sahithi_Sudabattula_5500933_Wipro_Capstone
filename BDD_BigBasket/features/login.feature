Feature: BigBasket Login Functionality

  Background:
    Given User launches BigBasket application

  @smoke @login
  Scenario: Valid login with mobile OTP
    When User clicks on Login menu
    And User enters mobile number from config
    And User clicks Continue button
    Then User should see OTP verification page
    When User completes OTP verification manually
    Then User should login successfully

