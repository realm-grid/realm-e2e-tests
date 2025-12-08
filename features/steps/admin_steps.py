"""
Step definitions for admin dashboard tests
"""
from behave import given, when, then

@given('I am logged in as an admin')
def step_impl(context):
    context.page.goto(f"{context.admin_url}/login")
    context.page.fill('input[name="email"]', context.admin_user["email"])
    context.page.fill('input[name="password"]', context.admin_user["password"])
    context.page.click('button[type="submit"]')
    context.page.wait_for_url(f"{context.admin_url}/dashboard")

@given('I am on the admin dashboard')
def step_impl(context):
    context.page.goto(f"{context.admin_url}/dashboard")

@when('I navigate to the billing section')
def step_impl(context):
    context.page.click('a[href="/billing"]')
    context.page.wait_for_url(f"{context.admin_url}/billing")

@then('I should see the monthly recurring revenue')
def step_impl(context):
    assert context.page.locator('text="Monthly Recurring Revenue"').is_visible()
    assert context.page.locator('[data-testid="mrr-value"]').is_visible()

@then('I should see active subscriptions count')
def step_impl(context):
    assert context.page.locator('text="Active Subscriptions"').is_visible()

@then('I should see recent transactions')
def step_impl(context):
    assert context.page.locator('text="Recent Transactions"').is_visible()

@when('I navigate to billing subscriptions')
def step_impl(context):
    context.page.click('a[href="/billing/subscriptions"]')

@when('I click on a subscription')
def step_impl(context):
    context.page.click('tbody tr:first-child')

@then('I should see the subscription details')
def step_impl(context):
    assert context.page.locator('[data-testid="subscription-details"]').is_visible()

@then('I should see the customer information')
def step_impl(context):
    assert context.page.locator('[data-testid="customer-info"]').is_visible()

@when('I select a subscription to cancel')
def step_impl(context):
    context.page.click('tbody tr:first-child [data-action="cancel"]')

@when('I click "{button_text}"')
def step_impl(context, button_text):
    context.page.click(f'button:has-text("{button_text}")')

@when('I confirm the cancellation')
def step_impl(context):
    context.page.click('button:has-text("Confirm")')

@then('I should see "{message}"')
def step_impl(context, message):
    assert context.page.locator(f'text="{message}"').is_visible()

@then('the subscription status should be "{status}"')
def step_impl(context, status):
    assert context.page.locator(f'[data-status="{status}"]').is_visible()

@when('I navigate to billing chargebacks')
def step_impl(context):
    context.page.click('a[href="/billing/chargebacks"]')

@when('I select a chargeback that needs response')
def step_impl(context):
    context.page.click('tbody tr[data-status="needs_response"]:first-child')

@when('I submit evidence for the chargeback')
def step_impl(context):
    context.page.fill('textarea[name="description"]', 'Test evidence for chargeback')
    context.page.click('button:has-text("Submit Evidence")')

@then('the chargeback status should be "{status}"')
def step_impl(context, status):
    assert context.page.locator(f'[data-chargeback-status="{status}"]').is_visible()

@when('I navigate to billing mollie console')
def step_impl(context):
    context.page.click('a[href="/billing/mollie"]')

@when('I create a test payment for "{amount}"')
def step_impl(context, amount):
    context.page.fill('input[name="amount"]', amount.replace('€', ''))
    context.page.click('button:has-text("Create Payment")')

@when('I simulate payment status "{status}"')
def step_impl(context, status):
    context.page.select_option('select[name="status"]', status)
    context.page.click('button:has-text("Update Status")')

@then('the payment status should be "{status}"')
def step_impl(context, status):
    assert context.page.locator(f'[data-payment-status="{status}"]').is_visible()
