import { expect, login, test } from './support/fixtures';
import { users } from './support/users';

/**
 * Exige a API com TENANT_BASE_DOMAIN igual a E2E_TENANT_BASE_DOMAIN (ex.: "localhost",
 * pois o navegador resolve *.localhost para a propria maquina).
 */
const baseDomain = process.env.E2E_TENANT_BASE_DOMAIN;
const port = new URL(process.env.E2E_BASE_URL ?? 'http://localhost:3000').port || '3000';
const origin = (slug: string) => `http://${slug}.${baseDomain}:${port}`;

test.skip(!baseDomain, 'defina E2E_TENANT_BASE_DOMAIN para testar instituicao por subdominio');

test('login no subdominio mostra a marca e entra naquela instituicao', async ({ page }) => {
  await page.goto(`${origin('faculdade-beta')}/login`);
  await expect(page.getByRole('heading', { name: 'Faculdade Beta' })).toBeVisible();
  await login(page, users.admin);
  await expect(page.locator('aside').first()).toContainText('Faculdade Beta');
});

test('usuario sem vinculo nao entra pelo subdominio de outra instituicao', async ({ page }) => {
  await page.goto(`${origin('faculdade-beta')}/login`);
  await page.fill('input[name="email"]', users.aluno);
  await page.fill('input[name="password"]', 'e2e-senha-123');
  await page.click('button[type="submit"]');
  await expect(page.getByText('Sem acesso a esta instituição')).toBeVisible();
});
