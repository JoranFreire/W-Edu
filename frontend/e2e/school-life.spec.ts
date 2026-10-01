import { createClassGroupOffering, createStudent, enrollInSeedProgram, linkGuardian } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('secretaria registra ocorrencia e o responsavel da ciencia no portal', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Ocorrencia ${suffix}`);
  const enrollment = await enrollInSeedProgram(request, student.id);
  const guardianEmail = `resp.ocorrencia.${suffix}@alfa.example.com`;
  await linkGuardian(request, student.id, `Responsável ${suffix}`, guardianEmail);

  await login(page, users.admin);
  await page.goto(`/admin/secretariat/enrollments/${enrollment.id}`);
  await page.getByRole('tab', { name: /Ocorrências/ }).click();
  await page.getByLabel('Tipo de ocorrência').selectOption('lateness');
  await page.getByLabel('Descrição da ocorrência').fill('Chegou após o início da aula');
  await page.getByRole('button', { name: 'Registrar ocorrência' }).click();
  await expectToast(page, 'Ocorrência registrada.');
  await expect(page.getByText('Chegou após o início da aula')).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, guardianEmail);
  await page.waitForURL('**/guardian');
  await page.getByRole('link', { name: new RegExp(student.name) }).click();
  await page.getByRole('tab', { name: /Comunicados/ }).click();
  await expect(page.getByText('Nova ocorrência')).toBeVisible();
  await page.getByRole('tab', { name: /Ocorrências/ }).click();
  await page.getByRole('button', { name: /^Ciente: Atraso/ }).click();
  await expectToast(page, 'Ciência registrada.');
  await expect(page.getByText(/Ciente em/)).toBeVisible();
});

test('professor publica na agenda da turma e o aluno ve na agenda escolar', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Agenda ${suffix}`);
  const enrollment = await enrollInSeedProgram(request, student.id);
  const { offeringId } = await createClassGroupOffering(request, `Agenda ${suffix}`, enrollment.id);
  const title = `Exercícios ${suffix}`;

  await login(page, users.instrutor);
  await page.goto(`/teaching/offerings/${offeringId}`);
  await page.getByRole('tab', { name: /Agenda/ }).click();
  await page.getByLabel('Tipo do item').selectOption('homework');
  await page.getByLabel('Título do item').fill(title);
  await page.getByRole('button', { name: 'Publicar' }).click();
  await expectToast(page, 'Publicado na agenda.');
  await expect(page.getByText(title)).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, student.email);
  await page.getByRole('link', { name: 'Agenda escolar' }).first().click();
  await expect(page.getByRole('heading', { name: 'Agenda escolar' })).toBeVisible();
  await expect(page.getByText(title)).toBeVisible();
});
