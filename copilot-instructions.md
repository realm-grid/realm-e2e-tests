# RealmGrid E2E Tests - Copilot Instructions

## Project Overview
End-to-end test suite for RealmGrid platform using Behave (BDD/Cucumber for Python) with Playwright for browser automation and Requests for API testing.

## Technology Stack
- **Framework**: Behave (Python BDD)
- **Browser Automation**: Playwright
- **API Testing**: Requests library
- **Assertions**: pytest-style assertions
- **Reporting**: HTML reports, JUnit XML

## Code Quality Standards

### File Size & Structure
- **Maximum 250 lines per file** - Split step definitions by domain/feature
- Each `.feature` file tests one specific feature area
- Step definition files organized by application: `web_steps.py`, `admin_steps.py`, `functions_steps.py`
- Keep scenario steps between 5-15 steps (not too granular, not too broad)
- Helper functions in separate utility files

### Test Organization
```
realm-e2e-tests/
├── features/
│   ├── web/                    # Customer portal tests
│   ├── admin/                  # Admin dashboard tests  
│   ├── functions/              # Azure Functions API tests
│   ├── e2e/                    # Full user journey tests
│   └── steps/                  # Step definitions
│       ├── web_steps.py        # Web app steps
│       ├── admin_steps.py      # Admin steps
│       ├── functions_steps.py  # API steps
│       └── e2e_flow_steps.py   # End-to-end flow steps
├── environment.py              # Behave hooks & setup
├── behave.ini                  # Configuration
└── requirements.txt            # Dependencies
```

### Feature File Guidelines

#### Structure
```gherkin
Feature: User Authentication
  As a user
  I want to log in securely
  So that I can access my game servers

  Background:
    Given the application is running
    And I am on the login page

  @smoke @authentication
  Scenario: Successful login with valid credentials
    When I enter valid credentials
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see my username in the header

  @negative
  Scenario: Failed login with invalid credentials
    When I enter invalid credentials
    And I click the login button
    Then I should see an error message
    And I should remain on the login page
```

#### Best Practices
- Feature name is descriptive and business-focused
- Include user story context (As/I want/So that)
- Use Background for common setup steps
- Tag scenarios appropriately: `@smoke`, `@regression`, `@api`, `@ui`
- Keep scenarios independent (no inter-scenario dependencies)
- Use Scenario Outline for data-driven tests
- Maximum 15 steps per scenario

### Step Definition Guidelines

#### Naming Patterns
```python
# Given - Preconditions/Setup
@given('I am logged in as a {role}')
@given('the server "{server_name}" exists')

# When - Actions
@when('I click the "{button_name}" button')
@when('I create a new server with plan "{plan}"')

# Then - Assertions
@then('I should see the text "{text}"')
@then('the server status should be "{status}"')
```

#### Implementation Standards
```python
from behave import given, when, then
from playwright.sync_api import Page, expect

# ✅ Good - Clear, focused, reusable
@when('I enter "{text}" in the "{field}" field')
def step_enter_text(context, text: str, field: str):
    """Enter text into a form field."""
    page: Page = context.page
    page.fill(f'[data-testid="{field}"]', text)

@then('I should see the error message "{message}"')
def step_verify_error(context, message: str):
    """Verify an error message is displayed."""
    page: Page = context.page
    error_element = page.locator('[data-testid="error-message"]')
    expect(error_element).to_have_text(message)

# ❌ Bad - Too specific, not reusable
@when('I enter john@example.com in the email field')
def step_hardcoded_email(context):
    context.page.fill('#email', 'john@example.com')
```

#### File Size Management
- Keep step files under 250 lines
- Group related steps together
- Extract complex logic to helper functions
- Create separate files per domain if needed:
  - `web_authentication_steps.py`
  - `web_servers_steps.py`
  - `web_billing_steps.py`

### Python Code Standards

#### Type Hints
```python
from typing import Optional
from behave.runner import Context

@given('I navigate to "{url}"')
def step_navigate(context: Context, url: str) -> None:
    """Navigate to a specific URL."""
    context.page.goto(url)
```

#### Error Handling
```python
@when('I submit the form')
def step_submit_form(context: Context) -> None:
    """Submit the current form."""
    try:
        context.page.click('[data-testid="submit-button"]')
        context.page.wait_for_load_state('networkidle')
    except TimeoutError:
        raise AssertionError("Form submission timed out")
```

#### Assertions
```python
# ✅ Use Playwright's expect for assertions
from playwright.sync_api import expect

expect(page.locator('[data-testid="title"]')).to_be_visible()
expect(page).to_have_url('https://example.com/dashboard')

# ✅ Use Python assertions for non-UI checks
assert response.status_code == 200
assert 'subscriptionId' in response.json()
```

### API Testing Standards

```python
import requests
from behave import when, then

@when('I send a POST request to "{endpoint}" with body')
def step_api_post(context: Context, endpoint: str) -> None:
    """Send POST request with JSON body from table."""
    url = f"{context.base_api_url}{endpoint}"
    body = context.table[0].as_dict() if context.table else {}
    
    context.response = requests.post(
        url, 
        json=body,
        headers={'Authorization': f'Bearer {context.api_token}'}
    )

@then('the response status should be {status_code:d}')
def step_verify_status(context: Context, status_code: int) -> None:
    """Verify HTTP response status code."""
    assert context.response.status_code == status_code, \
        f"Expected {status_code}, got {context.response.status_code}"
```

