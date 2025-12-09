@console
Feature: Server Console
  As a server owner
  I want to access server console
  So that I can manage my server

  @smoke
  Scenario: Browse page shows server options
    Given I am on the browse page
    Then I should see "Minecraft"
