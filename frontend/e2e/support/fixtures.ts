import { test as base, expect, type Page } from '@playwright/test';
import { E2E_PASSWORD } from './users';

export async function login(page: Page, email: string, password = E2E_PASSWORD) {
  await page.goto('/login');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
}

/** Sufixo para nomes criados pelos testes, permitindo reexecutar no mesmo banco. */
export const uniqueSuffix = () => Date.now().toString(36);

/** Primeira ocorrencia visivel (listas tem versoes desktop/mobile no DOM). */
export const visibleText = (page: Page, text: string) => page.locator(`text=${text} >> visible=true`).first();

export async function expectToast(page: Page, text: string) {
  await expect(page.getByText(text).first()).toBeVisible();
}

/** Falha o teste se a pagina lancar erro de JavaScript. */
export const test = base.extend<{ failOnPageErrors: void }>({
  failOnPageErrors: [async ({ page }, use) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await use();
    expect(errors, 'erros de JavaScript na pagina').toEqual([]);
  }, { auto: true }],
});

export { expect };
