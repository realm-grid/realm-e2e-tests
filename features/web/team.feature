@team
Feature: Team Management
  As a server owner
  I want to manage my team
  So that I can collaborate

  @smoke
  Scenario: Home page is accessible for teams
    Given I am on the home page
    Then I should see "Get Started"
