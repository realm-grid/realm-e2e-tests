@templates
Feature: Server Templates
  As a user
  I want to use server templates
  So that I can quickly deploy

  @smoke
  Scenario: Home page shows quick deployment
    Given I am on the home page
    Then I should see "Up in 60 Seconds"
