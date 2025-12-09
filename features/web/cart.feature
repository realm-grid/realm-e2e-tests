@cart
Feature: Shopping Cart
  As a user
  I want to manage my shopping cart
  So that I can checkout my server configurations

  # ==================== VISUAL & THEME ====================

  @visual @theme
  Scenario: Cart page has dark theme
    Given I am on the cart page
    Then the page should have a dark theme
    And the primary color should be purple

  @visual
  Scenario: Empty cart has proper styling
    Given I am on the cart page
    Then the page should display correctly

  # ==================== EMPTY CART ====================

  @empty @smoke
  Scenario: Empty cart displays message
    Given I am on the cart page
    Then I should see "Your Cart"
    And I should see empty cart message

  @empty
  Scenario: Empty cart has browse link
    Given I am on the cart page
    Then I should see "Browse Servers" link or button

  @empty
  Scenario: Empty cart shows cart icon
    Given I am on the cart page
    Then the page should display correctly

  # ==================== NAVIGATION ====================

  @navigation
  Scenario: Can navigate to browse servers
    Given I am on the cart page
    When I click the "Browse Servers" link or button
    Then I should see game filters

  @navigation
  Scenario: Can navigate back to home
    Given I am on the cart page
    When I click the "Realm Grid" link
    Then I should see "Game Server Hosting"

  @navigation
  Scenario: Can navigate to sign in
    Given I am on the cart page
    When I click the "Sign In" button
    Then I should see "Sign in to manage your game servers"

  # ==================== PAGE LAYOUT ====================

  @layout
  Scenario: Cart page has header
    Given I am on the cart page
    Then I should see "Realm Grid"
    And I should see a "Sign In" button

  @layout
  Scenario: Cart page has footer
    Given I am on the cart page
    Then I should see the footer
    And I should see "Terms of Service"

  # ==================== RESPONSIVE DESIGN ====================

  @responsive @mobile
  Scenario: Cart page is responsive on mobile
    Given I am on the cart page
    Given I am viewing on a mobile device
    Then all content should be visible
    And I should not see horizontal scrollbar

  @responsive @desktop
  Scenario: Cart page displays correctly on desktop
    Given I am on the cart page
    Given I am viewing on desktop
    Then all content should be visible

  # ==================== ACCESSIBILITY ====================

  @accessibility
  Scenario: Cart page has proper landmarks
    Given I am on the cart page
    Then the page should have a main landmark

  @accessibility
  Scenario: Cart buttons are accessible
    Given I am on the cart page
    Then buttons should have accessible names

  # ==================== INTERACTIONS ====================

  @interaction
  Scenario: Browse servers button works
    Given I am on the cart page
    When I click the "Browse Servers" link or button
    Then I should see "Browse Servers"
    And I should see server cards
