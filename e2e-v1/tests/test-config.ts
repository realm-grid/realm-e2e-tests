import { Page } from '@playwright/test';

/**
 * Shared Test Configuration
 * 
 * Contains configuration constants and helper functions
 * shared across all E2E test files.
 */

export const CONFIG = {
  // Web app URL (realm-admin runs on 5173 by default)
  webUrl: process.env.WEB_URL || 'http://localhost:5173',
  
  // Azure Functions URL
  functionsUrl: process.env.FUNCTIONS_URL || 'http://localhost:7071',
  
  // Admin app URL (same as webUrl when testing admin)
  adminUrl: process.env.ADMIN_URL || 'http://localhost:5173',
  
  // Test user credentials (mock for E2E)
  testUser: {
    email: 'e2e-test@realmgrid.io',
    name: 'E2E Test User',
    id: 'e2e-test-user-id',
  },
  
  // Timeouts
  timeouts: {
    navigation: 30000,
    action: 10000,
    serverProvision: 60000,
  },
};

/**
 * Mock authentication token for E2E tests
 * This simulates a logged-in user without requiring real Microsoft SSO
 */
export const MOCK_AUTH_TOKEN = {
  user: {
    id: CONFIG.testUser.id,
    email: CONFIG.testUser.email,
    name: CONFIG.testUser.name,
    accessToken: 'mock-access-token-for-e2e-testing',
    expiresAt: Date.now() + 3600000, // 1 hour from now
  },
  isAuthenticated: true,
};

/**
 * Setup mock authentication in the browser
 * Call this before tests that require a logged-in user
 */
export async function setupMockAuth(page: Page): Promise<void> {
  console.log('[DEBUG] Setting up mock authentication...');
  
  await page.addInitScript((token) => {
    // Set the auth token in localStorage
    localStorage.setItem('realm_auth_token', JSON.stringify(token));
    
    // Also set a flag for the app to recognize mock auth
    localStorage.setItem('realm_e2e_test', 'true');
  }, MOCK_AUTH_TOKEN);
  
  console.log('[DEBUG] Mock auth token set in localStorage');
}

/**
 * Clear authentication from the browser
 */
export async function clearAuth(page: Page): Promise<void> {
  console.log('[DEBUG] Clearing authentication...');
  
  await page.evaluate(() => {
    localStorage.removeItem('realm_auth_token');
    localStorage.removeItem('realm_e2e_test');
  });
  
  console.log('[DEBUG] Auth cleared');
}

/**
 * Wait for the app to be fully loaded
 */
export async function waitForAppLoad(page: Page): Promise<void> {
  console.log('[DEBUG] Waiting for app to load...');
  
  // Wait for hydration to complete
  await page.waitForLoadState('networkidle');
  
  // Give React time to hydrate
  await page.waitForTimeout(1000);
  
  console.log('[DEBUG] App loaded');
}

/**
 * Generate a unique server name for tests
 */
export function generateServerName(): string {
  return `E2E-Minecraft-${Date.now()}`;
}

/**
 * Generate a unique user ID for tests
 */
export function generateUserId(): string {
  return `e2e-user-${Date.now()}`;
}

/**
 * Log test step with timestamp
 */
export function logStep(step: string): void {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [STEP] ${step}`);
}

/**
 * Log debug info
 */
export function debug(message: string, data?: unknown): void {
  console.log(`[DEBUG] ${message}`, data ? JSON.stringify(data, null, 2) : '');
}

/**
 * Take a screenshot for debugging
 */
export async function takeDebugScreenshot(
  page: Page, 
  name: string
): Promise<void> {
  const timestamp = Date.now();
  const filename = `debug-${name}-${timestamp}.png`;
  await page.screenshot({ path: `test-results/${filename}`, fullPage: true });
  console.log(`[DEBUG] Screenshot saved: ${filename}`);
}

/**
 * Minecraft server tiers for testing
 */
export const SERVER_TIERS = {
  small: {
    name: 'Small',
    price: '€9.99',
    ram: '2GB',
    players: 10,
  },
  medium: {
    name: 'Medium', 
    price: '€19.99',
    ram: '4GB',
    players: 25,
  },
  heavy: {
    name: 'Heavy',
    price: '€49.99',
    ram: '8GB',
    players: 50,
  },
};
