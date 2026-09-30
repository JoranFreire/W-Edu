import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('perfil salvo persiste apos recarregar', async ({ page }) => {
  const phone = `11 9${uniqueSuffix()}`;
  await login(page, users.aluno);
  await page.goto('/settings');
  await page.getByLabel('Telefone').fill(phone);
  await page.getByRole('button', { name: 'Salvar alterações' }).click();
  await expectToast(page, 'Perfil atualizado.');
  await page.reload();
  await expect(page.getByLabel('Telefone')).toHaveValue(phone);
});

test('tema e menu recolhido persistem', async ({ page }) => {
  await login(page, users.aluno);
  const isDark = () => page.evaluate(() => document.documentElement.classList.contains('dark'));
  const before = await isDark();
  await page.getByRole('button', { name: before ? 'Ativar tema claro' : 'Ativar tema escuro' }).click();
  await page.reload();
  await expect.poll(isDark).toBe(!before);

  await page.getByRole('button', { name: 'Recolher menu lateral' }).click();
  await page.reload();
  await page.getByRole('button', { name: 'Expandir menu lateral' }).click();
  await expect(page.getByRole('button', { name: 'Recolher menu lateral' })).toBeVisible();
});

test('validacao publica de certificado pelo link', async ({ page }) => {
  await page.goto('/validate-certificate?code=INEXISTENTE');
  await expect(page.getByLabel('Código de validação')).toHaveValue('INEXISTENTE');
  await expect(page.getByText(/Certificado inválido|Não foi possível validar/)).toBeVisible();
});
