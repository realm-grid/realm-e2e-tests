@authentication
Feature: Authentication Pages
  As a user
  I want to sign in and sign up
  So that I can manage my game servers

  # ==================== VISUAL & THEME ====================

  @login @visual @theme
  Scenario: Login page has dark theme
    Given I am on the login page
    Then the page should have a dark theme

  @login @visual
  Scenario: Login form has proper styling
    Given I am on the login page
    Then the page should display correctly

  # ==================== LOGIN PAGE CONTENT ====================

  @login @smoke
  Scenario: Login page displays main elements
    Given I am on the login page
    Then I should see "Sign in to manage your game servers"
    And I should see OAuth buttons

  @login
  Scenario: Login page has terms info
    Given I am on the login page
    Then I should see "Terms of Service"

  # ==================== OAUTH BUTTONS ====================

  @login @oauth
  Scenario: All OAuth providers are displayed
    Given I am on the login page
    Then I should see "Sign in with Discord"
    And I should see "Sign in with Google"
    And I should see "Sign in with Microsoft"

  @login @oauth
  Scenario: Discord OAuth button is present
    Given I am on the login page
    Then I should see "Sign in with Discord"

  @login @oauth
  Scenario: Google OAuth button is present
    Given I am on the login page
    Then I should see "Sign in with Google"

  @login @oauth
  Scenario: Microsoft OAuth button is present
    Given I am on the login page
    Then I should see "Sign in with Microsoft"

  # ==================== RESPONSIVE DESIGN ====================

  @login @responsive @mobile
  Scenario: Login page is responsive on mobile
    Given I am on the login page
    Given I am viewing on a mobile device
    Then all content should be visible
    And I should not see horizontal scrollbar

  @login @responsive @desktop
  Scenario: Login page displays correctly on desktop
    Given I am on the login page
    Given I am viewing on desktop
    Then all content should be visible

  # ==================== ACCESSIBILITY ====================

  @login @accessibility
  Scenario: Login page has proper landmarks
    Given I am on the login page
    Then the page should have a main landmark

  @login @accessibility
  Scenario: OAuth buttons are accessible
    Given I am on the login page
    Then buttons should have accessible names

  # ==================== INTERACTIONS ====================

  @login @interaction
  Scenario: OAuth buttons have hover effects
    Given I am on the login page
    Then buttons should have hover effects
