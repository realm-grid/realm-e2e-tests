@contact
Feature: Contact Page
  As a user
  I want to contact support
  So that I can get help with my issues

  # ==================== VISUAL & THEME ====================

  @visual @theme
  Scenario: Contact page has dark theme
    Given I am on the contact page
    Then the page should have a dark theme
    And the primary color should be purple

  @visual
  Scenario: Contact form has proper styling
    Given I am on the contact page
    Then cards should have a dark background with blur effect

  # ==================== PAGE CONTENT ====================

  @content @smoke
  Scenario: Contact page displays main elements
    Given I am on the contact page
    Then I should see "Contact"
    And I should see contact information

  @content
  Scenario: Contact page has email info
    Given I am on the contact page
    Then I should see email contact information

  @content
  Scenario: Contact page shows support options
    Given I am on the contact page
    Then I should see support contact options

  # ==================== NAVIGATION ====================

  @navigation
  Scenario: Can navigate back to home from contact
    Given I am on the contact page
    When I click the back button
    Then I should see "Game Server Hosting"

  # ==================== PAGE LAYOUT ====================

  @layout
  Scenario: Contact page has back button
    Given I am on the contact page
    Then I should see a back button

  # ==================== RESPONSIVE DESIGN ====================

  @responsive @mobile
  Scenario: Contact page is responsive on mobile
    Given I am on the contact page
    Given I am viewing on a mobile device
    Then all content should be visible
    And I should not see horizontal scrollbar

  @responsive @desktop
  Scenario: Contact page displays correctly on desktop
    Given I am on the contact page
    Given I am viewing on desktop
    Then all content should be visible

  # ==================== ACCESSIBILITY ====================

  @accessibility
  Scenario: Contact page has proper landmarks
    Given I am on the contact page
    Then the page should have a main landmark

  @accessibility
  Scenario: Contact elements are accessible
    Given I am on the contact page
    Then buttons should have accessible names
    And links should be keyboard accessible
