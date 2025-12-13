import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for RealmGrid E2E Tests (v1)
 * 
 * Tests the full user journey:
 * - Login with Microsoft SSO (mocked)
 * - Browse Minecraft servers
 * - Add server to cart
 * - Checkout process
 * - Server provisioning
 * - Subscription creation
 * 
 * Run with: ./run-tests.sh
 */
export default defineConfig({
  testDir: './tests',
  
  // Run tests sequentially for E2E flow
  fullyParallel: false,
  
  // CI-specific settings
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  
  // Single worker for sequential E2E tests
  workers: 1,
  
  // Reporters with detailed output
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list'], // Show test names in console
  ],
  
  // Output directory for screenshots, videos, etc.
  outputDir: 'test-results',
  
  use: {
    // Admin portal runs on port 4321 (Astro default), Web app on port 5173
    baseURL: process.env.ADMIN_URL || process.env.WEB_URL || 'http://localhost:4321',
    
    // Always collect trace for debugging
    trace: 'on',
    
    // Always take screenshots for debugging
    screenshot: 'on',
    
    // Record video for debugging
    video: 'on',
    
    // Default timeout for actions
    actionTimeout: 30000,
    
    // Navigation timeout
    navigationTimeout: 60000,
    
    // Viewport size
    viewport: { width: 1280, height: 720 },
    
    // Ignore HTTPS errors for local dev
    ignoreHTTPSErrors: true,
  },

  // Global timeout for each test (2 minutes)
  timeout: 120000,

  // Expect timeout
  expect: {
    timeout: 10000,
  },

  // Only test on Chromium for speed
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Web server configuration
  // The run-tests.sh script handles server startup
  // Uncomment to have Playwright start the servers automatically
  /*
  webServer: [
    {
      command: 'cd ../../realm-web && PORT=5005 npm run dev',
      url: 'http://localhost:5005',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
    {
      command: 'cd ../../realm-functions && func start',
      url: 'http://localhost:7071/api/health_check',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      stdout: 'pipe',
      stderr: 'pipe',
    },
  ],
  */
});
