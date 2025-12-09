# Realm Grid E2E Tests - Azure Dev Setup Guide

## Overview

This E2E test suite is now configured to run against your Azure Dev environment:

- **Web App**: `realm-dev-website-wa.azurewebsites.net`
- **Function App**: `realm-dev-api-fa.azurewebsites.net`

From Azure resource IDs:
- `/subscriptions/4a55c776-9f6b-4966-921e-c9f60e50652f/resourceGroups/realm-dta-website-rg/providers/Microsoft.Web/sites/realm-dev-api-fa`
- `/subscriptions/4a55c776-9f6b-4966-921e-c9f60e50652f/resourceGroups/realm-dta-website-rg/providers/Microsoft.Web/sites/realm-dev-website-wa`

## 🎯 Quick Start

### Option 1: Automated Script (Recommended)

```bash
cd /home/falk/realm-grid/realm-e2e-tests

# First time - installs everything and runs tests
./run-tests.sh

# Run specific test suites
./run-tests.sh smoke      # Fast smoke tests
./run-tests.sh auth       # Authentication tests
./run-tests.sh billing    # Billing tests
./run-tests.sh report     # Generate HTML report
```

### Option 2: Manual Commands

```bash
cd /home/falk/realm-grid/realm-e2e-tests

# Activate environment
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt
python3 -m playwright install chromium

# Run tests
behave features/web/
```

## 📋 Configuration Files

### .env - Environment Variables

```env
ENVIRONMENT=dev
WEB_URL=https://realm-dev-website-wa.azurewebsites.net
FUNCTIONS_URL=https://realm-dev-api-fa.azurewebsites.net
ADMIN_URL=https://realm-dev-website-wa.azurewebsites.net
```

**⚠️ IMPORTANT**: Update test credentials in `.env`:

```env
TEST_USER_EMAIL=your-dev-test-email@example.com
TEST_USER_PASSWORD=your-dev-password
ADMIN_USER_EMAIL=your-dev-admin@example.com
ADMIN_USER_PASSWORD=your-dev-admin-password
```

### behave.ini - Test Framework Configuration

Controls how tests are run:
- Default tags: `-@wip -@skip` (excludes work-in-progress and skipped tests)
- Format: Pretty printing with timing info
- Browser: Chromium
- Headless: false (show browser)

### environment.py - Test Lifecycle Hooks

- **before_all**: Initializes Playwright browser
- **before_scenario**: Creates page context and browser instance
- **after_scenario**: Takes screenshots on failure, closes browser
- **after_all**: Cleanup

### run-tests.sh - Test Execution Script

Complete automation script that:
1. Checks dependencies (Python, venv)
2. Creates virtual environment
3. Installs Python packages
4. Installs Playwright browsers
5. Runs tests with proper configuration

## 🧪 Running Tests

### All Tests

```bash
./run-tests.sh
# or
behave features/web/
```

### Specific Feature Files

```bash
# Authentication
behave features/web/authentication.feature

# Dashboard
behave features/web/dashboard.feature

# Browse servers
behave features/web/browse.feature

# Subscriptions
behave features/web/subscription.feature
```

### By Tags

```bash
# Smoke tests (fastest, core functionality)
behave features/web/ --tags=@smoke

# Authentication tests
behave features/web/ --tags=@authentication

# Billing/payment tests
behave features/web/ --tags=@billing

# Visual/theme tests
behave features/web/ --tags=@visual

# Combined tags (AND)
behave features/web/ --tags=@smoke --tags=@authentication

# Excluded tags
behave features/web/ --tags=-@wip,-@skip
```

### Verbose Output

```bash
# Step-by-step output
behave features/web/ -v

# Show all steps
behave features/web/ --steps

# Debug mode
behave features/web/ --debug
```

## 📊 Test Reports

### HTML Report

```bash
./run-tests.sh report
# or
behave features/web/ --format=html --outfile=reports/test-report.html
```

Open `reports/test-report.html` in browser for detailed results.

### JSON Report

```bash
behave features/web/ --format=json --outfile=reports/test-report.json
```

## 🔍 Debugging Tests

### Enable Debug Mode

