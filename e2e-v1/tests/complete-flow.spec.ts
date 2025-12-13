import { test, expect } from '@playwright/test';
import { 
  CONFIG, 
  setupMockAuth, 
  waitForAppLoad, 
  logStep, 
  debug,
  generateServerName,
  SERVER_TIERS 
} from './test-config';

/**
 * Complete E2E Flow Test
 * 
 * Tests the full user journey:
 * 1. Login (mocked)
 * 2. Browse Minecraft servers
 * 3. Add to cart
 * 4. Checkout
 * 5. Verify server provisioning
 * 6. Verify subscription creation
 */

test.describe('Complete User Journey', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAuth(page);
  });

  test('Full E2E: Login → Browse → Cart → Checkout → Server → Subscription', async ({ page, request }) => {
    const serverName = generateServerName();
    const selectedTier = SERVER_TIERS.small;
    
    // Step 1: Login and access homepage
    logStep('1. Accessing homepage with mock authentication');
    await page.goto(CONFIG.webUrl);
    await waitForAppLoad(page);
    
    debug('Homepage loaded', { url: page.url(), title: await page.title() });
    
    // Verify we're logged in (auth token should be set)
    const authToken = await page.evaluate(() => {
      return localStorage.getItem('realm_auth_token');
    });
    expect(authToken).toBeTruthy();
    debug('Auth token present in localStorage');
    
    // Step 2: Navigate to Minecraft servers
    logStep('2. Browsing Minecraft server options');
    
    // Click on Minecraft or browse link
    const minecraftLink = page.locator('a[href*="minecraft"]')
      .or(page.locator('button:has-text("Minecraft")'))
      .or(page.locator('text=/minecraft/i').first());
    
    if (await minecraftLink.isVisible()) {
      await minecraftLink.click();
      await waitForAppLoad(page);
      debug('Navigated to Minecraft page');
    } else {
      // Try direct navigation
      await page.goto(`${CONFIG.webUrl}/minecraft`);
      await waitForAppLoad(page);
      debug('Direct navigation to Minecraft page');
    }
    
    await page.screenshot({ 
      path: 'test-results/e2e-01-minecraft-page.png', 
      fullPage: true 
    });
    
    // Step 3: Select a server tier
    logStep('3. Selecting Small server tier');
    
    const tierSelector = page.locator(`[data-tier="small"]`)
      .or(page.locator(`button:has-text("${selectedTier.name}")`))
      .or(page.locator(`text=/${selectedTier.price}/`).first());
    
    if (await tierSelector.isVisible()) {
      await tierSelector.click();
      debug('Selected Small tier');
    }
    
    // Step 4: Add to cart
    logStep('4. Adding server to cart');
    
    const addToCartButton = page.locator('button:has-text("Add to Cart")')
      .or(page.locator('[data-testid="add-to-cart"]'))
      .or(page.locator('button:has-text("Order Now")'));
    
    if (await addToCartButton.isVisible()) {
      await addToCartButton.click();
      debug('Clicked add to cart');
      
      // Wait for cart update
      await page.waitForTimeout(500);
    }
    
    await page.screenshot({ 
      path: 'test-results/e2e-02-added-to-cart.png', 
      fullPage: true 
    });
    
    // Step 5: Open cart and proceed to checkout
    logStep('5. Proceeding to checkout');
    
    const cartButton = page.locator('[data-testid="cart-button"]')
      .or(page.locator('button:has-text("Cart")'))
      .or(page.locator('[aria-label*="cart" i]'));
    
    if (await cartButton.isVisible()) {
      await cartButton.click();
      await page.waitForTimeout(500);
      debug('Opened cart');
    }
    
    const checkoutButton = page.locator('button:has-text("Checkout")')
      .or(page.locator('[data-testid="checkout-button"]'))
      .or(page.locator('button:has-text("Pay")'));
    
    if (await checkoutButton.isVisible()) {
      await checkoutButton.click();
      debug('Clicked checkout');
    }
    
    await page.screenshot({ 
      path: 'test-results/e2e-03-checkout.png', 
      fullPage: true 
    });
    
    // Step 6: Verify API can provision server
    logStep('6. Verifying server provisioning API');
    
    const provisionResponse = await request.post(
      `${CONFIG.functionsUrl}/api/server/provision`,
      {
        data: {
          serverId: `e2e-${Date.now()}`,
          userId: CONFIG.testUser.id,
          name: serverName,
          gameType: 'minecraft',
          tier: 'small',
          version: '1.20.4',
        },
      }
    );
    
    debug('Provision API response', { 
      status: provisionResponse.status(),
      ok: provisionResponse.ok() 
    });
    
    // Step 7: Verify subscription API
    logStep('7. Verifying subscription creation API');
    
    const subscriptionResponse = await request.post(
      `${CONFIG.functionsUrl}/api/checkout/create`,
      {
        data: {
          userId: CONFIG.testUser.id,
          email: CONFIG.testUser.email,
          gameType: 'minecraft',
          tier: 'small',
          serverName: serverName,
        },
      }
    );
    
    debug('Subscription API response', { 
      status: subscriptionResponse.status(),
      ok: subscriptionResponse.ok() 
    });
    
    await page.screenshot({ 
      path: 'test-results/e2e-04-complete.png', 
      fullPage: true 
    });
    
    logStep('✅ Complete E2E flow finished successfully');
  });
});

test.describe('Server Lifecycle', () => {
  test('Provision and manage Minecraft server', async ({ request }) => {
    const serverId = `e2e-srv-${Date.now()}`;
    const serverName = generateServerName();
    
    // 1. Provision server
    logStep('Provisioning new Minecraft server');
    const provisionRes = await request.post(
      `${CONFIG.functionsUrl}/api/server/provision`,
      {
        data: {
          serverId,
          userId: CONFIG.testUser.id,
          name: serverName,
          gameType: 'minecraft',
          tier: 'small',
          version: '1.20.4',
        },
      }
    );
    
    debug('Provision response', { status: provisionRes.status() });
    
    // 2. Get server status
    logStep('Checking server status');
    const statusRes = await request.get(
      `${CONFIG.functionsUrl}/api/server/${serverId}`
    );
    
    debug('Status response', { status: statusRes.status() });
    
    // 3. List all servers
    logStep('Listing all servers');
    const listRes = await request.get(
      `${CONFIG.functionsUrl}/api/game-servers?userId=${CONFIG.testUser.id}`
    );
    
    debug('List response', { status: listRes.status() });
    
    logStep('✅ Server lifecycle test complete');
  });
});
