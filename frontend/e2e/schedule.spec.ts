import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test.beforeEach(async ({ page }) => {
  await login(page, users.admin);
  await page.goto('/admin/schedule');
  await expect(page.getByText('Turma Matemática')).toBeVisible();
});

test('cria unidade vinculada a campus pelo modal', async ({ page }) => {
  const name = `Prédio ${uniqueSuffix()}`;
  await page.getByRole('tab', { name: /Unidades/ }).click();
  await page.getByRole('button', { name: 'Adicionar unidade' }).click();
  const dialog = page.getByRole('dialog');
  await dialog.getByPlaceholder('Nome da unidade').fill(name);
  await dialog.getByLabel('Campus').selectOption({ label: 'Campus Centro' });
  await dialog.getByRole('button', { name: 'Criar unidade' }).click();
  await expect(page.getByText(name)).toBeVisible();
  await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('abas de salas e agenda do instrutor', async ({ page }) => {
  await page.getByRole('tab', { name: /Salas/ }).click();
  await expect(page.getByRole('button', { name: 'Adicionar sala' })).toBeVisible();
  await page.getByRole('tab', { name: /Instrutores/ }).click();
  await expect(page.getByText('Agenda do professor')).toBeVisible();
  await expect(page.getByLabel('Instrutor').locator('option', { hasText: 'Instrutor Alfa' })).toHaveCount(1);
});

/** Horario de 30 min variando a cada execucao, para nao colidir com encontros ja criados no instrutor. */
function uniqueSlot() {
  const minutes = Math.floor(Date.now() / 60_000);
  const start = new Date();
  start.setDate(start.getDate() + 1 + (minutes % 50));
  start.setHours(6 + (minutes % 14), (minutes % 2) * 30, 0, 0);
  const end = new Date(start.getTime() + 30 * 60_000);
  const local = (date: Date) => {
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  };
  return { start: local(start), end: local(end) };
}

test('cria encontro para uma turma', async ({ page }) => {
  const slot = uniqueSlot();
  await page.getByRole('button', { name: 'Criar encontro' }).first().click();
  const dialog = page.getByRole('dialog', { name: 'Criar encontro' });
  await dialog.getByPlaceholder('Título do encontro').fill(`Aula ${uniqueSuffix()}`);
  await dialog.getByLabel('Início').fill(slot.start);
  await dialog.getByLabel('Fim').fill(slot.end);
  await dialog.getByRole('button', { name: 'Criar encontro' }).click();
  await expectToast(page, 'Encontro criado.');
});
