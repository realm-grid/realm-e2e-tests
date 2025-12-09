@dashboard
Feature: User Dashboard
  As a logged in user
  I want to access my dashboard
  So that I can manage my game servers

  @smoke
  Scenario: Dashboard header is present on browse page
    Given I am on the browse page
    Then I should see "Browse Servers"
