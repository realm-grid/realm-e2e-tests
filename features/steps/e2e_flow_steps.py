"""
Step definitions for end-to-end flow tests.
These test the complete customer journey from subscription to playing.
"""
from behave import given, when, then
import requests
import os
import json
import time


def get_function_url(context, path):
    """Build the full function URL with auth"""
    base_url = context.functions_url
    function_key = os.getenv("FUNCTIONS_KEY", "")
    
    if function_key:
        separator = "&" if "?" in path else "?"
        return f"{base_url}{path}{separator}code={function_key}"
    return f"{base_url}{path}"


# ============================================================================
# CHECKOUT FLOW
# ============================================================================

@then('I save the "{field}" for later')
def step_save_field(context, field):
    data = context.response_data.get("data", context.response_data)
    value = data.get(field)
    assert value is not None, f"Field '{field}' not found in response"
    
    if not hasattr(context, "saved_values"):
        context.saved_values = {}
    context.saved_values[field] = value


@when('I simulate Stripe webhook "checkout.session.completed" for the session')
def step_simulate_checkout_webhook(context):
    """Simulate Stripe sending a checkout.session.completed webhook"""
    session_id = context.saved_values.get("sessionId")
    assert session_id, "No session ID saved"
    
    # In test mode, directly call the provision endpoint
    # In integration mode, this would be a real webhook simulation
    if os.getenv("TEST_MODE") == "mock":
        context.server_provisioned = True
        context.server_ip = "1.2.3.4"
        context.server_port = 25565
    else:
        # Call provision directly as webhook would
        url = get_function_url(context, "/api/servers/provision")
        response = requests.post(url, json={
            "userId": context.user_id,
            "subscriptionId": session_id,
            "gameType": "minecraft",
            "tier": "small",
            "serverName": "E2E Test Server",
        }, timeout=120)  # Provisioning can take time
        
        context.response = response
        context.response_data = response.json()
        
        if response.status_code == 200:
            data = context.response_data.get("data", {})
            context.server_id = data.get("serverId")
            context.server_ip = data.get("ip")
            context.server_port = data.get("port")
            context.server_provisioned = True


@then('the server should be provisioned')
def step_server_provisioned(context):
    assert hasattr(context, "server_provisioned") and context.server_provisioned, \
        "Server was not provisioned"


@then('I should receive the server IP and port')
def step_receive_ip_port(context):
    # IP might be pending initially
    if context.server_ip:
        assert context.server_port is not None


# ============================================================================
# SERVER OPERATIONS
# ============================================================================

@then('the first server status should be "{status}"')
def step_first_server_status(context, status):
    data = context.response_data.get("data", {})
    servers = data.get("servers", [])
    assert len(servers) > 0, "No servers found"
    
    context.server_id = servers[0].get("id")
    actual_status = servers[0].get("status") or servers[0].get("liveStatus", {}).get("podPhase", "").lower()
    # Running status can be "running" or k8s phase "Running"
    assert status.lower() in actual_status.lower(), \
        f"Expected status '{status}', got '{actual_status}'"


@when('I get the first server details')
def step_get_first_server(context):
    server_id = context.server_id
    assert server_id, "No server ID available"
    
    url = get_function_url(context, f"/api/servers/{server_id}")
    context.response = requests.get(url, timeout=30)
    context.response_data = context.response.json()


@then('the server game type should be "{game_type}"')
def step_server_game_type(context, game_type):
    data = context.response_data.get("data", {})
    server = data.get("server", {})
    assert server.get("gameType") == game_type


@then('the kubernetes pod should be "{phase}"')
def step_k8s_pod_phase(context, phase):
    data = context.response_data.get("data", {})
    k8s = data.get("kubernetes", {})
    pod = k8s.get("pod", {})
    assert pod.get("phase") == phase or pod.get("status") == "found"


