@analytics
Feature: Analytics
  As a user
  I want to view analytics
  So that I can understand usage

  @smoke
  Scenario: Home page shows metrics
    Given I am on the home page
    Then I should see "99.9%"
