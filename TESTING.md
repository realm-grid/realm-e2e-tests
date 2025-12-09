# Realm Grid E2E Tests - Quick Start Guide

## ✅ Setup Configuration for Dev Azure Resources

Your tests are now configured to run against:
- **Web App**: `realm-dev-website-wa.azurewebsites.net`
- **Function App**: `realm-dev-api-fa.azurewebsites.net`

## 🚀 Quick Start

### 1. First Time Setup

```bash
cd /home/falk/realm-grid/realm-e2e-tests
./run-tests.sh
```

This will:
- Check Python installation
- Create virtual environment
- Install all dependencies
- Run all web tests against dev environment

### 2. Run Tests by Category

```bash
# Run smoke tests only (fastest)
./run-tests.sh smoke

# Run authentication tests
./run-tests.sh auth

# Run billing tests
./run-tests.sh billing

# Generate HTML report
./run-tests.sh report
```

### 3. Direct Behave Commands

```bash
# Activate venv first (if not using the script)
source venv/bin/activate

# Run all web tests
behave features/web/

# Run specific feature file
behave features/web/authentication.feature

# Run with specific tags
behave features/web/ --tags=@smoke
behave features/web/ --tags=@authentication
behave features/web/ --tags=@billing

# Run with verbose output
behave features/web/ -v

# Generate HTML report
behave features/web/ --format=html --outfile=reports/test-report.html

# Generate JSON report
behave features/web/ --format=json --outfile=reports/test-report.json
```

## 📋 Configuration

### Environment Variables (.env)

The `.env` file contains:
- **WEB_URL**: https://realm-dev-website-wa.azurewebsites.net
- **FUNCTIONS_URL**: https://realm-dev-api-fa.azurewebsites.net
- **ADMIN_URL**: https://realm-dev-website-wa.azurewebsites.net
- **Test Credentials**: Email/password for login tests
- **Payment Test Cards**: Stripe test card details
- **Browser Settings**: Chrome/headless configuration

### Update Credentials

Edit `.env` to add real test user credentials:

```env
TEST_USER_EMAIL=your-test-user@example.com
TEST_USER_PASSWORD=your-test-password
ADMIN_USER_EMAIL=your-admin-user@example.com
ADMIN_USER_PASSWORD=your-admin-password
```

### Update Function Keys (if needed)

```env
PROVISION_VM_KEY=your-actual-function-key
CREATE_SUBSCRIPTION_KEY=your-actual-function-key
DEPLOY_SERVER_KEY=your-actual-function-key
```

## 📊 Test Categories

### Available Feature Files (23 total)

| Feature | File | Tags | Purpose |
|---------|------|------|---------|
| Authentication | `authentication.feature` | @authentication, @login, @oauth | Login, OAuth, sessions |
| Dashboard | `dashboard.feature` | @dashboard | User dashboard functionality |
| Browse | `browse.feature` | @browse | Server browsing & search |
| Subscription | `subscription.feature` | @billing, @subscription | Billing & plan management |
| Home | `home.feature` | @home | Marketing home page |
| Contact | `contact.feature` | @contact | Contact form |
| Admin | `admin.feature` | @admin | Admin features |
| And 16 more... | `*.feature` | Various | Full test coverage |

### Run Tests by Feature

```bash
# Authentication tests
behave features/web/authentication.feature

# Dashboard tests
behave features/web/dashboard.feature

# Browse & search tests
behave features/web/browse.feature

# Subscription & billing tests
behave features/web/subscription.feature
```

## 🔍 Monitoring & Debugging

### View Test Output

```bash
# Pretty format (default)
behave features/web/

# Verbose output
behave features/web/ -v

# Show undefined steps
behave features/web/ --undefined

# Step-by-step execution
behave features/web/ --steps
```

### Enable Playwright Debug

```bash
# Run with slow motion (1 second delay between actions)
SLOW_MO=1000 behave features/web/

# Run in headed mode (not headless)
HEADLESS=false behave features/web/
```

## 📈 Reports

### HTML Report

```bash
./run-tests.sh report
# or
behave features/web/ --format=html --outfile=reports/test-report.html
```

Open `reports/test-report.html` in your browser to view detailed test results.

### JSON Report

```bash
behave features/web/ --format=json --outfile=reports/test-report.json
```

## 🛠️ Troubleshooting

### Tests Fail to Connect

1. Verify Azure resources are running:
   ```bash
   curl https://realm-dev-website-wa.azurewebsites.net
   curl https://realm-dev-api-fa.azurewebsites.net
   ```

2. Check `.env` URLs are correct:
   ```bash
   cat .env | grep URL
   ```

### Playwright Issues

```bash
# Reinstall Playwright browsers
python3 -m playwright install

# Clear Playwright cache
rm -rf ~/Library/Caches/ms-playwright
```

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📁 Project Structure

```
realm-e2e-tests/
├── features/
│   ├── web/                    # 23 feature files
│   ├── admin/                  # Admin tests
│   ├── e2e/                    # End-to-end flows
│   ├── functions/              # Function app tests
│   └── steps/
│       ├── web_steps.py        # 116 step definitions
│       ├── admin_steps.py
│       ├── functions_steps.py
│       └── e2e_flow_steps.py
├── .env                        # Configuration (created)
├── behave.ini                  # Behave configuration
├── environment.py              # Test setup/teardown
├── requirements.txt            # Python dependencies
├── run-tests.sh               # Test runner script
└── reports/                   # Test reports (generated)
```

## 🎯 Next Steps

1. **First run**: `./run-tests.sh smoke`
2. **Update credentials**: Edit `.env` with real test users
3. **Run full suite**: `./run-tests.sh`
4. **View results**: `./run-tests.sh report`

## 📞 Support

For issues:
1. Check `.env` configuration
2. Verify Azure resources are accessible
3. Run tests with verbose output: `behave features/web/ -v`
4. Check `reports/` for detailed test output

---

**Test Framework**: Behave (BDD for Python)
**Browser**: Chromium (via Playwright)
**Target**: Azure Dev Environment
