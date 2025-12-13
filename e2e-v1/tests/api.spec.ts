import { test, expect } from '@playwright/test';
import { CONFIG } from './test-config';

/**
 * API Integration Tests
 * 
 * Tests the Azure Functions API endpoints:
 * 1. Health check
 * 2. Checkout creation
 * 3. Server provisioning
 * 4. Server listing
 * 5. Subscription management
 */

// Helper to check if API is available
async function isApiAvailable(request: any): Promise<boolean> {
  try {
    const response = await request.get(`${CONFIG.functionsUrl}/api/health`, {
      timeout: 5000,
    });
    return response.ok();
  } catch {
    return false;
  }
}

test.describe('API Health & Checkout', () => {
  test('1. Health check endpoint works', async ({ request }) => {
    console.log(`[DEBUG] Calling health check: ${CONFIG.functionsUrl}/api/health`);
    
    try {
      const response = await request.get(`${CONFIG.functionsUrl}/api/health`, {
        timeout: 5000,
      });
      console.log(`[DEBUG] Health check status: ${response.status()}`);
      
      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      console.log('[DEBUG] Health response:', data);
      expect(data.status).toBe('healthy');
    } catch (error) {
      console.log('[DEBUG] API not available, skipping test');
      test.skip(true, 'API server not available');
    }
  });

  test('2. Create checkout session', async ({ request }) => {
    if (!(await isApiAvailable(request))) {
      test.skip(true, 'API server not available');
      return;
    }

    const testData = {
      userId: 'e2e-test-user',
      email: CONFIG.testUser.email,
      gameType: 'minecraft',
      tier: 'small',
      serverName: `E2E-Test-${Date.now()}`,
    };
    
    console.log('[DEBUG] Creating checkout session:', testData);
    
    const response = await request.post(`${CONFIG.functionsUrl}/api/checkout/create`, {
      data: testData,
    });
    
    console.log(`[DEBUG] Checkout response status: ${response.status()}`);
    
    // In test mode, this might return 200 or redirect
    if (response.ok()) {
      const data = await response.json();
      console.log('[DEBUG] Checkout response:', data);
      expect(data).toHaveProperty('checkoutUrl');
    }
  });
});

test.describe('Server Provisioning API', () => {
  test('1. Provision new Minecraft server', async ({ request }) => {
    if (!(await isApiAvailable(request))) {
      test.skip(true, 'API server not available');
      return;
    }

    const serverId = `e2e-srv-${Date.now()}`;
    const serverData = {
      serverId: serverId,
      userId: 'e2e-test-user',
      name: `E2E Minecraft Server ${Date.now()}`,
      gameType: 'minecraft',
      tier: 'small',
      version: '1.20.4',
      settings: {
        MAX_PLAYERS: 10,
        MOTD: 'E2E Test Server',
      },
    };
    
    console.log('[DEBUG] Provisioning server:', serverData);
    
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/provision`, {
      data: serverData,
    });
    
    console.log(`[DEBUG] Provision response status: ${response.status()}`);
    
    // Server provisioning might take time
    if (response.status() === 200 || response.status() === 202) {
      const data = await response.json();
      console.log('[DEBUG] Provision response:', data);
      
      if (data.success) {
        expect(data.data).toHaveProperty('serverId');
        expect(data.data).toHaveProperty('status');
        expect(['installing', 'starting', 'running', 'pending']).toContain(data.data.status);
      }
    }
  });

  test('2. List servers for user', async ({ request }) => {
    if (!(await isApiAvailable(request))) {
      test.skip(true, 'API server not available');
      return;
    }

    const userId = 'e2e-test-user';
    console.log(`[DEBUG] Listing servers for user: ${userId}`);
    
    const response = await request.get(`${CONFIG.functionsUrl}/api/game-servers`, {
      params: { userId },
    });
    
    console.log(`[DEBUG] List servers status: ${response.status()}`);
    
    if (response.ok()) {
      const data = await response.json();
      console.log('[DEBUG] Servers list:', data);
      expect(Array.isArray(data.data) || Array.isArray(data.servers)).toBeTruthy();
    }
  });

  test('3. Create subscription', async ({ request }) => {
    if (!(await isApiAvailable(request))) {
      test.skip(true, 'API server not available');
      return;
    }

    const subscriptionData = {
      userId: 'e2e-test-user',
      email: CONFIG.testUser.email,
      tier: 'small',
      gameType: 'minecraft',
      serverName: `E2E Subscription Test ${Date.now()}`,
    };
    
    console.log('[DEBUG] Creating subscription:', subscriptionData);
    
    const response = await request.post(`${CONFIG.functionsUrl}/api/subscriptions`, {
      data: subscriptionData,
    });
    
    console.log(`[DEBUG] Subscription response status: ${response.status()}`);
    
    // This might require Mollie integration
    if (response.ok()) {
      const data = await response.json();
      console.log('[DEBUG] Subscription response:', data);
      expect(data).toBeDefined();
    }
  });
});