```bash
# Show browser (not headless)
HEADLESS=false ./run-tests.sh

# Slow motion (1 second between actions)
SLOW_MO=1000 behave features/web/

# Both
HEADLESS=false SLOW_MO=1000 behave features/web/
```

### Verify Azure Resources

```bash
./verify-azure-resources.sh
```

This checks:
- Web app connectivity
- Function app connectivity
- DNS resolution
- HTTP response codes

### Check Specific Step

```bash
# Run single scenario
behave features/web/authentication.feature:5 -v

# Search for undefined steps
behave features/web/ --undefined
```

## 📁 Project Structure

```
realm-e2e-tests/
├── features/
│   ├── web/                          # 23 feature files
│   │   ├── authentication.feature
│   │   ├── dashboard.feature
│   │   ├── browse.feature
│   │   ├── subscription.feature
│   │   └── ... (19 more)
│   ├── admin/                        # Admin tests
│   ├── e2e/                          # End-to-end flows
│   ├── functions/                    # Function app tests
│   └── steps/
│       ├── web_steps.py              # 116 step definitions
│       ├── admin_steps.py
│       ├── functions_steps.py
│       └── e2e_flow_steps.py
├── .env                              # ⚠️ Update credentials here
├── .env.example                      # Template
├── behave.ini                        # Behave configuration
├── environment.py                    # Test setup/teardown
├── requirements.txt                  # Python dependencies
├── run-tests.sh                      # Test runner script
├── verify-azure-resources.sh         # Resource checker
├── TESTING.md                        # Detailed testing guide
└── reports/                          # Generated test reports
    ├── test-report.html
    └── test-report.json
```

## 🛠️ Troubleshooting

### Issue: "Module not found: playwright"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
python3 -m playwright install chromium
```

### Issue: "Connection refused" to Azure resources

**Solution**: Check connectivity
```bash
./verify-azure-resources.sh

# Manual check
curl https://realm-dev-website-wa.azurewebsites.net
curl https://realm-dev-api-fa.azurewebsites.net
```

### Issue: Tests fail with 503/404

**Solution**: Check .env configuration
```bash
cat .env | grep URL
```

Make sure URLs are correct:
- `WEB_URL=https://realm-dev-website-wa.azurewebsites.net`
- `FUNCTIONS_URL=https://realm-dev-api-fa.azurewebsites.net`

### Issue: Authentication fails in tests

**Solution**: Update test credentials in .env
```bash
# Edit .env with valid Azure Dev test users
nano .env
```

### Issue: Virtual environment issues

**Solution**: Recreate venv
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔐 Security

### Credentials Management

Never commit `.env` to git. The file is in `.gitignore`:

```bash
cat .gitignore | grep -E ".env|\.env\.local"
```

### Test User Accounts

Use dedicated test accounts in dev:
- Create test users in Azure AD or your auth provider
- Use non-production accounts
- Store credentials securely (pass to CI/CD via secrets)

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r realm-e2e-tests/requirements.txt
          python3 -m playwright install chromium
      
      - name: Run tests
        env:
          WEB_URL: https://realm-dev-website-wa.azurewebsites.net
          FUNCTIONS_URL: https://realm-dev-api-fa.azurewebsites.net
          TEST_USER_EMAIL: ${{ secrets.DEV_TEST_USER }}
          TEST_USER_PASSWORD: ${{ secrets.DEV_TEST_PASSWORD }}
        run: |
          cd realm-e2e-tests
          behave features/web/
```

## 📞 Support

For issues:

1. **Check configuration**: `cat .env | grep URL`
2. **Verify connectivity**: `./verify-azure-resources.sh`
3. **Run verbose**: `behave features/web/ -v`
4. **Check reports**: View `reports/test-report.html`

## ✨ Next Steps

1. **Update .env** with real test credentials
2. **Verify Azure resources** are online
3. **Run smoke tests**: `./run-tests.sh smoke`
4. **Review results**: Open generated HTML report
5. **Expand testing**: Run full suite `./run-tests.sh`

---

**Framework**: Behave (BDD Python)  
**Browser**: Chromium (Playwright)  
**Target**: Azure Dev Environment  
**Last Updated**: Dec 8, 2025
