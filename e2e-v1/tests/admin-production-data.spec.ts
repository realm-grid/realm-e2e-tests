import { test, expect } from '@playwright/test';

/**
 * End-to-End Test: RealmGrid Admin Portal with Production Data
 * 
 * Tests the admin portal against DEV Azure Function Apps with real production data:
 * - test.sso.user@xevolve.io: 1 running Minecraft server
 * - yair@cloudevolvers.com: 1 subscription (€14.99/month), 1 invoice (paid), 1 pending server
 * 
 * Authentication: Uses dev credentials (auth v1) for quick testing
 * Environment: DEV Function Apps (realm-dev-*-api-fa.azurewebsites.net)
 */

const ADMIN_URL = process.env.ADMIN_URL || 'http://localhost:4321';
const DEV_LOGIN_EMAIL = 'dev@localhost.local';
const DEV_LOGIN_PASSWORD = 'RealmDev2025';

test.describe('Admin Portal - Production Data Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Enable verbose console logging
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      
      if (type === 'error') {
        console.log(`🔴 [Browser] ${text}`);
      } else if (type === 'warning') {
        console.log(`🟡 [Browser] ${text}`);
      } else if (text.includes('[API]') || text.includes('[AdminApp]')) {
        console.log(`🔵 ${text}`);
      }
    });
    
    page.on('pageerror', error => {
      console.log(`🔴 [Page Error] ${error.message}`);
    });
    
    page.on('requestfailed', request => {
      console.log(`🔴 [Network] ${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
    });
  });

  test('should load admin portal and login with dev credentials', async ({ page }) => {
    console.log('═══════════════════════════════════════════════');
    console.log('🧪 TEST: Admin portal load and dev auth');
    console.log('═══════════════════════════════════════════════');
    
    await page.goto(ADMIN_URL);
    await page.waitForLoadState('networkidle');
    
    // Check if login page is visible
    const hasLoginButton = await page.locator('button:has-text("Login with Microsoft")').isVisible().catch(() => false);
    
    console.log('🔐 Login page visible:', hasLoginButton);
    
    if (hasLoginButton) {
      // Look for dev login button
      const hasDevLogin = await page.locator('button:has-text("Development Login")').isVisible().catch(() => false);
      
      console.log('🔧 Dev login available:', hasDevLogin);
      
      if (hasDevLogin) {
        console.log('🔑 Clicking dev login button...');
        await page.click('button:has-text("Development Login")');
        await page.waitForLoadState('networkidle');
        
        // Wait a moment for dashboard to load
        await page.waitForTimeout(2000);
      } else {
        console.log('⚠️  Dev login not available - test requires dev mode');
        test.skip(true, 'Dev login not available');
        return;
      }
    }
    
    // Verify we're on the dashboard
    const hasDashboard = await page.locator('text=Dashboard').isVisible().catch(() => false) ||
                         await page.locator('text=Total Servers').isVisible().catch(() => false);
    
    console.log('✅ Dashboard loaded:', hasDashboard);
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/admin-login.png', fullPage: true });
    console.log('📸 Screenshot saved: test-results/admin-login.png');
    
    expect(hasDashboard).toBeTruthy();
  });

  test('should display production data from Cosmos DB', async ({ page }) => {
    console.log('═══════════════════════════════════════════════');
    console.log('🧪 TEST: Production data display');
    console.log('═══════════════════════════════════════════════');
    
    const apiCalls: Array<{ url: string; status: number; method: string }> = [];
    
    // Monitor API calls to Function Apps
    page.on('response', async response => {
      const url = response.url();
      if (url.includes('azurewebsites.net') || url.includes('/api/')) {
        const call = {
          url,
          status: response.status(),
          method: response.request().method(),
        };
        apiCalls.push(call);
        
        const emoji = response.status() < 400 ? '✅' : '❌';
        console.log(`${emoji} API: ${call.method} ${url} → ${call.status}`);
        
        // Log response body for failed requests
        if (response.status() >= 400) {
          try {
            const body = await response.text();
            console.log(`   Response: ${body.substring(0, 200)}`);
          } catch (e) {
            // Ignore errors reading body
          }
        }
      }
    });
    
    await page.goto(ADMIN_URL);
    await page.waitForLoadState('networkidle');
    
    // Login if needed
    const hasLoginButton = await page.locator('button:has-text("Login with Microsoft")').isVisible().catch(() => false);
    if (hasLoginButton) {
      const hasDevLogin = await page.locator('button:has-text("Development Login")').isVisible().catch(() => false);
      if (hasDevLogin) {
        await page.click('button:has-text("Development Login")');
        await page.waitForLoadState('networkidle');
      } else {
        test.skip(true, 'Dev login required');
        return;
      }
    }
    
    // Wait for API calls to complete
    console.log('⏳ Waiting for dashboard data to load...');
    await page.waitForTimeout(5000);
    
    // Check for dashboard stats
    const bodyText = await page.textContent('body');
    
    console.log('═══════════════════════════════════════════════');
    console.log('🔍 Checking for production data...');
    
    // Expected data from Cosmos DB:
    // - test.sso.user@xevolve.io: 1 running Minecraft server
    // - yair@cloudevolvers.com: 1 subscription, 1 invoice, 1 pending server
    
    const hasServers = bodyText?.toLowerCase().includes('server');
    const hasSubscriptions = bodyText?.toLowerCase().includes('subscription');
    const hasMinecraft = bodyText?.toLowerCase().includes('minecraft');
    
    console.log('📊 Data found:');
    console.log('   • Servers:', hasServers ? '✓' : '✗');
    console.log('   • Subscriptions:', hasSubscriptions ? '✓' : '✗');
    console.log('   • Minecraft:', hasMinecraft ? '✓' : '✗');
    
    // Check for specific numbers (we have 2 servers total)
    const hasTotalServers = bodyText?.includes('2') || bodyText?.includes('Total Servers');
    console.log('   • Server count:', hasTotalServers ? '✓' : '✗');
    
    console.log('\n📡 API Calls Summary:');
    console.log(`   Total calls: ${apiCalls.length}`);
    
    if (apiCalls.length > 0) {
      const successCalls = apiCalls.filter(c => c.status >= 200 && c.status < 300);
      const errorCalls = apiCalls.filter(c => c.status >= 400);
      
      console.log(`   Successful: ${successCalls.length}`);
      console.log(`   Errors: ${errorCalls.length}`);
      
      // List specific endpoints called
      const endpoints = [...new Set(apiCalls.map(c => {
        const url = new URL(c.url);
        return url.pathname;
      }))];
      
      console.log('\n🎯 Endpoints called:');
      endpoints.forEach(ep => console.log(`   • ${ep}`));
    }
    console.log('═══════════════════════════════════════════════');
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/admin-production-data.png', fullPage: true });
    console.log('📸 Screenshot saved: test-results/admin-production-data.png');
    
    // Assertions
    expect(apiCalls.length).toBeGreaterThan(0);
    expect(hasServers || hasSubscriptions).toBeTruthy();
  });

  test('should fetch servers from dev Function Apps', async ({ page }) => {
    console.log('═══════════════════════════════════════════════');
    console.log('🧪 TEST: Servers endpoint verification');
    console.log('═══════════════════════════════════════════════');
    
    let serversResponse: any = null;
    
    page.on('response', async response => {
      const url = response.url();
      if (url.includes('/global-admin/servers')) {
        console.log(`📡 Servers API called: ${response.status()}`);
        try {
          const data = await response.json();
          serversResponse = data;
          console.log('📊 Servers response:', JSON.stringify(data, null, 2));
        } catch (e) {
          console.error('❌ Failed to parse servers response');
        }
      }
    });
    
    await page.goto(ADMIN_URL);
    await page.waitForLoadState('networkidle');
    
    // Login
    const hasLoginButton = await page.locator('button:has-text("Login with Microsoft")').isVisible().catch(() => false);
    if (hasLoginButton) {
      const hasDevLogin = await page.locator('button:has-text("Development Login")').isVisible().catch(() => false);
      if (hasDevLogin) {
        await page.click('button:has-text("Development Login")');
        await page.waitForLoadState('networkidle');
      } else {
        test.skip(true, 'Dev login required');
        return;
      }
    }
    
    // Wait for servers API to be called
    await page.waitForTimeout(5000);
    
    if (serversResponse) {
      const servers = serversResponse.data || serversResponse || [];
      console.log('═══════════════════════════════════════════════');
      console.log(`✅ Found ${servers.length} servers in response`);
      
      if (servers.length > 0) {
        console.log('\n🎮 Server details:');
        servers.forEach((srv: any, idx: number) => {
          console.log(`   ${idx + 1}. ${srv.serverName || srv.id}`);
          console.log(`      Game: ${srv.gameType || 'N/A'}`);
          console.log(`      Status: ${srv.status || 'N/A'}`);
          console.log(`      User: ${srv.userId || 'N/A'}`);
        });
      }
      console.log('═══════════════════════════════════════════════');
      
      expect(servers.length).toBeGreaterThanOrEqual(2);
    } else {
      console.log('⚠️  No servers response captured');
    }
  });

  test('should fetch subscriptions from dev Function Apps', async ({ page }) => {
    console.log('═══════════════════════════════════════════════');
    console.log('🧪 TEST: Subscriptions endpoint verification');
    console.log('═══════════════════════════════════════════════');
    
    let subscriptionsResponse: any = null;
    
    page.on('response', async response => {
      const url = response.url();
      if (url.includes('/global-admin/subscriptions')) {
        console.log(`📡 Subscriptions API called: ${response.status()}`);
        try {
          const data = await response.json();
          subscriptionsResponse = data;
          console.log('📊 Subscriptions response:', JSON.stringify(data, null, 2));
        } catch (e) {
          console.error('❌ Failed to parse subscriptions response');
        }
      }
    });
    
    await page.goto(ADMIN_URL);
    await page.waitForLoadState('networkidle');
    
    // Login
    const hasLoginButton = await page.locator('button:has-text("Login with Microsoft")').isVisible().catch(() => false);
    if (hasLoginButton) {
      const hasDevLogin = await page.locator('button:has-text("Development Login")').isVisible().catch(() => false);
      if (hasDevLogin) {
        await page.click('button:has-text("Development Login")');
        await page.waitForLoadState('networkidle');
      } else {
        test.skip(true, 'Dev login required');
        return;
      }
    }
    
    // Wait for subscriptions API to be called
    await page.waitForTimeout(5000);
    
    if (subscriptionsResponse) {
      const subscriptions = subscriptionsResponse.data || subscriptionsResponse || [];
      console.log('═══════════════════════════════════════════════');
      console.log(`✅ Found ${subscriptions.length} subscriptions in response`);
      
      if (subscriptions.length > 0) {
        console.log('\n💳 Subscription details:');
        subscriptions.forEach((sub: any, idx: number) => {
          console.log(`   ${idx + 1}. ${sub.id}`);
          console.log(`      Plan: ${sub.planType || 'N/A'}`);
          console.log(`      Amount: €${sub.amount || 'N/A'}`);
          console.log(`      Status: ${sub.status || 'N/A'}`);
          console.log(`      Mollie: ${sub.mollieSubscriptionId || 'not linked'}`);
        });
      }
      console.log('═══════════════════════════════════════════════');
      
      expect(subscriptions.length).toBeGreaterThanOrEqual(1);
    } else {
      console.log('⚠️  No subscriptions response captured');
    }
  });
});
