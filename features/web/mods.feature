@mods
Feature: Mod Management
  As a server owner
  I want to manage mods
  So that I can customize my server

  @smoke
  Scenario: Home page shows game support
    Given I am on the home page
    Then I should see "Valheim"
