@checkout
Feature: Checkout
  As a user
  I want to checkout
  So that I can purchase game servers

  @smoke
  Scenario: Browse page shows pricing
    Given I am on the browse page
    Then I should see "/month"
