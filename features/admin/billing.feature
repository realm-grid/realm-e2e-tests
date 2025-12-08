Feature: Admin Billing Management
  As an admin
  I want to manage customer subscriptions
  So that I can monitor revenue and handle billing issues

  Background:
    Given I am logged in as an admin
    And I am on the admin dashboard

  @smoke @admin @billing
  Scenario: View billing overview
    When I navigate to the billing section
    Then I should see the monthly recurring revenue
    And I should see active subscriptions count
    And I should see recent transactions

  @admin @billing
  Scenario: View subscription details
    When I navigate to billing subscriptions
    And I click on a subscription
    Then I should see the subscription details
    And I should see the customer information
    And I should see payment history

  @admin @billing
  Scenario: Cancel a subscription
    When I navigate to billing subscriptions
    And I select a subscription to cancel
    And I click "Cancel Subscription"
    And I confirm the cancellation
    Then I should see "Subscription cancelled successfully"
    And the subscription status should be "canceled"

  @admin @billing @chargebacks
  Scenario: Handle a chargeback
    When I navigate to billing chargebacks
    And I select a chargeback that needs response
    And I submit evidence for the chargeback
    Then I should see "Evidence submitted successfully"
    And the chargeback status should be "under_review"

  @admin @billing @mollie
  Scenario: Test Mollie payment in DTA
    When I navigate to billing mollie console
    And I create a test payment for "€9.99"
    And I simulate payment status "paid"
    Then I should see "Payment updated successfully"
    And the payment status should be "paid"
