# RealmGrid E2E Tests

End-to-end testing suite for RealmGrid platform using Cucumber (Python with Behave).

## Overview

This repository contains comprehensive E2E tests for:
- **realm-admin**: Admin dashboard
- **realm-web**: Customer-facing web application
- **realm-functions**: Azure Functions backend

## Technology Stack

- **Behave**: Python BDD framework (Cucumber for Python)
- **Playwright**: Browser automation
- **Requests**: API testing
- **pytest**: Test assertions

## Project Structure

```
realm-e2e-tests/
├── features/
│   ├── admin/              # Admin dashboard tests
│   │   ├── billing.feature
│   │   ├── servers.feature
│   │   └── vms.feature
│   ├── web/                # Web application tests
│   │   ├── auth.feature
│   │   ├── subscription.feature
│   │   └── servers.feature
│   ├── functions/          # Azure Functions tests
│   │   ├── provisioning.feature
│   │   ├── billing.feature
│   │   └── deployment.feature
│   └── steps/              # Step definitions
│       ├── admin_steps.py
│       ├── web_steps.py
│       └── functions_steps.py
├── environment.py          # Behave hooks
├── requirements.txt
└── pytest.ini
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for Playwright)

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Configuration

Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running Tests

```bash
# Run all tests
behave

# Run specific feature
behave features/admin/billing.feature

# Run with tags
behave --tags=@smoke
behave --tags=@admin
behave --tags=@billing

# Run with specific environment
behave -D environment=dev
behave -D environment=prod
```

### Parallel Execution

```bash
# Run tests in parallel
behave --parallel
```

## Test Tags

- `@smoke`: Critical smoke tests
- `@regression`: Full regression suite
- `@admin`: Admin dashboard tests
- `@web`: Web application tests
- `@functions`: Azure Functions tests
- `@billing`: Billing-related tests
- `@provisioning`: VM provisioning tests

## CI/CD

Tests run automatically on:
- Pull requests to main
- Nightly schedule (full regression)
- Manual trigger

See `.github/workflows/e2e-tests.yml`

## Writing Tests

Example feature file:

```gherkin
Feature: User Subscription
  As a customer
  I want to subscribe to a tier
  So that I can use game servers

  @smoke @web @billing
  Scenario: Subscribe to small tier
    Given I am on the pricing page
    When I select the "small" tier
    And I enter payment details
    And I confirm the subscription
    Then I should see "Subscription activated"
    And I should have access to small tier features
```

Example step definition:

```python
@given('I am on the pricing page')
def step_impl(context):
    context.page.goto(f"{context.web_url}/pricing")

@when('I select the "{tier}" tier')
def step_impl(context, tier):
    context.page.click(f'button[data-tier="{tier}"]')
```

## Environments

| Environment | Admin URL | Web URL | Functions URL |
|-------------|-----------|---------|---------------|
| dev | https://realm-dev-admin.azurewebsites.net | https://dev.realmgrid.com | https://realm-dev-functions.azurewebsites.net |
| test | https://realm-test-admin.azurewebsites.net | https://test.realmgrid.com | https://realm-test-functions.azurewebsites.net |
| acc | https://realm-acc-admin.azurewebsites.net | https://acc.realmgrid.com | https://realm-acc-functions.azurewebsites.net |
| prod | https://realm-prod-admin.azurewebsites.net | https://realmgrid.com | https://realm-prod-functions.azurewebsites.net |

## Reports

Test results are published as:
- HTML report: `reports/index.html`
- JUnit XML: `reports/junit.xml`
- Screenshots on failure: `reports/screenshots/`

## License

Proprietary - RealmGrid 2024
