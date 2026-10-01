import { createStudent, linkGuardian } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('mesma pessoa como professora e aluna; depois responsavel de um aluno', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const name = `Dupla ${suffix}`;
  const email = `dupla.${suffix}@alfa.example.com`;

  // Cadastro com dois papeis, professora como principal.
  await login(page, users.admin);
  await page.goto('/admin/users');
  await page.getByRole('button', { name: 'Novo usuário' }).click();
  const dialog = page.getByRole('dialog', { name: 'Novo usuário' });
  await dialog.getByLabel('Nome *').fill(name);
  await dialog.getByLabel('E-mail *').fill(email);
  await dialog.getByLabel('Senha *').fill('e2e-senha-123');
  await dialog.getByLabel('Instrutor').check();
  await dialog.getByLabel('Papel principal').selectOption('instructor');
  await dialog.getByRole('button', { name: 'Criar usuário' }).click();
  await expectToast(page, 'Usuário criado!');

  // A lista mostra os dois papeis e o filtro por perfil encontra a pessoa nos dois.
  await page.getByLabel('Buscar usuário').fill(name);
  const row = page.getByRole('link', { name: `Dossiê de ${name}`, exact: true }).locator('xpath=ancestor::div[1]');
  await expect(row.getByText('Instrutor', { exact: true })).toBeVisible();
  await expect(row.getByText('Aluno', { exact: true })).toBeVisible();
  for (const role of ['students', 'instructors']) {
    await page.getByLabel('Perfil', { exact: true }).selectOption(role);
    await expect(page.getByRole('link', { name: `Dossiê de ${name}`, exact: true })).toBeVisible();
  }

  // Vira responsavel de um aluno: ganha o papel sem perder os outros.
  const kid = await createStudent(request, `Filho ${suffix}`);
  await linkGuardian(request, kid.id, name, email);

  await page.evaluate(() => window.localStorage.clear());
  await login(page, email);
  const menu = page.getByRole('navigation');
  await expect(menu.getByRole('link', { name: 'Diário de classe' })).toBeVisible();
  await expect(menu.getByRole('link', { name: 'Boletim' })).toBeVisible();
  await expect(menu.getByRole('link', { name: 'Meus dependentes' })).toBeVisible();
  // Papel principal primeiro; os demais em seguida.
  await expect(page.getByText(/^Instrutor · (Aluno · Responsável|Responsável · Aluno)$/)).toBeVisible();

  await menu.getByRole('link', { name: 'Meus dependentes' }).click();
  await expect(page.getByText(kid.name)).toBeVisible();
  await menu.getByRole('link', { name: 'Diário de classe' }).click();
  await expect(page.getByRole('heading', { name: 'Diário de classe' })).toBeVisible();
});