### Environment Configuration

#### environment.py Structure
```python
from playwright.sync_api import sync_playwright

def before_all(context):
    """Setup before entire test run."""
    context.config = load_config()
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(
        headless=context.config.get('headless', True)
    )

def before_scenario(context, scenario):
    """Setup before each scenario."""
    context.page = context.browser.new_page()
    context.page.goto(context.config['base_url'])

def after_scenario(context, scenario):
    """Cleanup after each scenario."""
    if scenario.status == 'failed':
        context.page.screenshot(path=f'reports/screenshots/{scenario.name}.png')
    context.page.close()

def after_all(context):
    """Cleanup after entire test run."""
    context.browser.close()
    context.playwright.stop()
```

### Tagging Strategy
```gherkin
@smoke                  # Critical path tests (run on every commit)
@regression            # Full regression suite
@api                   # API-only tests
@ui                    # UI-only tests
@slow                  # Tests that take >30 seconds
@wip                   # Work in progress (excluded from CI)
@skip                  # Temporarily disabled
@prod                  # Safe to run in production
@destructive           # May modify/delete data
```

### Data Management

#### Test Data
- Use fixtures for consistent test data
- Clean up created test data after scenarios
- Don't rely on existing production data
- Use unique identifiers (timestamps, UUIDs)

```python
@given('a test user exists')
def step_create_test_user(context: Context) -> None:
    """Create a test user for the scenario."""
    import uuid
    user_id = f"test_{uuid.uuid4().hex[:8]}"
    context.test_user = create_user(user_id)
    context.cleanup_users.append(user_id)  # Track for cleanup
```

### Page Object Pattern (Optional)
For complex UIs, consider using Page Objects:

```python
class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.locator('[data-testid="email"]')
        self.password_input = page.locator('[data-testid="password"]')
        self.login_button = page.locator('[data-testid="login-button"]')
    
    def login(self, email: str, password: str) -> None:
        """Perform login action."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()
```

### Selectors Best Practices
Priority order for element selection:
1. `data-testid` attributes (most stable)
2. Accessible roles and labels
3. Unique IDs
4. CSS classes (least stable)

```python
# ✅ Best - Test-specific attribute
page.locator('[data-testid="submit-button"]')

# ✅ Good - Semantic role
page.get_by_role('button', name='Submit')

# ⚠️ Acceptable - Unique ID
page.locator('#submit-btn')

# ❌ Avoid - Fragile class selector
page.locator('.btn.btn-primary.submit')
```

### Timeouts & Waits
```python
# Explicit wait for element
page.wait_for_selector('[data-testid="dashboard"]', timeout=5000)

# Wait for navigation
page.wait_for_url('**/dashboard')

# Wait for network to be idle
page.wait_for_load_state('networkidle')

# Custom wait condition
page.wait_for_function('() => document.readyState === "complete"')
```

### Reporting & Screenshots
- Capture screenshot on failure
- Save to `reports/screenshots/`
- Include scenario name and timestamp
- Generate HTML report for CI visibility

### CI/CD Integration
- Tests run on pull requests
- Separate smoke vs full regression runs
- Run against dev/test environments
- Never run destructive tests in prod

### Environment Variables
```bash
# Required
BASE_URL=https://dev.realmgrid.com
BASE_API_URL=https://realm-dev-api-fa.azurewebsites.net
ADMIN_URL=https://realm-dev-admin.azurewebsites.net

# Optional
HEADLESS=true
TIMEOUT=30000
SCREENSHOT_ON_FAILURE=true
```

### Anti-Patterns to Avoid
❌ Hard-coded URLs or credentials in step files  
❌ Steps dependent on execution order  
❌ Overly long scenarios (>15 steps)  
❌ Testing implementation details instead of behavior  
❌ No cleanup of test data  
❌ Ignoring failed tests  
❌ Complex logic in step definitions (extract to helpers)  
❌ Sleeping instead of explicit waits  

### Performance Guidelines
- Run tests in parallel when possible
- Use headless mode in CI
- Minimize unnecessary waits
- Reuse browser contexts where appropriate
- Skip UI tests for API-only validations

### Security Testing
- Test authentication flows
- Verify authorization (access control)
- Test input validation
- Check for sensitive data exposure
- SQL injection, XSS prevention tests

### Maintenance Checklist
- [ ] Update tests when features change
- [ ] Remove tests for deprecated features
- [ ] Keep selectors up to date
- [ ] Review and update test data
- [ ] Check for flaky tests and stabilize
- [ ] Document known issues or limitations

## Related Documentation
- [TESTING.md](./TESTING.md) - Test execution guide
- [README.md](./README.md) - Project setup
- [AZURE_DEV_SETUP.md](./AZURE_DEV_SETUP.md) - Azure environment setup

## Questions & Support
For test infrastructure issues or complex test scenarios, consult the team or update documentation with solutions.
