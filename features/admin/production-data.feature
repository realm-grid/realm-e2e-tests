@admin @production-data @smoke
Feature: Admin Portal Production Data
  As a RealmGrid administrator
  I want to view production data from Cosmos DB
  So that I can manage servers, subscriptions, and users

  Background:
    Given the admin portal is running on "http://localhost:4321"
    And the dev Function Apps are accessible

  @auth @dev-login
  Scenario: Login to admin portal with dev credentials
    Given I am on the admin portal login page
    When I click the "Development Login" button
    Then I should be redirected to the dashboard
    And the dashboard should display stats

  @api @servers
  Scenario: Fetch servers from dev Function Apps
    Given I am logged into the admin portal
    When the dashboard loads
    Then I should see a call to "/global-admin/servers"
    And the admin response should contain server data
    And I should see at least 2 servers
    And one server should be "minecraft" type
    And one server should be in "running" status

  @api @subscriptions
  Scenario: Fetch subscriptions from dev Function Apps
    Given I am logged into the admin portal
    When the dashboard loads
    Then I should see a call to "/global-admin/subscriptions"
    And the admin response should contain subscription data
    And I should see at least 1 subscription
    And subscriptions should have Mollie IDs

  @integration @end-to-end
  Scenario: Verify complete production data flow
    Given I am logged into the admin portal
    When the dashboard loads
    Then I should see production data for:
      | Data Type     | Expected Count | Expected Values                    |
      | Servers       | 2              | minecraft, running, pending        |
      | Subscriptions | 1              | active, pro, €14.99                |
      | Users         | 2              | test.sso.user, yair@cloudevolvers |
    And the dashboard stats should show:
      | Stat               | Value |
      | Total Servers      | 2     |
      | Running Servers    | 1     |
      | Total Customers    | 2     |
      | Active Subscriptions | 1   |
