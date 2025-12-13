# RealmGrid E2E Tests (v1)

End-to-end Playwright tests for the RealmGrid platform.

## Test Coverage

| File | Description | Tests |
|------|-------------|-------|
| `web-app.spec.ts` | Web app flow: homepage, browse, cart, checkout | 6 |
| `api.spec.ts` | API tests: health check, checkout, provisioning | 5 |
| `admin.spec.ts` | Admin dashboard: access, servers, users, CRM | 4 |
| `server-provisioning.spec.ts` | Server lifecycle: provision, start/stop, backup | 14 |
| `subscription.spec.ts` | Subscriptions: checkout, tiers, payment methods | 12 |
| `complete-flow.spec.ts` | Full E2E journey: login → cart → server → subscription | 2 |

**Total: 44 tests**

## File Structure

```
e2e-v1/
├── playwright.config.ts    # Playwright configuration
├── run-tests.sh            # Test runner (starts servers on port 5005)
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── .gitignore              # Ignores node_modules, test-results
└── tests/
    ├── test-config.ts      # Shared config and helpers (161 lines)
    ├── web-app.spec.ts     # Web app tests (230 lines)
    ├── api.spec.ts         # API tests (132 lines)
    ├── admin.spec.ts       # Admin tests (104 lines)
    ├── server-provisioning.spec.ts  # Server tests (181 lines)
    ├── subscription.spec.ts # Subscription tests (155 lines)
    └── complete-flow.spec.ts # E2E flow tests (223 lines)
```

All test files are **under 250 lines** for maintainability.

## Quick Start

```bash
# Run the test script (starts servers automatically on port 5005)
./run-tests.sh

# Or with options:
./run-tests.sh --headed      # Show browser
./run-tests.sh --debug       # Debug mode
./run-tests.sh --ui          # Playwright UI
./run-tests.sh --skip-servers # Use already running servers
```

## Manual Setup

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install chromium

# Run tests (servers must be running)
npx playwright test
```

## Test Options

| Flag | Description |
|------|-------------|
| `--headed` | Show browser window |
| `--debug` | Playwright debug mode |
| `--ui` | Open Playwright UI |
| `--skip-servers` | Don't start servers (use existing) |
| `--api` | Run only API tests |
| `--web` | Run only web app tests |
| `--admin` | Run only admin tests |
| `--flow` | Run only complete E2E flow |
| `--report` | Open HTML report |

## Ports

| Service | Port |
|---------|------|
| Web App | 5005 |
| Azure Functions | 7071 |
| Admin Dashboard | 4321 |

## Debugging

All tests include debug output via:
- `logStep('...')` - Step markers with timestamps
- `debug('...', data)` - Debug info with optional data
- Screenshots saved to `test-results/`
- Videos recorded for all tests
- Traces captured for debugging

### View Test Report

```bash
npx playwright show-report playwright-report
```

### Server Logs

When using `./run-tests.sh`, server logs are saved to:
- `test-results/web-server.log`
- `test-results/functions-server.log`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_URL` | `http://localhost:5005` | Web app URL |
| `FUNCTIONS_URL` | `http://localhost:7071` | Azure Functions URL |
| `ADMIN_URL` | `http://localhost:4321` | Admin dashboard URL |

## Mock Authentication

Tests use mock authentication via `setupMockAuth(page)` which:
1. Sets `realm_auth_token` in localStorage
2. Sets `realm_e2e_test` flag

This simulates a logged-in user without requiring real Microsoft SSO.
