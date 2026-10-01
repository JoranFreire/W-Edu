import { expect, login, test } from './support/fixtures';
import { users } from './support/users';

test('cursos do admin: alterna grade e lista e lembra a escolha', async ({ page }) => {
  await login(page, users.admin);
  await page.goto('/admin/courses');
  await expect(page.getByRole('button', { name: 'Exibir em grade' })).toHaveAttribute('aria-pressed', 'true');

  await page.getByRole('button', { name: 'Exibir em lista' }).click();
  const list = page.getByRole('list', { name: 'Cursos' });
  await expect(list.getByRole('heading', { name: /^Matemática/ }).first()).toBeVisible();
  await expect(list.getByRole('button', { name: 'Gerenciar curso' }).first()).toBeVisible();

  await page.reload();
  await expect(page.getByRole('button', { name: 'Exibir em lista' })).toHaveAttribute('aria-pressed', 'true');
  await list.getByRole('button', { name: 'Gerenciar curso' }).first().click();
  await expect(page.getByRole('button', { name: 'Voltar para cursos' })).toBeVisible();

  await page.getByRole('button', { name: 'Voltar para cursos' }).click();
  await page.getByRole('button', { name: 'Exibir em grade' }).click();
  await expect(page.getByRole('list', { name: 'Cursos' })).toHaveCount(0);
});

test('certificados em lista', async ({ page }) => {
  await login(page, users.admin);
  await page.goto('/admin/certificates');
  await page.getByRole('button', { name: 'Exibir em lista' }).click();
  await page.getByRole('list', { name: 'Cursos' }).getByRole('button', { name: /Matemática/ }).first().click();
  await expect(page.getByRole('button', { name: 'Salvar regra' })).toBeVisible();
});

test('catalogo do aluno em lista', async ({ page }) => {
  await login(page, users.aluno);
  await page.goto('/courses');
  await page.getByRole('button', { name: 'Exibir em lista' }).click();
  const list = page.getByRole('list', { name: 'Cursos' });
  await expect(list.getByRole('listitem').first()).toBeVisible();
  await expect(list.getByRole('button', { name: 'Matricular' }).or(list.getByRole('link', { name: /Continuar/ })).first()).toBeVisible();
});
