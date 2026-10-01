import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('perfil de acesso concede a secretaria ao instrutor e a remocao revoga', async ({ page }) => {
  const suffix = uniqueSuffix();
  const roleName = `Apoio da secretaria ${suffix}`;

  await login(page, users.admin);
  await page.getByRole('link', { name: 'Perfis de acesso' }).first().click();
  await page.getByRole('button', { name: 'Novo perfil' }).click();
  const modal = page.getByRole('dialog', { name: 'Novo perfil de acesso' });
  await modal.getByLabel('Nome').fill(roleName);
  await modal.getByLabel(/Secretaria acadêmica/).check();
  await modal.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Perfil salvo.');
  await page.getByLabel(`Pessoa para ${roleName}`).selectOption({ label: `Instrutor Alfa (${users.instrutor})` });
  await page.getByRole('button', { name: `Atribuir ${roleName}` }).click();
  await expectToast(page, 'Perfil atribuído.');

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.instrutor);
  await page.getByRole('link', { name: 'Secretaria' }).first().click();
  await expect(page.getByRole('heading', { name: 'Secretaria', exact: true })).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.admin);
  await page.goto('/admin/access');
  await page.getByRole('button', { name: `Remover Instrutor Alfa de ${roleName}` }).click();
  await expectToast(page, 'Perfil removido da pessoa.');
  page.once('dialog', (dialog) => dialog.accept());
  await page.getByRole('button', { name: `Excluir ${roleName}` }).click();
  await expectToast(page, 'Perfil excluído.');

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.instrutor);
  await expect(page.getByRole('link', { name: 'Secretaria' })).toHaveCount(0);
});
