@status
Feature: System Status Page
  As a user
  I want to check the system status
  So that I can see if services are operational

  # ==================== VISUAL & THEME ====================

  @visual @theme
  Scenario: Status page has dark theme
    Given I am on the status page
    Then the page should have a dark theme
    And the primary color should be purple

  @visual
  Scenario: Status indicators have proper colors
    Given I am on the status page
    Then status indicators should be visible

  # ==================== PAGE CONTENT ====================

  @content @smoke
  Scenario: Status page displays main elements
    Given I am on the status page
    Then I should see "System Status"
    And I should see service status information

  @content
  Scenario: Status page shows operational message
    Given I am on the status page
    Then I should see status indication

  @content
  Scenario: Status page lists services
    Given I am on the status page
    Then I should see service components

  # ==================== NAVIGATION ====================

  @navigation
  Scenario: Can navigate back to home from status
    Given I am on the status page
    When I click the back button
    Then I should see "Game Server Hosting"

  # ==================== PAGE LAYOUT ====================

  @layout
  Scenario: Status page has back button
    Given I am on the status page
    Then I should see a back button

  # ==================== RESPONSIVE DESIGN ====================

  @responsive @mobile
  Scenario: Status page is responsive on mobile
    Given I am on the status page
    Given I am viewing on a mobile device
    Then all content should be visible
    And I should not see horizontal scrollbar

  @responsive @desktop
  Scenario: Status page displays correctly on desktop
    Given I am on the status page
    Given I am viewing on desktop
    Then all content should be visible

  # ==================== ACCESSIBILITY ====================

  @accessibility
  Scenario: Status page has proper landmarks
    Given I am on the status page
    Then the page should have a main landmark

  @accessibility
  Scenario: Status indicators are accessible
    Given I am on the status page
    Then buttons should have accessible names

  # ==================== REAL-TIME UPDATES ====================

  @realtime
  Scenario: Status page shows last updated time
    Given I am on the status page
    Then I should see update time or status timestamp
