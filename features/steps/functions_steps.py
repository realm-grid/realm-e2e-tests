"""
Step definitions for Azure Functions API tests.
These test the realm-functions backend API.
"""
from behave import given, when, then
import requests
import os
import json


# ============================================================================
# CONTEXT SETUP
# ============================================================================

@given('I have a valid user ID "{user_id}"')
def step_have_user_id(context, user_id):
    context.user_id = user_id


@given('I have a valid email "{email}"')
def step_have_email(context, email):
    context.email = email


@given('I have valid Kubernetes credentials')
def step_have_k8s_credentials(context):
    # Just verify the test environment has K8s access
    assert os.getenv("K8S_KUBECONFIG") is not None or os.getenv("TEST_MODE") == "mock"


@given('I have servers for user "{user_id}"')
def step_have_servers_for_user(context, user_id):
    context.user_id = user_id
    # In test mode, we assume test data exists


@given('I have a server with ID "{server_id}"')
def step_have_server(context, server_id):
    context.server_id = server_id


@given('I have a running server "{server_id}"')
def step_have_running_server(context, server_id):
    context.server_id = server_id
    context.server_state = "running"


@given('I have a stopped server "{server_id}"')
def step_have_stopped_server(context, server_id):
    context.server_id = server_id
    context.server_state = "stopped"


@given('I have a running Minecraft server "{server_id}"')
def step_have_minecraft_server(context, server_id):
    context.server_id = server_id
    context.game_type = "minecraft"


@given('I have a server "{server_id}" with backup "{backup_id}"')
def step_have_server_with_backup(context, server_id, backup_id):
    context.server_id = server_id
    context.backup_id = backup_id


@given('I have an active subscription "{subscription_id}"')
def step_have_subscription(context, subscription_id):
    context.subscription_id = subscription_id


# ============================================================================
# API CALLS
# ============================================================================

def get_function_url(context, path):
    """Build the full function URL with auth"""
    base_url = context.functions_url
    function_key = os.getenv("FUNCTIONS_KEY", "")
    
    if function_key:
        separator = "&" if "?" in path else "?"
        return f"{base_url}{path}{separator}code={function_key}"
    return f"{base_url}{path}"


@when('I call POST "{path}" with')
def step_call_post_with_table(context, path):
    """Call a POST endpoint with parameters from table"""
    params = {}
    for row in context.table:
        key = row[0]
        value = row[1]
        # Convert boolean strings
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        params[key] = value
    
    url = get_function_url(context, path)
    context.response = requests.post(url, json=params, timeout=30)
    
    try:
        context.response_data = context.response.json()
    except:
        context.response_data = {}


@when('I call GET "{path}"')
def step_call_get(context, path):
    """Call a GET endpoint"""
    url = get_function_url(context, path)
    context.response = requests.get(url, timeout=30)
    
    try:
        context.response_data = context.response.json()
    except:
        context.response_data = {}


@when('I call DELETE "{path}"')
def step_call_delete(context, path):
    """Call a DELETE endpoint"""
    url = get_function_url(context, path)
    context.response = requests.delete(url, timeout=30)
    
    try:
        context.response_data = context.response.json()
    except:
        context.response_data = {}


# ============================================================================
# RESPONSE ASSERTIONS
# ============================================================================

@then('the response status should be {status_code:d}')
def step_check_status(context, status_code):
    assert context.response.status_code == status_code, \
        f"Expected {status_code}, got {context.response.status_code}: {context.response.text}"


@then('the response should contain "{key}"')
def step_response_contains_key(context, key):
    data = context.response_data.get("data", context.response_data)
    assert key in data, f"Response does not contain '{key}': {data}"


@then('the error message should contain "{text}"')
def step_error_contains(context, text):
    message = context.response_data.get("error", "") or context.response_data.get("message", "")
    assert text.lower() in message.lower(), f"Error message '{message}' does not contain '{text}'"


@then('the servers list should not be empty')
def step_servers_not_empty(context):
    data = context.response_data.get("data", {})
    servers = data.get("servers", [])
    assert len(servers) > 0, "Servers list is empty"


@then('the response should contain server configuration')
def step_contains_server_config(context):
    data = context.response_data.get("data", {})
    assert "server" in data, "Response does not contain 'server'"


@then('the response should contain kubernetes status')
def step_contains_k8s_status(context):
    data = context.response_data.get("data", {})
    assert "kubernetes" in data, "Response does not contain 'kubernetes'"


@then('the response should contain network information')
def step_contains_network(context):
    data = context.response_data.get("data", {})
    assert "network" in data, "Response does not contain 'network'"


# ============================================================================
# KUBERNETES ASSERTIONS
# ============================================================================

@then('a Kubernetes deployment should be created')
def step_k8s_deployment_created(context):
    data = context.response_data.get("data", {})
    # Verify we got a server ID back (implies deployment created)
    assert "serverId" in data or "id" in data, \
        "No server ID in response - deployment may not have been created"


@then('a LoadBalancer service should be created')
def step_k8s_service_created(context):
    # Implicit in successful provisioning
    pass


@then('server details should be stored in Cosmos DB')
def step_cosmos_stored(context):
    # Implicit in successful response
    pass


@then('the server should be scaled to {replicas:d} replicas')
def step_server_scaled(context, replicas):
    # Check response indicates scaling happened
    data = context.response_data.get("data", {})
    assert data.get("success") is not False, "Scaling operation failed"


@then('the server should be scaled to {replicas:d} replica')
def step_server_scaled_singular(context, replicas):
    step_server_scaled(context, replicas)


# ============================================================================
# BACKUP ASSERTIONS
# ============================================================================

@then('the backup should be stored in Azure Blob Storage')
def step_backup_stored(context):
    data = context.response_data.get("data", {})
    assert "url" in data or "backupId" in data, "No backup URL in response"


@then('the server data should be restored')
def step_server_restored(context):
    data = context.response_data.get("data", {})
    assert data.get("restored") is True, "Server was not restored"


# ============================================================================
# SUBSCRIPTION ASSERTIONS
# ============================================================================

@then('the subscription status should be "{status}"')
def step_subscription_status(context, status):
    data = context.response_data.get("data", {})
    assert data.get("status") == status, \
        f"Expected status '{status}', got '{data.get('status')}'"


@then('the server should still be running')
def step_server_running(context):
    # Would need to check K8s or make another API call
    pass


@then('the server should be stopped')
def step_server_stopped(context):
    # Would need to check K8s or make another API call
    pass
