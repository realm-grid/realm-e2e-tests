@smoke
Feature: Smoke Tests
  Basic application smoke tests

  Scenario: Application loads
    Given I navigate to the home page
    Then the page should load successfully
    And I should see the page title

  Scenario: Home page has content
    Given I am on the home page
    Then I should see "Realm Grid"
    And I should see "Browse Servers"
