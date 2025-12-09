@user-journey @e2e
Feature: User Journeys
  As a user
  I want to complete common user flows
  So that I can achieve my goals on the platform

  # ==================== VISITOR JOURNEYS ====================

  @visitor @smoke
  Scenario: New visitor explores the platform
    Given I am on the home page
    Then I should see "Realm Grid"
    And I should see "Game Server Hosting"
    When I click the "Browse Servers" button
    Then I should see "Browse Servers"
    And I should see game filters
    And I should see server cards

  @visitor
  Scenario: Visitor learns about features
    Given I am on the home page
    Then I should see "Up in 60 Seconds"
    And I should see "DDoS Protection"
    And I should see "Built-In Friend System"

  @visitor
  Scenario: Visitor views supported games
    Given I am on the home page
    Then I should see "Minecraft"
    And I should see "Valheim"
    And I should see "Rust"

  @visitor
  Scenario: Visitor navigates to contact
    Given I am on the home page
    When I click the "Contact Us" link
    Then I should see "Contact"

  @visitor
  Scenario: Visitor checks system status
    Given I am on the home page
    When I click the "System Status" link
    Then I should see "System Status"

  # ==================== SHOPPING JOURNEYS ====================

  @shopping
  Scenario: Browse to cart journey
    Given I am on the home page
    When I click the "Browse Servers" button
    Then I should see "Browse Servers"
    When I click the cart icon
    Then I should see "Shopping Cart"

  @shopping
  Scenario: Browse servers and view configuration
    Given I am on the browse page
    Then I should see game filters
    And I should see "Configure"
    And I should see pricing information

  @shopping
  Scenario: Filter servers by game
    Given I am on the browse page
    Then I should see "Minecraft"
    And I should see "Valheim"

  # ==================== AUTHENTICATION JOURNEYS ====================

  @auth
  Scenario: Sign in journey from home
    Given I am on the home page
    When I click the "Sign In" button
    Then I should see "Sign in to manage your game servers"
    And I should see OAuth buttons

  @auth
  Scenario: Sign in journey from browse
    Given I am on the browse page
    When I click the "Sign In" button
    Then I should see "Sign in to manage your game servers"

  @auth
  Scenario: Login shows sign up link
    Given I am on the login page
    Then I should see "Don't have an account?"

  # ==================== CROSS-PAGE NAVIGATION ====================

  @navigation @e2e
  Scenario: Full site navigation
    Given I am on the home page
    When I click the "Browse Servers" button
    Then I should see "Browse Servers"
    When I click the cart icon
    Then I should see "Shopping Cart"
    When I press escape
    And I click the "Realm Grid" link
    Then I should see "Game Server Hosting"
    When I click the "Sign In" button
    Then I should see "Sign in to manage your game servers"

  @navigation
  Scenario: Footer navigation
    Given I am on the home page
    Then I should see "Terms"
    And I should see "Privacy"
    And I should see "System Status"
    And I should see "Contact Us"

  # ==================== RESPONSIVE JOURNEYS ====================

  @responsive @mobile
  Scenario: Mobile user journey
    Given I am on the home page
    Given I am viewing on a mobile device
    Then all content should be visible
    # On mobile, browse servers may be via hero CTA
    When I click the "Browse Servers" button
    Then I should see "Configure"

  @responsive @desktop
  Scenario: Desktop user journey
    Given I am on the home page
    Given I am viewing on desktop
    Then all content should be visible
    When I click the "Browse Servers" button
    Then I should see "Browse Servers"
    And I should see server cards
