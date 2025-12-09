@files
Feature: File Manager
  As a server owner
  I want to manage files
  So that I can configure my server

  @smoke
  Scenario: Status page shows file manager service
    Given I am on the status page
    Then I should see "File Manager"
