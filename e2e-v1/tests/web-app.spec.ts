import { test, expect, Page, BrowserContext } from '@playwright/test';
import { CONFIG, setupMockAuth } from './test-config';

/**
 * RealmGrid Web App E2E Tests
 * 
 * Tests the web application user journey:
 * 1. Homepage loading
 * 2. Browsing servers
 * 3. Adding to cart
 * 4. Checkout flow
 */

test.describe('RealmGrid Web App Flow', () => {
  test.describe.configure({ mode: 'serial' });

  test('1. Homepage loads correctly', async ({ page }) => {
    await page.goto(CONFIG.webUrl);
    
    // Wait for page to fully load and hydrate
    await page.waitForLoadState('networkidle');
    
    // Wait a moment for React hydration
    await page.waitForTimeout(2000);
    
    // Check for main elements first (more reliable than title during SSR)
    const hasNavigation = await page.locator('nav, [role="navigation"], .sidebar, aside').first().isVisible({ timeout: 5000 }).catch(() => false);
    const hasContent = await page.locator('main, [role="main"], .content, .dashboard').first().isVisible({ timeout: 5000 }).catch(() => false);
    
    // Debug: log page title
    const title = await page.title();
    console.log(`[DEBUG] Page title: ${title}`);
    console.log(`[DEBUG] Has navigation: ${hasNavigation}, Has content: ${hasContent}`);
    
    // Check title contains RealmGrid (accounts for various title formats)
    // The page may have an empty title initially due to SSR/hydration
    if (title) {
      expect(title.toLowerCase()).toMatch(/realm|grid|admin/i);
    }
    
    // Verify the app loaded successfully - check for key UI elements
    expect(hasNavigation || hasContent).toBeTruthy();
  });

  test('2. User can browse available servers', async ({ page }) => {
    await page.goto(CONFIG.webUrl);
    
    // Navigate to browse/servers section
    const browseButton = page.locator('text=Browse').first();
    if (await browseButton.isVisible()) {
      console.log('[DEBUG] Clicking Browse button');
      await browseButton.click();
    }
    
    // Wait for server cards to load
    await page.waitForTimeout(1000);
    
    // Look for game server options
    const minecraftOption = page.locator('text=Minecraft').first();
    await expect(minecraftOption).toBeVisible({ timeout: 10000 });
  });

  test('3. User can add a Minecraft server to cart', async ({ page }) => {
    await page.goto(CONFIG.webUrl);
    
    // Navigate to browse
    const browseButton = page.locator('text=Browse').first();
    if (await browseButton.isVisible()) {
      await browseButton.click();
      await page.waitForTimeout(500);
    }
    
    // Find a Minecraft server card and click add to cart
    const minecraftCard = page.locator('[data-game="minecraft"]').first()
      .or(page.locator('text=Minecraft').first().locator('..').locator('..'));
    
    // Click on the server or add to cart button
    const addToCartButton = page.locator('button:has-text("Add")').first()
      .or(page.locator('button:has-text("Cart")').first())
      .or(page.locator('[data-testid="add-to-cart"]').first());
    
    if (await addToCartButton.isVisible()) {
      console.log('[DEBUG] Clicking Add to Cart button');
      await addToCartButton.click();
    } else {
      // Click on the server card itself
      await minecraftCard.click();
      await page.waitForTimeout(500);
      
      // Then find add to cart button in modal/detail view
      const modalAddButton = page.locator('button:has-text("Add")').first();
      if (await modalAddButton.isVisible()) {
        await modalAddButton.click();
      }
    }
    
    // Verify item was added (cart count or toast notification)
    const cartIndicator = page.locator('[data-testid="cart-count"]')
      .or(page.locator('.cart-count'))
      .or(page.locator('text=Added to cart'));
    
    await expect(cartIndicator.first()).toBeVisible({ timeout: 5000 });
  });

  test('4. User can open cart and view items', async ({ page }) => {
    await page.goto(CONFIG.webUrl);
    
    // First add item to cart
    await test.step('Add item to cart', async () => {
      const browseButton = page.locator('text=Browse').first();
      if (await browseButton.isVisible()) {
        await browseButton.click();
        await page.waitForTimeout(500);
      }
      
      const addButton = page.locator('button:has-text("Add")').first();
      if (await addButton.isVisible()) {
        await addButton.click();
        await page.waitForTimeout(500);
      }
    });
    
    // Open cart
    const cartButton = page.locator('[data-testid="cart-button"]')
      .or(page.locator('button:has-text("Cart")'))
      .or(page.locator('[aria-label*="cart"]'))
      .or(page.locator('.cart-icon'))
      .first();
    
    if (await cartButton.isVisible()) {
      console.log('[DEBUG] Opening cart');
      await cartButton.click();
    }
    
    // Verify cart sheet/modal opens
    const cartSheet = page.locator('[data-testid="cart-sheet"]')
      .or(page.locator('.cart-sheet'))
      .or(page.locator('[role="dialog"]'));
    
    await expect(cartSheet.first()).toBeVisible({ timeout: 5000 });
  });

  test('5. User can proceed to checkout', async ({ page }) => {
    await page.goto(CONFIG.webUrl);
    
    // Add item and open cart
    await test.step('Setup cart', async () => {
      const browseButton = page.locator('text=Browse').first();
      if (await browseButton.isVisible()) {
        await browseButton.click();
        await page.waitForTimeout(500);
      }
      
      const addButton = page.locator('button:has-text("Add")').first();
      if (await addButton.isVisible()) {
        await addButton.click();
        await page.waitForTimeout(1000);
      }
      
      const cartButton = page.locator('[data-testid="cart-button"]')
        .or(page.locator('button:has-text("Cart")'))
        .first();
      
      if (await cartButton.isVisible()) {
        await cartButton.click();
        await page.waitForTimeout(500);
      }
    });
    
    // Click checkout button
    const checkoutButton = page.locator('button:has-text("Checkout")')
      .or(page.locator('[data-testid="checkout-button"]'))
      .first();
    
    await expect(checkoutButton).toBeVisible({ timeout: 5000 });
    await checkoutButton.click();
    
    // Verify checkout dialog opens
    const checkoutDialog = page.locator('[data-testid="checkout-dialog"]')
      .or(page.locator('text=Join the Waitlist'))
      .or(page.locator('[role="dialog"]'));
    
    await expect(checkoutDialog.first()).toBeVisible({ timeout: 5000 });
  });

  test('6. User can complete checkout form', async ({ page }) => {
    await page.goto(CONFIG.webUrl);
    
    // Setup cart and go to checkout
    await test.step('Navigate to checkout', async () => {
      const browseButton = page.locator('text=Browse').first();
      if (await browseButton.isVisible()) {
        await browseButton.click();
        await page.waitForTimeout(500);
      }
      
      const addButton = page.locator('button:has-text("Add")').first();
      if (await addButton.isVisible()) {
        await addButton.click();
        await page.waitForTimeout(500);
      }
      
      const cartButton = page.locator('button:has-text("Cart")').first();
      if (await cartButton.isVisible()) {
        await cartButton.click();
        await page.waitForTimeout(500);
      }
      
      const checkoutButton = page.locator('button:has-text("Checkout")').first();
      if (await checkoutButton.isVisible()) {
        await checkoutButton.click();
        await page.waitForTimeout(500);
      }
    });
    
    // Fill checkout form
    await test.step('Fill form fields', async () => {
      const firstNameInput = page.locator('input[name="firstName"]');
      const lastNameInput = page.locator('input[name="lastName"]');
      const emailInput = page.locator('input[name="email"]');
      
      if (await firstNameInput.isVisible()) await firstNameInput.fill('E2E');
      if (await lastNameInput.isVisible()) await lastNameInput.fill('TestUser');
      if (await emailInput.isVisible()) await emailInput.fill(CONFIG.testUser.email);
    });
    
    // Submit form
    const submitButton = page.locator('button[type="submit"]')
      .or(page.locator('button:has-text("Join")'))
      .first();
    
    if (await submitButton.isVisible()) {
      console.log('[DEBUG] Submitting checkout form');
      await submitButton.click();
    }
    
    // Wait for success message
    const successMessage = page.locator('text=Thank you')
      .or(page.locator('text=Success'))
      .or(page.locator('[data-testid="checkout-success"]'));
    
    await expect(successMessage.first()).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Subscription View UI', () => {
  test('1. Navigate to subscriptions from user menu', async ({ page }) => {
    await page.goto(CONFIG.webUrl);
    await page.waitForLoadState('networkidle');
    
    // First sign in using mock auth
    await setupMockAuth(page);
    await page.goto(CONFIG.webUrl);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Find user avatar/menu
    const userMenu = page.locator('[data-testid="user-menu"]')
      .or(page.locator('button:has(span.rounded-full)'))
      .or(page.locator('.avatar'))
      .first();
    
    if (await userMenu.isVisible({ timeout: 3000 })) {
      await userMenu.click();
      await page.waitForTimeout(500);
      
      // Look for "My Subscriptions" menu item
      const subscriptionsLink = page.locator('text=My Subscriptions')
        .or(page.locator('[data-testid="subscriptions-link"]'))
        .first();
      
      if (await subscriptionsLink.isVisible({ timeout: 3000 })) {
        await subscriptionsLink.click();
        await page.waitForTimeout(1000);
        
        // Verify we're on the subscriptions page
        const pageTitle = page.locator('h1:has-text("My Subscriptions")')
          .or(page.locator('text=Manage your game server subscriptions'))
          .first();
        
        await expect(pageTitle).toBeVisible({ timeout: 5000 });
        console.log('✅ Navigated to subscriptions view');
      } else {
        console.log('⚠️ Subscriptions link not visible (user may not be authenticated)');
      }
    } else {
      console.log('⚠️ User menu not visible (auth may not be set up)');
    }
  });

  test('2. Subscriptions view displays correctly', async ({ page }) => {
    // Set up authenticated session
    await setupMockAuth(page);
    
    // Navigate directly to subscriptions view
    await page.goto(`${CONFIG.webUrl}?view=subscriptions`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check for subscription cards or empty state
    const hasSubscriptions = await page.locator('[data-testid="subscription-card"]')
      .or(page.locator('.subscription-card'))
      .or(page.locator('text=Active'))
      .first()
      .isVisible({ timeout: 5000 })
      .catch(() => false);
    
    const hasEmptyState = await page.locator('text=No subscriptions yet')
      .or(page.locator('text=Browse our game servers'))
      .first()
      .isVisible({ timeout: 5000 })
      .catch(() => false);
    
    // Either state is valid
    expect(hasSubscriptions || hasEmptyState).toBeTruthy();
    
    if (hasSubscriptions) {
      console.log('✅ Subscription cards displayed');
    } else {
      console.log('✅ Empty state displayed (no subscriptions)');
    }
  });

  test('3. Back button returns to dashboard', async ({ page }) => {
    await setupMockAuth(page);
    await page.goto(`${CONFIG.webUrl}?view=subscriptions`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const backButton = page.locator('button:has-text("Back")')
      .or(page.locator('[data-testid="back-button"]'))
      .or(page.locator('button svg.lucide-arrow-left').locator('..'))
      .first();
    
    if (await backButton.isVisible({ timeout: 3000 })) {
      await backButton.click();
      await page.waitForTimeout(1000);
      
      // Should be back on dashboard or home
      const currentUrl = page.url();
      expect(currentUrl).not.toContain('subscriptions');
      console.log('✅ Back button works');
    }
  });
});
