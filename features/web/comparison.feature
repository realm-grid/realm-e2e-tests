@comparison
Feature: Server Comparison
  As a user
  I want to compare servers
  So that I can make an informed decision

  @smoke
  Scenario: Comparison checkboxes are visible on browse page
    Given I am on the browse page
    Then I should see "Compare"
