@server-detail
Feature: Server Details
  As a user
  I want to view server details
  So that I can learn about server specifications

  @smoke
  Scenario: Server information is accessible from browse page
    Given I am on the browse page
    Then I should see "Configure"
