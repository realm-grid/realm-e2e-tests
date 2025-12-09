@backups
Feature: Backups
  As a server owner
  I want to manage backups
  So that I can protect my data

  @smoke
  Scenario: Home page mentions data protection
    Given I am on the home page
    Then I should see "DDoS Protection"