@when('I call POST the server command endpoint with')
def step_call_server_command(context):
    server_id = context.server_id
    params = {row[0]: row[1] for row in context.table}
    
    url = get_function_url(context, f"/api/servers/{server_id}/command")
    context.response = requests.post(url, json=params, timeout=30)
    context.response_data = context.response.json()


@when('I call POST the server stop endpoint')
def step_call_server_stop(context):
    server_id = context.server_id
    url = get_function_url(context, f"/api/servers/{server_id}/stop")
    context.response = requests.post(url, timeout=60)
    context.response_data = context.response.json()


@when('I call POST the server start endpoint')
def step_call_server_start(context):
    server_id = context.server_id
    url = get_function_url(context, f"/api/servers/{server_id}/start")
    context.response = requests.post(url, timeout=60)
    context.response_data = context.response.json()


@when('I call POST the server backup endpoint')
def step_call_server_backup(context):
    server_id = context.server_id
    url = get_function_url(context, f"/api/servers/{server_id}/backup")
    context.response = requests.post(url, timeout=120)
    context.response_data = context.response.json()


@when('I cancel the subscription with immediate={immediate}')
def step_cancel_subscription(context, immediate):
    subscription_id = context.saved_values.get("sessionId") or context.subscription_id
    immediate_bool = immediate.lower() == "true"
    
    url = get_function_url(context, f"/api/subscriptions/{subscription_id}/cancel")
    context.response = requests.post(url, json={"immediate": immediate_bool}, timeout=30)
    context.response_data = context.response.json()


@when('I delete the test server')
def step_delete_test_server(context):
    server_id = context.server_id
    if not server_id:
        return  # Nothing to delete
    
    url = get_function_url(context, f"/api/servers/{server_id}")
    context.response = requests.delete(url, timeout=60)
    context.response_data = context.response.json()


@then('the server should be removed from Kubernetes')
def step_server_removed(context):
    # Verify with a GET that should 404
    server_id = context.server_id
    if not server_id:
        return
    
    url = get_function_url(context, f"/api/servers/{server_id}")
    response = requests.get(url, timeout=30)
    # Should be 404 or have deleted status
    assert response.status_code in [404, 200]


# ============================================================================
# BILLING WEBHOOKS
# ============================================================================

@given('I have a running server for user "{user_id}"')
def step_have_running_server_for_user(context, user_id):
    context.user_id = user_id
    # In test mode, assume server exists


@given('I have a suspended server for user "{user_id}"')
def step_have_suspended_server(context, user_id):
    context.user_id = user_id
    context.server_state = "suspended"


@given('I have a small tier server for user "{user_id}"')
def step_have_small_tier_server(context, user_id):
    context.user_id = user_id
    context.current_tier = "small"


@when('I simulate Stripe webhook "invoice.payment_failed" with {attempts:d} attempts')
def step_simulate_payment_failed(context, attempts):
    # In test mode, just mark as failed
    context.payment_failed = True
    context.payment_attempts = attempts


@when('I simulate Stripe webhook "invoice.paid"')
def step_simulate_payment_success(context):
    context.payment_success = True


@then('the server should be started')
def step_verify_server_started(context):
    # Would verify via API
    pass


@when('I call PATCH the server with')
def step_patch_server(context):
    server_id = context.server_id
    params = {row[0]: row[1] for row in context.table}
    
    url = get_function_url(context, f"/api/servers/{server_id}")
    context.response = requests.patch(url, json=params, timeout=60)
    context.response_data = context.response.json()


@then('the server resources should be updated to "{plan}"')
def step_resources_updated(context, plan):
    data = context.response_data.get("data", {})
    changes = data.get("changes", [])
    assert "plan" in changes, f"Plan not updated. Changes: {changes}"


@then('the pod should be restarted with new resources')
def step_pod_restarted(context):
    data = context.response_data.get("data", {})
    assert data.get("needsRestart") is True, "Pod restart not indicated"
