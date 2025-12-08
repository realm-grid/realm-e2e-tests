Feature: Customer Subscription
  As a customer
  I want to subscribe to a game server plan
  So that I can host my game servers

  Background:
    Given I am logged in as a customer
    And I have no active subscriptions

  @smoke @web @billing
  Scenario: Subscribe to small tier with Stripe
    Given I am on the pricing page
    When I select the "small" tier with "monthly" billing
    And I enter my Stripe payment details
    And I confirm the subscription
    Then I should see "Subscription activated"
    And I should be redirected to my dashboard
    And I should see my small tier subscription

  @web @billing @mollie
  Scenario: Subscribe to medium tier with Mollie (DTA only)
    Given I am on the pricing page in DTA environment
    When I select the "medium" tier with "monthly" billing
    And I choose Mollie as payment method
    And I select "iDEAL" payment
    And I complete the Mollie payment flow
    Then I should see "Subscription activated"
    And I should have access to medium tier features

  @web @billing
  Scenario: Upgrade from small to medium tier
    Given I have an active small tier subscription
    And I am on my subscription page
    When I click "Upgrade Tier"
    And I select the "medium" tier
    And I confirm the upgrade
    Then I should see "Tier upgraded successfully"
    And my subscription should be "medium"

  @web @billing
  Scenario: Cancel subscription
    Given I have an active subscription
    And I am on my subscription page
    When I click "Cancel Subscription"
    And I select "End of current period"
    And I confirm cancellation
    Then I should see "Subscription will be cancelled at period end"
    And my subscription status should be "active" with cancel scheduled

  @web @billing
  Scenario: View invoices
    Given I have an active subscription
    And I am on my billing page
    When I navigate to invoices
    Then I should see my subscription invoices
    And I should be able to download invoice PDFs
