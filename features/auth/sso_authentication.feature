@auth @sso
Feature: SSO Authentication
  As a user
  I want to authenticate using Azure AD SSO
  So that I can access protected resources

  Background:
    Given the API is healthy

  @smoke
  Scenario: Unauthenticated user cannot access protected endpoints
    When I request "/api/auth/me" without authentication
    Then I should receive a 401 response
    And the response should indicate "No session token provided"

  @smoke @login
  Scenario: User can login with Azure AD SSO
    Given I am not authenticated
    When I initiate SSO login with Azure AD
    Then I should be authenticated
    And the session should be valid

  @smoke @session
  Scenario: Authenticated user has a valid session
    Given I have logged in with SSO
    When I request "/api/auth/me" with my auth token
    Then I should receive a 200 response
    And the response should contain my user information
    And my email should be "test.sso.user@xevolve.io"

  @profile @wip
  Scenario: Authenticated user can access their profile page
    Given I have logged in with SSO
    When I navigate to the profile page
    Then I should see my profile information
    And I should see my email address
    And I should see my display name

  @servers @wip
  Scenario: Authenticated user can view the servers page
    Given I have logged in with SSO
    When I navigate to the servers page
    Then I should see the servers list
    And the page should load without errors

  @servers @wip
  Scenario: Authenticated user can access server details
    Given I have logged in with SSO
    And there is at least one server available
    When I navigate to the servers page
    And I click on a server
    Then I should see the server details page
    And I should see the server status

  @logout
  Scenario: User can logout
    Given I have logged in with SSO
    When I click the logout button
    Then I should be logged out
    And my session should be invalidated

  @session @negative
  Scenario: Expired token is rejected
    Given I have an expired auth token
    When I request "/api/auth/me" with my auth token
    Then I should receive a 401 response
    And the response should indicate "Invalid session"

  @session @negative  
  Scenario: Invalid token is rejected
    Given I have an invalid auth token
    When I request "/api/auth/me" with my auth token
    Then I should receive a 401 response
    And the response should indicate "Invalid session token"
