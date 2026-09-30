import { defineConfig, devices } from '@playwright/test';

/**
 * Testes de navegador. Pre-requisitos (ver e2e/README.md):
 * - API rodando com banco populado por `backend/scripts/seed_e2e.py`;
 * - `npm run build` feito (o frontend sobe com `next start`).
 */
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:3000';
const chromiumPath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE;

export default defineConfig({
  testDir: './e2e',
  // Os testes compartilham o banco de e2e; rodar em serie evita interferencia.
  workers: 1,
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL,
    actionTimeout: 10_000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1366, height: 850 }, launchOptions: chromiumPath ? { executablePath: chromiumPath } : {} },
    },
  ],
  webServer: {
    command: 'npx next start -p 3000',
    url: `${baseURL}/login`,
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
