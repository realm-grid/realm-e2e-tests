Feature: End-to-End Subscription Flow
  As a customer
  I want to subscribe and get a game server automatically
  So I can start playing immediately

  @e2e @critical
  Scenario: Complete subscription flow - Minecraft Small
    # Customer journey from subscription to playing
    
    # Step 1: Create checkout session
    Given I have a valid user ID "e2e-user-001"
    And I have a valid email "e2e-test@example.com"
    When I call POST "/api/checkout/create" with:
      | userId     | e2e-user-001         |
      | email      | e2e-test@example.com |
      | gameType   | minecraft            |
      | tier       | small                |
      | serverName | E2E Test Server      |
      | provider   | stripe               |
    Then the response status should be 200
    And the response should contain "checkoutUrl"
    And I save the "sessionId" for later

    # Step 2: Simulate Stripe webhook (checkout completed)
    When I simulate Stripe webhook "checkout.session.completed" for the session
    Then the server should be provisioned
    And I should receive the server IP and port

    # Step 3: Verify server is running
    When I call GET "/api/servers?userId=e2e-user-001"
    Then the response status should be 200
    And the servers list should not be empty
    And the first server status should be "running"

    # Step 4: Get server details
    When I get the first server details
    Then the response status should be 200
    And the server game type should be "minecraft"
    And the kubernetes pod should be "Running"

    # Step 5: Execute a command on the server
    When I call POST the server command endpoint with:
      | command | list |
    Then the response status should be 200
    And the response should contain "output"

    # Step 6: Stop the server
    When I call POST the server stop endpoint
    Then the response status should be 200
    And the server should be scaled to 0 replicas

    # Step 7: Start the server
    When I call POST the server start endpoint
    Then the response status should be 200
    And the server should be scaled to 1 replica

    # Step 8: Create a backup
    When I call POST the server backup endpoint
    Then the response status should be 200
    And the response should contain "backupId"

    # Step 9: Cancel subscription at period end
    When I cancel the subscription with immediate=false
    Then the response status should be 200
    And the subscription status should be "canceling"
    And the server should still be running

    # Cleanup: Delete the server
    When I delete the test server
    Then the server should be removed from Kubernetes

  @e2e @billing
  Scenario: Payment failure suspends server
    Given I have a running server for user "e2e-user-002"
    When I simulate Stripe webhook "invoice.payment_failed" with 2 attempts
    Then the server should be stopped
    And the subscription status should be "past_due"

  @e2e @billing
  Scenario: Payment recovery resumes server
    Given I have a suspended server for user "e2e-user-003"
    When I simulate Stripe webhook "invoice.paid"
    Then the server should be started
    And the subscription status should be "active"

  @e2e @upgrade
  Scenario: Upgrade tier increases resources
    Given I have a small tier server for user "e2e-user-004"
    When I call PATCH the server with:
      | tier | medium |
    Then the response status should be 200
    And the server resources should be updated to "medium"
    And the pod should be restarted with new resources
