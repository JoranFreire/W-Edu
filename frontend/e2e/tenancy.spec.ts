import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { E2E_PASSWORD, users } from './support/users';

const primaryColor = (page: import('@playwright/test').Page) =>
  page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--color-indigo-600').trim());

test('admin com duas instituicoes entra na primeira e ve o seletor', async ({ page }) => {
  await login(page, users.admin);
  const switcher = page.getByLabel('Instituição ativa');
  await expect(switcher).toHaveValue('escola-alfa');
  await expect(switcher.locator('option[value="faculdade-beta"]')).toHaveCount(1);
});

test('identidade visual aplica nome e cor; trocar de instituicao volta ao padrao', async ({ page }) => {
  const name = `Alfa ${uniqueSuffix()}`;
  await login(page, users.admin);
  await page.goto('/admin/institution');
  await page.getByLabel('Nome exibido no menu').fill(name);
  await page.getByPlaceholder('#4f46e5').fill('#059669');
  await page.getByRole('button', { name: 'Salvar alterações' }).click();
  await expectToast(page, 'Instituição atualizada.');
  await expect(page.locator('aside').first()).toContainText(name);
  expect(await primaryColor(page)).toBe('#059669');

  await page.getByLabel('Instituição ativa').selectOption('faculdade-beta');
  await page.waitForURL('**/dashboard');
  await expect(page.locator('aside').first()).toContainText('Faculdade Beta');
  expect(await primaryColor(page)).not.toBe('#059669');
});

test('campus pode ser criado e aparece na lista', async ({ page }) => {
  const campus = `Campus ${uniqueSuffix()}`;
  await login(page, users.admin);
  await page.goto('/admin/institution');
  await page.getByPlaceholder('Nome do campus').fill(campus);
  await page.getByRole('button', { name: 'Adicionar' }).click();
  await expectToast(page, 'Campus criado.');
  await expect(page.getByText(campus)).toBeVisible();
});

test('super admin cria instituicao com primeiro admin e entra nela', async ({ page, browser }) => {
  const sfx = uniqueSuffix();
  const adminEmail = `diretor-${sfx}@nova.example.com`;
  await login(page, users.root);
  await page.goto('/platform/institutions');
  await page.getByRole('button', { name: 'Nova instituição' }).click();
  await page.getByLabel('Nome', { exact: true }).first().fill(`Faculdade Nova ${sfx}`);
  await page.getByLabel('Nome', { exact: true }).nth(1).fill('Diretor');
  await page.getByLabel('E-mail').fill(adminEmail);
  await page.getByLabel('Senha inicial').fill(E2E_PASSWORD);
  await page.getByRole('button', { name: 'Criar instituição' }).click();
  await expectToast(page, 'Instituição criada.');
  const row = page.locator('tr', { hasText: `faculdade-nova-${sfx}` });
  await row.getByText('Entrar').click();
  await page.waitForURL('**/dashboard');
  await expect(page.locator('aside').first()).toContainText(`Faculdade Nova ${sfx}`);

  const director = await browser.newPage();
  await login(director, adminEmail);
  await expect(director.locator('aside').first()).toContainText(`Faculdade Nova ${sfx}`);
  await director.close();
});

test('aluno nao acessa areas administrativas nem ve seletor', async ({ page }) => {
  await login(page, users.aluno);
  for (const path of ['/admin/institution', '/platform/institutions', '/admin/finance']) {
    await page.goto(path);
    await expect(page.getByText('Acesso restrito')).toBeVisible();
  }
  await expect(page.getByLabel('Instituição ativa')).toHaveCount(0);
});
