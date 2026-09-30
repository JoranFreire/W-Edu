import { expect, expectToast, login, test, uniqueSuffix, visibleText } from './support/fixtures';
import { users } from './support/users';

test.beforeEach(async ({ page }) => {
  await login(page, users.admin);
});

test('cursos: detalhe com abas e edicao refletida', async ({ page }) => {
  const newName = `História ${uniqueSuffix()}`;
  await page.goto('/admin/courses');
  const card = page.locator('div', { has: page.getByRole('heading', { name: /^História/ }) }).last();
  await card.getByRole('button', { name: 'Gerenciar curso' }).click();
  await page.getByRole('tab', { name: /Aulas/ }).click();
  await page.getByRole('tab', { name: /Pré-requisitos/ }).click();
  await page.getByRole('tab', { name: /Módulos/ }).click();

  await page.getByRole('button', { name: 'Editar curso' }).click();
  await page.locator('input[value^="História"]').fill(newName);
  await page.getByRole('button', { name: /Salvar/ }).last().click();
  await expectToast(page, 'Curso atualizado!');
  await expect(page.getByRole('heading', { name: newName })).toBeVisible();
  await page.getByRole('button', { name: 'Voltar para cursos' }).click();
  await expect(page.getByText(newName)).toBeVisible();
});

test('certificados: regra, elegibilidade e emitidos', async ({ page }) => {
  await page.goto('/admin/certificates');
  await page.getByRole('button', { name: /Matemática/ }).click();
  await page.getByRole('button', { name: 'Salvar regra' }).click();
  await expectToast(page, 'Regra atualizada.');
  await page.getByRole('tab', { name: /Emitir/ }).click();
  await page.getByRole('tabpanel').locator('select').selectOption({ label: 'Aluno Alfa - aluno@alfa.example.com' });
  await page.getByRole('button', { name: 'Ver elegibilidade' }).click();
  await expect(page.getByText('Não elegível')).toBeVisible();
  await page.getByRole('tab', { name: /Emitidos/ }).click();
  await page.getByRole('button', { name: 'Voltar para cursos' }).click();
  await expect(page.getByText('Selecione um curso')).toBeVisible();
});

test('usuarios: lista, cria empresa e abre novo usuario', async ({ page }) => {
  const company = `Empresa ${uniqueSuffix()}`;
  await page.goto('/admin/students');
  await expect(visibleText(page, users.aluno)).toBeVisible();
  await page.getByRole('tab', { name: /Empresas/ }).click();
  await page.getByRole('button', { name: 'Nova empresa' }).click();
  await page.getByRole('dialog').getByPlaceholder('Nome da empresa').fill(company);
  await page.getByRole('dialog').getByRole('button', { name: 'Criar empresa' }).click();
  await expectToast(page, 'Empresa criada!');
  await expect(visibleText(page, company)).toBeVisible();
  await page.getByRole('tab', { name: /Usuários/ }).click();
  await page.getByRole('button', { name: 'Novo usuário' }).click();
  await page.getByRole('button', { name: 'Cancelar' }).click();
});
