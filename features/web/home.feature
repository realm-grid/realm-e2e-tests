@home
Feature: Home Page
  As a visitor
  I want to see the Realm Grid home page
  So that I can learn about game server hosting

  # ==================== VISUAL & THEME TESTING ====================

  @visual @theme
  Scenario: Page has dark theme
    Given I am on the home page
    Then the page should have a dark theme
    And the primary color should be purple

  @visual @theme
  Scenario: Hero section has gradient background
    Given I am on the home page
    Then the hero section should have a gradient background

  @visual @theme
  Scenario: Cards have glass effect styling
    Given I am on the home page
    When I scroll to the "Features" section
    Then cards should have a dark background with blur effect

  @visual @theme
  Scenario: Badges have colored backgrounds
    Given I am on the home page
    Then badges should have colored backgrounds

  # ==================== HERO SECTION ====================

  @hero @smoke
  Scenario: Hero section displays main content
    Given I am on the home page
    Then I should see "Realm Grid"
    And I should see "Game Server Hosting"
    And I should see a "Browse Servers" button
    And I should see a "Get Started" button

  @hero
  Scenario: Hero shows trust indicators
    Given I am on the home page
    Then I should see "99.9%"
    And I should see "Uptime"

  @hero
  Scenario: CTA buttons are prominent
    Given I am on the home page
    Then I should see a "Browse Servers" button
    And I should see a "Get Started" button

  # ==================== NAVIGATION ====================

  @navigation
  Scenario: Header is visible
    Given I am on the home page
    Then I should see "Realm Grid"
    And I should see a "Sign In" button

  @navigation
  Scenario: Browse servers navigation works
    Given I am on the home page
    When I click the "Browse Servers" button
    Then I should see "Browse Servers"

  @navigation
  Scenario: Sign in navigation works
    Given I am on the home page
    When I click the "Sign In" button
    Then I should see "Sign in to manage your game servers"

  # ==================== FEATURES SECTION ====================

  @features
  Scenario: Features section displays all features
    Given I am on the home page
    Then I should see "Up in 60 Seconds"
    And I should see "DDoS Protection"
    And I should see "Built-In Friend System"

  @features
  Scenario: Additional features are shown
    Given I am on the home page
    Then I should see "Real-Time Stats"
    And I should see "Chat Anywhere"

  # ==================== GAMES SECTION ====================

  @games
  Scenario: Supported games are displayed
    Given I am on the home page
    Then I should see "Minecraft"
    And I should see "Valheim"
    And I should see "Rust"
    And I should see "ARK"
    And I should see "Palworld"

  # ==================== STATS SECTION ====================

  @stats
  Scenario: Platform statistics are displayed
    Given I am on the home page
    Then I should see "99.9%"
    And I should see "Up in 60 Seconds"

  # ==================== CTA SECTION ====================

  @cta
  Scenario: Call to action section is present
    Given I am on the home page
    When I scroll to the "Ready to Get Started" section
    Then I should see "Ready to Get Started"

  # ==================== FOOTER ====================

  @footer
  Scenario: Footer displays company info
    Given I am on the home page
    Then I should see the footer
    And I should see "Terms"
    And I should see "Privacy"

  @footer
  Scenario: Footer has status and contact links
    Given I am on the home page
    Then I should see "System Status"
    And I should see "Contact"

  # ==================== RESPONSIVE DESIGN ====================

  @responsive @mobile
  Scenario: Home page is responsive on mobile
    Given I am on the home page
    Given I am viewing on a mobile device
    Then all content should be visible
    And I should not see horizontal scrollbar

  @responsive @tablet
  Scenario: Home page is responsive on tablet
    Given I am on the home page
    Given I am viewing on a tablet
    Then all content should be visible
    And I should not see horizontal scrollbar

  @responsive @desktop
  Scenario: Home page displays correctly on desktop
    Given I am on the home page
    Given I am viewing on desktop
    Then all content should be visible

  # ==================== ACCESSIBILITY ====================

  @accessibility
  Scenario: Page has proper landmarks
    Given I am on the home page
    Then the page should have a main landmark

  @accessibility
  Scenario: Buttons are accessible
    Given I am on the home page
    Then buttons should have accessible names

  @accessibility
  Scenario: Links are keyboard accessible
    Given I am on the home page
    Then links should be keyboard accessible

  # ==================== INTERACTIONS ====================

  @interaction
  Scenario: Buttons have hover effects
    Given I am on the home page
    Then buttons should have hover effects

  @interaction
  Scenario: Scroll to browse servers
    Given I am on the home page
    When I click the "Browse Servers" button
    Then I should see "Browse Servers"
    And I should see "Configure"
