@notifications
Feature: Notifications
  As a user
  I want to receive notifications
  So that I stay informed

  @smoke
  Scenario: Home page shows real-time features
    Given I am on the home page
    Then I should see "Real-Time Stats"
