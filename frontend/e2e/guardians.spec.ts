import { createStudent, enrollInSeedProgram } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('secretaria vincula responsavel e ele acessa o portal do dependente', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Dependente ${suffix}`);
  const enrollment = await enrollInSeedProgram(request, student.id);
  const guardianEmail = `resp.${suffix}@alfa.example.com`;

  await login(page, users.admin);
  await page.goto(`/admin/secretariat/enrollments/${enrollment.id}`);
  await page.getByRole('tab', { name: /Responsáveis/ }).click();
  await page.getByLabel('Nome do responsável').fill(`Responsável ${suffix}`);
  await page.getByLabel('E-mail do responsável').fill(guardianEmail);
  await page.getByLabel('Senha inicial').fill('e2e-senha-123');
  await page.getByLabel('Parentesco').selectOption('mother');
  await page.getByLabel('Responsável financeiro').check();
  await page.getByRole('button', { name: 'Vincular' }).click();
  await expectToast(page, 'Responsável vinculado.');
  await expect(page.getByText(`Responsável ${suffix} · Mãe`)).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, guardianEmail);
  await page.waitForURL('**/guardian');
  await page.getByRole('link', { name: new RegExp(student.name) }).click();
  await expect(page.getByRole('heading', { name: student.name })).toBeVisible();
  await expect(page.getByText('Ainda não há notas publicadas.')).toBeVisible();
  await page.getByRole('tab', { name: /Comunicados/ }).click();
  await expect(page.getByText('Nenhum comunicado.')).toBeVisible();
  await page.getByRole('tab', { name: /Financeiro/ }).click();
  await expect(page.getByText('Nenhuma cobrança.')).toBeVisible();
});

test('aluno nao acessa o portal do responsavel', async ({ page }) => {
  await login(page, users.aluno);
  await page.goto('/guardian');
  await expect(page.getByRole('heading', { name: 'Acesso restrito' })).toBeVisible();
});
