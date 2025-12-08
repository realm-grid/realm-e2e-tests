"""
Step definitions for web application tests
"""
from behave import given, when, then

@given('I am logged in as a customer')
def step_impl(context):
    context.page.goto(f"{context.web_url}/login")
    context.page.fill('input[name="email"]', context.test_user["email"])
    context.page.fill('input[name="password"]', context.test_user["password"])
    context.page.click('button[type="submit"]')
    context.page.wait_for_url(f"{context.web_url}/dashboard")

@given('I have no active subscriptions')
def step_impl(context):
    # Check that no subscription badge is shown
    assert not context.page.locator('[data-testid="active-subscription"]').is_visible()

@given('I am on the pricing page')
def step_impl(context):
    context.page.goto(f"{context.web_url}/pricing")

@when('I select the "{plan}" plan with "{interval}" billing')
def step_impl(context, plan, interval):
    context.page.click(f'[data-plan="{plan}"]')
    context.page.click(f'[data-interval="{interval}"]')

@when('I enter my Stripe payment details')
def step_impl(context):
    # Switch to Stripe iframe
    stripe_frame = context.page.frame_locator('iframe[name^="__privateStripeFrame"]')
    stripe_frame.locator('input[name="cardnumber"]').fill(context.stripe_test_card["number"])
    stripe_frame.locator('input[name="exp-date"]').fill(
        f"{context.stripe_test_card['exp_month']}{context.stripe_test_card['exp_year'][2:]}"
    )
    stripe_frame.locator('input[name="cvc"]').fill(context.stripe_test_card["cvc"])

@when('I confirm the subscription')
def step_impl(context):
    context.page.click('button:has-text("Subscribe")')
    context.page.wait_for_timeout(2000)

@then('I should be redirected to my dashboard')
def step_impl(context):
    context.page.wait_for_url(f"{context.web_url}/dashboard")

@then('I should see my small tier subscription')
def step_impl(context):
    assert context.page.locator('[data-tier="small"]').is_visible()

@given('I am on the pricing page in DTA environment')
def step_impl(context):
    assert context.environment in ["dev", "test", "acc"]
    context.page.goto(f"{context.web_url}/pricing")

@when('I choose Mollie as payment method')
def step_impl(context):
    context.page.click('[data-payment-provider="mollie"]')

@when('I select "{payment_method}" payment')
def step_impl(context, payment_method):
    context.page.click(f'[data-mollie-method="{payment_method.lower()}"]')

@when('I complete the Mollie payment flow')
def step_impl(context):
    context.page.click('button:has-text("Pay with Mollie")')
    context.page.wait_for_timeout(2000)
    # Simulate successful payment in test mode
    if context.page.url.startswith("https://www.mollie.com"):
        context.page.click('button:has-text("Paid")')

@then('I should have access to medium tier features')
def step_impl(context):
    assert context.page.locator('[data-tier="medium"]').is_visible()

@given('I have an active small tier subscription')
def step_impl(context):
    context.page.goto(f"{context.web_url}/dashboard")
    assert context.page.locator('[data-tier="small"]').is_visible()

@given('I am on my subscription page')
def step_impl(context):
    context.page.goto(f"{context.web_url}/subscription")

@when('I select "{option}"')
def step_impl(context, option):
    context.page.click(f'input[value="{option.lower().replace(" ", "_")}"]')

@then('my subscription status should be "{status}" with cancel scheduled')
def step_impl(context, status):
    assert context.page.locator(f'[data-status="{status}"]').is_visible()
    assert context.page.locator('text="Cancels at end of period"').is_visible()

@given('I am on my billing page')
def step_impl(context):
    context.page.goto(f"{context.web_url}/billing")

@when('I navigate to invoices')
def step_impl(context):
    context.page.click('a[href="/billing/invoices"]')

@then('I should see my subscription invoices')
def step_impl(context):
    assert context.page.locator('table tbody tr').count() > 0

@then('I should be able to download invoice PDFs')
def step_impl(context):
    assert context.page.locator('a[download]:has-text("Download")').count() > 0
