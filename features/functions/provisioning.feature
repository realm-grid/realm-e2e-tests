Feature: Game Server Provisioning via Functions
  As a platform
  I want to provision game servers via Azure Functions
  So that customers can play on their own servers

  @smoke @functions @provisioning
  Scenario: Create checkout session
    Given I have a valid user ID "test-user-123"
    And I have a valid email "test@example.com"
    When I call POST "/api/checkout/create" with:
      | userId    | test-user-123      |
      | email     | test@example.com   |
      | gameType  | minecraft          |
      | plan      | starter            |
      | provider  | stripe             |
    Then the response status should be 200
    And the response should contain "checkoutUrl"
    And the response should contain "sessionId"

  @functions @provisioning
  Scenario: Provision a Minecraft server
    Given I have valid Kubernetes credentials
    When I call POST "/api/servers/provision" with:
      | userId         | test-user-123      |
      | subscriptionId | sub_test123        |
      | gameType       | minecraft          |
      | plan           | starter            |
      | serverName     | Test Minecraft     |
    Then the response status should be 200
    And the response should contain "serverId"
    And a Kubernetes deployment should be created
    And a LoadBalancer service should be created
    And server details should be stored in Cosmos DB

  @functions @provisioning
  Scenario: Provision server with invalid game type
    When I call POST "/api/servers/provision" with:
      | userId   | test-user-123 |
      | gameType | invalid-game  |
      | plan     | starter       |
    Then the response status should be 400
    And the error message should contain "Unknown game type"

  @functions @provisioning
  Scenario: List servers for a user
    Given I have servers for user "test-user-123"
    When I call GET "/api/servers?userId=test-user-123"
    Then the response status should be 200
    And the response should contain "servers"
    And the servers list should not be empty

  @functions @provisioning
  Scenario: Get server details
    Given I have a server with ID "server-123"
    When I call GET "/api/servers/server-123"
    Then the response status should be 200
    And the response should contain server configuration
    And the response should contain kubernetes status
    And the response should contain network information

  @functions @lifecycle
  Scenario: Stop a running server
    Given I have a running server "server-123"
    When I call POST "/api/servers/server-123/stop"
    Then the response status should be 200
    And the server should be scaled to 0 replicas

  @functions @lifecycle
  Scenario: Start a stopped server
    Given I have a stopped server "server-123"
    When I call POST "/api/servers/server-123/start"
    Then the response status should be 200
    And the server should be scaled to 1 replica

  @functions @lifecycle
  Scenario: Execute RCON command
    Given I have a running Minecraft server "server-123"
    When I call POST "/api/servers/server-123/command" with:
      | command | say Hello World! |
    Then the response status should be 200
    And the response should contain "output"

  @functions @backup
  Scenario: Create a backup
    Given I have a running server "server-123"
    When I call POST "/api/servers/server-123/backup"
    Then the response status should be 200
    And the response should contain "backupId"
    And the backup should be stored in Azure Blob Storage

  @functions @backup
  Scenario: Restore from backup
    Given I have a server "server-123" with backup "backup-456"
    When I call POST "/api/servers/server-123/restore" with:
      | backupId | backup-456 |
    Then the response status should be 200
    And the server data should be restored

  @functions @billing
  Scenario: Cancel subscription at period end
    Given I have an active subscription "sub-123"
    When I call POST "/api/subscriptions/sub-123/cancel" with:
      | immediate | false |
    Then the response status should be 200
    And the subscription status should be "canceling"
    And the server should still be running

  @functions @billing
  Scenario: Cancel subscription immediately
    Given I have an active subscription "sub-123"
    When I call POST "/api/subscriptions/sub-123/cancel" with:
      | immediate | true |
    Then the response status should be 200
    And the subscription status should be "canceled"
    And the server should be stopped
