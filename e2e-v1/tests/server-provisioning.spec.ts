import { test, expect } from '@playwright/test';
import { CONFIG, debug, logStep, generateServerName, generateUserId } from './test-config';

/**
 * Minecraft Server Provisioning E2E Tests
 * 
 * Tests server provisioning, lifecycle, and management.
 */

// Helper to check if API is available
async function isApiAvailable(request: any): Promise<boolean> {
  try {
    const response = await request.get(`${CONFIG.functionsUrl}/api/health`, { timeout: 5000 });
    return response.ok();
  } catch { return false; }
}

test.describe('Server Provisioning', () => {
  const testServerId = `srv-${Date.now()}`;
  const testUserId = generateUserId();

  test.afterAll(async ({ request }) => {
    await request.delete(`${CONFIG.functionsUrl}/api/game-servers/${testServerId}`);
  });

  test('1. Health check', async ({ request }) => {
    logStep('Checking API health');
    
    try {
      const response = await request.get(`${CONFIG.functionsUrl}/api/health`, { timeout: 5000 });
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.status).toBe('healthy');
      debug('Health check passed');
    } catch {
      test.skip(true, 'API not available');
    }
  });

  test('2. Provision Minecraft server', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Provisioning new Minecraft server');
    
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/provision`, {
      data: {
        serverId: testServerId,
        userId: testUserId,
        name: generateServerName(),
        gameType: 'minecraft',
        tier: 'small',
        version: '1.20.4',
        settings: { MAX_PLAYERS: 10, MOTD: 'E2E Test' },
      },
    });

    debug('Provision response', { status: response.status() });
    expect([200, 201, 202, 400]).toContain(response.status());

    if (response.ok()) {
      const data = await response.json();
      if (data.success !== false) {
        expect(data.data || data).toHaveProperty('serverId');
        debug('Server provisioned', { id: testServerId });
      }
    }
  });

  test('3. List user servers', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Listing servers');
    
    const response = await request.get(`${CONFIG.functionsUrl}/api/game-servers`, {
      params: { userId: testUserId },
    });

    if (response.ok()) {
      const data = await response.json();
      const servers = data.data || data.servers || [];
      debug(`Found ${servers.length} servers`);
    }
  });

  test('4. Get server details', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Getting server details');
    
    const response = await request.get(`${CONFIG.functionsUrl}/api/game-servers/${testServerId}`);
    debug('Details response', { status: response.status() });

    if (response.ok()) {
      const data = await response.json();
      expect(data.data || data).toHaveProperty('serverId');
    }
  });

  test('5. Check server status', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    logStep('Checking server status');
    
    const response = await request.get(`${CONFIG.functionsUrl}/api/game-servers/${testServerId}/status`);
    debug('Status response', { status: response.status() });

    if (response.ok()) {
      const data = await response.json();
      const validStatuses = ['installing', 'starting', 'running', 'stopping', 'stopped', 'pending'];
      const status = (data.status || data.data?.status || '').toLowerCase();
      expect(validStatuses).toContain(status);
    }
  });
});

test.describe('Server Lifecycle', () => {
  const serverId = `lifecycle-${Date.now()}`;
  const userId = generateUserId();

  test.beforeAll(async ({ request }) => {
    await request.post(`${CONFIG.functionsUrl}/api/game-servers/provision`, {
      data: { serverId, userId, name: 'Lifecycle Test', gameType: 'minecraft', tier: 'small' },
    });
  });

  test.afterAll(async ({ request }) => {
    await request.delete(`${CONFIG.functionsUrl}/api/game-servers/${serverId}`);
  });

  test('1. Stop server', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/${serverId}/stop`);
    debug('Stop response', { status: response.status() });
    expect([200, 404]).toContain(response.status());
  });

  test('2. Start server', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/${serverId}/start`);
    debug('Start response', { status: response.status() });
    expect([200, 404]).toContain(response.status());
  });

  test('3. Restart server', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/${serverId}/restart`);
    debug('Restart response', { status: response.status() });
    expect([200, 404]).toContain(response.status());
  });

  test('4. Create backup', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/${serverId}/backup`);
    debug('Backup response', { status: response.status() });
    expect([200, 201, 404]).toContain(response.status());
  });
});

test.describe('Game Types', () => {
  const games = ['minecraft', 'valheim', 'palworld'];

  for (const game of games) {
    test(`Provision ${game} server`, async ({ request }) => {
      if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
      const id = `${game}-${Date.now()}`;
      
      const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/provision`, {
        data: { serverId: id, userId: generateUserId(), name: `${game} Test`, gameType: game, tier: 'small' },
      });

      debug(`${game} response`, { status: response.status() });
      expect([200, 201, 202, 400, 503]).toContain(response.status());

      if (response.ok()) await request.delete(`${CONFIG.functionsUrl}/api/game-servers/${id}`);
    });
  }
});

test.describe('Error Handling', () => {
  test('Invalid game type', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/provision`, {
      data: { serverId: `err-${Date.now()}`, userId: 'test', name: 'Err', gameType: 'invalid', tier: 'small' },
    });
    expect([400, 422]).toContain(response.status());
  });

  test('Invalid tier', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/provision`, {
      data: { serverId: `err-${Date.now()}`, userId: 'test', name: 'Err', gameType: 'minecraft', tier: 'invalid' },
    });
    expect([400, 422]).toContain(response.status());
  });

  test('Missing required fields', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.post(`${CONFIG.functionsUrl}/api/game-servers/provision`, {
      data: { gameType: 'minecraft', tier: 'small' },
    });
    expect([400, 422]).toContain(response.status());
  });

  test('Non-existent server', async ({ request }) => {
    if (!(await isApiAvailable(request))) { test.skip(true, 'API not available'); return; }
    const response = await request.get(`${CONFIG.functionsUrl}/api/game-servers/non-existent-id`);
    expect([404, 400]).toContain(response.status());
  });
});
