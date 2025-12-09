@admin
Feature: Admin Features
  As an admin
  I want to access admin features
  So that I can manage the platform

  @smoke
  Scenario: Home page is accessible
    Given I am on the home page
    Then I should see "Realm Grid"
