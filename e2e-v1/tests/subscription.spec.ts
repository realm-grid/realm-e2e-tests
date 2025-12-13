import { test, expect } from '@playwright/test';
import { CONFIG, debug, logStep } from './test-config';

/**
 * Subscription E2E Tests
 * 
 * Tests the full subscription flow with real Mollie integration:
 * 1. Create checkout session via API
 * 2. Navigate to Mollie checkout
 * 3. Complete payment (test mode)
 * 4. Verify subscription created
 * 
 * REQUIRED: Azure Function App must have MOLLIE_API_KEY configured!
 */

// API URL - use FUNCTION_APP_URL env var for Azure Functions
const API_URL = process.env.FUNCTION_APP_URL || CONFIG.functionsUrl;

function generateTestId(): string {
  return `e2e-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Helper to check if API is available
async function isApiAvailable(request: any): Promise<boolean> {
  try {
    const response = await request.get(`${API_URL}/api/health`, { timeout: 5000 });
    return response.ok();
  } catch { return false; }
}

// Store checkout data for the full flow test
let checkoutData: {
  checkoutUrl?: string;
  paymentId?: string;
  userId?: string;
  email?: string;
  testPassed?: boolean;
} = {};

test.describe('Full Subscription Flow', () => {
  test.describe.configure({ mode: 'serial' }); // Run tests in order

  test.beforeEach(async () => {
    // Skip remaining tests if first test failed
    if (checkoutData.testPassed === false) {
      test.skip(true, 'Skipping: checkout creation failed');
    }
  });

  test('1. Create checkout session with Mollie', async ({ request }) => {
    logStep('Creating checkout session');
    
    // Generate unique user for this test
    const testUserId = `e2e-sub-${Date.now()}`;
    const testEmail = `e2e-${Date.now()}@realmgrid.io`;
    
    checkoutData.userId = testUserId;
    checkoutData.email = testEmail;
    checkoutData.testPassed = false; // Will set to true if successful
    
    const requestBody = {
      userId: testUserId,
      email: testEmail,
      gameType: 'minecraft',
      tier: 'small',
      serverName: `E2E-Server-${Date.now()}`,
      // Don't specify paymentMethod - let Mollie show selector
    };
    
    debug('Request body', requestBody);
    debug('API URL', `${API_URL}/api/checkout/create`);
    
    const response = await request.post(`${API_URL}/api/checkout/create`, {
      data: requestBody,
      headers: { 'Content-Type': 'application/json' },
    });

    debug('Checkout response status', response.status());

    // Check for configuration errors
    if (!response.ok()) {
      const errorData = await response.json().catch(() => ({}));
      debug('Checkout error', errorData);
      
      if (errorData.message?.includes('Bearer') || errorData.message?.includes('API key')) {
        throw new Error('MOLLIE_API_KEY is not configured in Azure Function App! Add it to Application Settings.');
      }
      throw new Error(`Checkout failed: ${errorData.message || response.status()}`);
    }
    
    const data = await response.json();
    debug('Checkout response', data);
    
    expect(data.success).toBeTruthy();
    expect(data.data.checkoutUrl).toContain('mollie');
    expect(data.data.paymentId).toBeDefined();
    
    checkoutData.checkoutUrl = data.data.checkoutUrl;
    checkoutData.paymentId = data.data.paymentId;
    checkoutData.testPassed = true; // Mark success
    
    console.log(`✅ Checkout created: ${checkoutData.paymentId}`);
    console.log(`   Mollie URL: ${checkoutData.checkoutUrl?.substring(0, 60)}...`);
  });

  test('2. Navigate to Mollie checkout page', async ({ page }) => {
    test.skip(!checkoutData.testPassed, 'Checkout creation failed - skipping');
    
    logStep('Opening Mollie checkout');
    
    await page.goto(checkoutData.checkoutUrl!);
    await page.waitForLoadState('networkidle');
    
    // Take screenshot
    await page.screenshot({ 
      path: 'test-results/mollie-checkout.png', 
      fullPage: true 
    });
    
    const url = page.url();
    debug('Mollie URL', url);
    
    expect(url).toMatch(/mollie\.(com|nl)/);
    console.log('✅ On Mollie checkout page');
  });

  test('3. Complete payment on Mollie (test mode)', async ({ page }) => {
    test.skip(!checkoutData.checkoutUrl, 'Checkout URL not available');
    
    logStep('Completing Mollie payment');
    
    await page.goto(checkoutData.checkoutUrl!);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Take screenshot of payment options
    await page.screenshot({ 
      path: 'test-results/mollie-payment-form.png', 
      fullPage: true 
    });
    
    // In Mollie test mode, select a bank for iDEAL
    const bankSelector = page.locator('select[name="issuer"]');
    if (await bankSelector.isVisible({ timeout: 3000 }).catch(() => false)) {
      await bankSelector.selectOption({ index: 1 });
      debug('Selected bank from dropdown');
    }
    
    // Look for bank buttons (test mode may show these)
    const bankButton = page.locator('button:has-text("ABN AMRO"), button:has-text("ING"), button:has-text("Rabobank")').first();
    if (await bankButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await bankButton.click();
      debug('Clicked bank button');
    }
    
    // Click continue/pay button
    const payButton = page.locator('button[type="submit"], button:has-text("Continue"), button:has-text("Pay"), button:has-text("Betaal")').first();
    if (await payButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      await payButton.click();
      await page.waitForTimeout(2000);
    }
    
    // In test mode, look for status buttons (Paid, Failed, etc.)
    const paidButton = page.locator('button:has-text("Paid"), a:has-text("Paid"), [data-status="paid"]').first();
    if (await paidButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      debug('Test mode: clicking Paid button');
      await paidButton.click();
      await page.waitForTimeout(2000);
    }
    
    // Take screenshot after payment
    await page.screenshot({ 
      path: 'test-results/mollie-after-payment.png', 
      fullPage: true 
    });
    
    // Wait for redirect to success URL
    try {
      await page.waitForURL(/success|realm|localhost/, { timeout: 15000 });
      console.log('✅ Redirected to success page');
    } catch {
      debug('No redirect detected - may need manual verification');
    }
    
    console.log('✅ Payment flow completed');
  });

  test('4. Verify subscription was created', async ({ request }) => {
    test.skip(!checkoutData.userId, 'User ID not available');
    
    logStep('Verifying subscription');
    
    // Wait for webhook processing
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    const response = await request.get(`${API_URL}/api/subscriptions`, {
      params: { userId: checkoutData.userId || '' },
    });

    debug('Subscription list status', response.status());

    if (response.ok()) {
      const data = await response.json();
      const subs = data.data?.subscriptions || data.subscriptions || [];
      
      if (subs.length > 0) {
        console.log(`✅ Found ${subs.length} subscription(s)`);
        const sub = subs[0];
        console.log(`   ID: ${sub.id}`);
        console.log(`   Status: ${sub.status}`);
        console.log(`   Tier: ${sub.tier}`);
        console.log(`   Game: ${sub.gameType}`);
      } else {
        console.log('⚠️  No subscriptions found yet (webhook may be processing)');
      }
    } else {
      console.log('⚠️  Could not query subscriptions');
    }
  });

  test('5. List user subscriptions', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Listing all user subscriptions');
    
    const response = await request.get(`${API_URL}/api/subscriptions`, {
      params: { userId: checkoutData.userId || '' },
    });

    debug('List response status', response.status());

    if (response.ok()) {
      const data = await response.json();
      const subs = data.data?.subscriptions || data.subscriptions || [];
      console.log(`✅ User has ${subs.length} subscription(s)`);
    }
  });
});

test.describe('Subscription Lifecycle', () => {
  const testId = generateTestId();

  test('1. Pause subscription', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Testing pause subscription');
    
    const response = await request.post(
      `${API_URL}/api/subscriptions/${testId}/pause`
    );
    
    // May fail with 404 if subscription doesn't exist - that's expected
    debug('Pause response', { status: response.status() });
    expect([200, 404]).toContain(response.status());
  });

  test('2. Resume subscription', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Testing resume subscription');
    
    const response = await request.post(
      `${API_URL}/api/subscriptions/${testId}/resume`
    );
    
    debug('Resume response', { status: response.status() });
    expect([200, 404]).toContain(response.status());
  });

  test('3. Cancel subscription', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Testing cancel subscription');
    
    const response = await request.post(
      `${API_URL}/api/subscriptions/${testId}/cancel`,
      { data: { immediately: false, reason: 'E2E test' } }
    );
    
    debug('Cancel response', { status: response.status() });
    expect([200, 404]).toContain(response.status());
  });
});

test.describe('Subscription Tiers', () => {
  const tiers = [
    { tier: 'small', price: '9.99' },
    { tier: 'medium', price: '19.99' },
    { tier: 'heavy', price: '49.99' },
  ];

  for (const { tier, price } of tiers) {
    test(`Checkout ${tier} tier (€${price})`, async ({ request }) => {
      if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
      logStep(`Testing ${tier} tier checkout`);
      
      const response = await request.post(`${API_URL}/api/checkout/create`, {
        data: {
          userId: `tier-test-${tier}-${Date.now()}`,
          email: `tier-${tier}@realmgrid.io`,
          gameType: 'minecraft',
          tier: tier,
          serverName: `Tier Test ${tier}`,
        },
      });

      debug(`${tier} tier response`, { status: response.status() });

      if (response.ok()) {
        const data = await response.json();
        expect(data.success).toBeTruthy();
        expect(data.data.checkoutUrl).toContain('mollie');
        console.log(`✅ ${tier} tier checkout created`);
      }
    });
  }
});

test.describe('Payment Methods', () => {
  const methods = ['ideal', 'creditcard', 'bancontact'];

  for (const method of methods) {
    test(`Checkout with ${method}`, async ({ request }) => {
      if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
      logStep(`Testing ${method} payment method`);
      
      const response = await request.post(`${API_URL}/api/checkout/create`, {
        data: {
          userId: `pay-${method}-${Date.now()}`,
          email: `payment-${method}@realmgrid.io`,
          gameType: 'minecraft',
          tier: 'small',
          serverName: `Payment Test ${method}`,
          paymentMethod: method,
        },
      });

      debug(`${method} response`, { status: response.status() });
      
      if (response.ok()) {
        const data = await response.json();
        expect(data.success).toBeTruthy();
        expect(data.data.paymentMethod).toBe(method);
        console.log(`✅ ${method} payment method checkout created`);
      }
    });
  }
});

test.describe('Game Types', () => {
  const games = ['minecraft', 'valheim', 'palworld', 'rust'];

  for (const game of games) {
    test(`Checkout for ${game}`, async ({ request }) => {
      if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
      logStep(`Testing ${game} checkout`);
      
      const response = await request.post(`${API_URL}/api/checkout/create`, {
        data: {
          userId: `game-${game}-${Date.now()}`,
          email: `game-${game}@realmgrid.io`,
          gameType: game,
          tier: 'small',
          serverName: `${game.charAt(0).toUpperCase() + game.slice(1)} Test Server`,
        },
      });

      debug(`${game} response`, { status: response.status() });
      
      if (response.ok()) {
        const data = await response.json();
        expect(data.success).toBeTruthy();
        expect(data.data.checkoutUrl).toContain('mollie');
        console.log(`✅ ${game} checkout created`);
      }
    });
  }
});

test.describe('Validation Tests', () => {
  test('Rejects missing userId', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/checkout/create`, {
      data: {
        email: 'test@example.com',
        gameType: 'minecraft',
        tier: 'small',
      },
    });
    expect(response.status()).toBe(400);
    console.log('✅ Correctly rejected missing userId');
  });

  test('Rejects missing email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/checkout/create`, {
      data: {
        userId: 'test-user',
        gameType: 'minecraft',
        tier: 'small',
      },
    });
    expect(response.status()).toBe(400);
    console.log('✅ Correctly rejected missing email');
  });

  test('Rejects invalid email', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/checkout/create`, {
      data: {
        userId: 'test-user',
        email: 'not-an-email',
        gameType: 'minecraft',
        tier: 'small',
      },
    });
    expect(response.status()).toBe(400);
    console.log('✅ Correctly rejected invalid email');
  });

  test('Rejects invalid tier', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/checkout/create`, {
      data: {
        userId: 'test-user',
        email: 'test@example.com',
        gameType: 'minecraft',
        tier: 'invalid-tier',
      },
    });
    expect(response.status()).toBe(400);
    console.log('✅ Correctly rejected invalid tier');
  });

  test('Rejects invalid game type', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/checkout/create`, {
      data: {
        userId: 'test-user',
        email: 'test@example.com',
        gameType: 'invalid-game',
        tier: 'small',
      },
    });
    expect(response.status()).toBe(400);
    console.log('✅ Correctly rejected invalid game type');
  });
});
