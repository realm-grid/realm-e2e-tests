@players
Feature: Player Management
  As a server owner
  I want to manage players
  So that I can control access

  @smoke
  Scenario: Home page shows friend features
    Given I am on the home page
    Then I should see "Built-In Friend System"
