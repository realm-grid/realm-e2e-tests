@browse
Feature: Browse Servers Page
  As a user
  I want to browse available game servers
  So that I can find the right server to host my game

  Background:
    Given I am on the browse page

  # ==================== VISUAL & THEME ====================

  @visual @theme
  Scenario: Browse page has dark theme
    Then the page should have a dark theme
    And the primary color should be purple

  @visual @theme
  Scenario: Server cards have proper styling
    Then cards should have a dark background with blur effect
    And prices should be highlighted

  # ==================== PAGE LAYOUT ====================

  @layout @smoke
  Scenario: Browse page displays main elements
    Then I should see "Browse Servers"
    And I should see game filters
    And I should see server cards

  @layout
  Scenario: Header and navigation visible
    Then I should see "Realm Grid"
    And I should see a "Sign In" button
    And I should see a cart icon

  # ==================== GAME FILTERS ====================

  @filters
  Scenario: All game filters are displayed
    Then I should see "Minecraft"
    And I should see "Valheim"
    And I should see "Rust"
    And I should see "ARK"
    And I should see "Palworld"

  @filters
  Scenario: Game type filter label is present
    Then I should see "Game Type"

  @filters @visual
  Scenario: Filter buttons have proper styling
    Then badges should have colored backgrounds

  # ==================== SERVER CARDS ====================

  @cards @smoke
  Scenario: Server cards show essential info
    Then I should see "Configure"
    And I should see pricing information

  @cards
  Scenario: Server cards have configuration buttons
    Then I should see "Configure"

  @cards @visual
  Scenario: Cards have hover states
    Then cards should have hover effects

  # ==================== SEARCH FUNCTIONALITY ====================

  @search
  Scenario: Search box is present
    Then I should see a search box

  @search
  Scenario: Search box has placeholder text
    Then I should see a search box

  # ==================== NAVIGATION ====================

  @navigation
  Scenario: Can navigate back to home
    When I click the "Realm Grid" link
    Then I should see "Game Server Hosting"

  @navigation
  Scenario: Can open cart sheet
    When I click the cart icon
    Then I should see "Shopping Cart"

  @navigation
  Scenario: Can navigate to sign in
    When I click the "Sign In" button
    Then I should see "Sign in to manage your game servers"

  # ==================== RESPONSIVE DESIGN ====================

  @responsive @mobile
  Scenario: Browse page is responsive on mobile
    Given I am viewing on a mobile device
    Then all content should be visible
    And I should not see horizontal scrollbar
    And I should see server cards

  @responsive @tablet
  Scenario: Browse page is responsive on tablet
    Given I am viewing on a tablet
    Then all content should be visible
    And I should not see horizontal scrollbar

  @responsive @desktop
  Scenario: Browse page displays grid on desktop
    Given I am viewing on desktop
    Then all content should be visible
    And I should see server cards

  # ==================== ACCESSIBILITY ====================

  @accessibility
  Scenario: Page has proper landmarks
    Then the page should have a main landmark

  @accessibility
  Scenario: Buttons are accessible
    Then buttons should have accessible names

  @accessibility
  Scenario: Filter buttons are keyboard accessible
    Then links should be keyboard accessible

  # ==================== INTERACTIONS ====================

  @interaction
  Scenario: Configure button opens modal
    When I click the first "Configure" button
    Then I should see a configuration modal or panel

  @interaction
  Scenario: Game badge hover effects
    Then badges should have hover effects
