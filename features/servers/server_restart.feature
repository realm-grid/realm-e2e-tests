@servers @restart
Feature: Server Restart
  As an authenticated user
  I want to restart my game server
  So that I can apply configuration changes

  @smoke
  Scenario: User can list their servers
    Given the API is healthy
    Given I have logged in with SSO
    When I request "/api/game-servers" with my auth token
    Then I should receive a 200 response
    And the response should contain server data

  @smoke
  Scenario: User can restart their server
    Given the API is healthy
    Given I have logged in with SSO
    When I get my first server ID
    And I restart the server
    Then the restart should be initiated
