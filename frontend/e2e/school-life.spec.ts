import { createClassGroupOffering, createStudent, enrollInSeedProgram, linkGuardian, registerOccurrence, syncGroupEnrollments } from './support/api';
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

  // O aviso tambem chega na caixa do proprio responsavel.
  await page.getByRole('link', { name: /^Avisos \(1 não lido\)/ }).click();
  await expect(page.getByRole('heading', { name: 'Avisos' })).toBeVisible();
  await expect(page.getByText(/Foi registrada uma ocorrência \(atraso\)/)).toBeVisible();
  await page.getByRole('button', { name: 'Marcar todos como lidos' }).click();
  await expect(page.getByRole('button', { name: /^Marcar como lido/ })).toHaveCount(0);
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

test('professor consulta no diario o historico de ocorrencias do aluno', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Historico ${suffix}`);
  const enrollment = await enrollInSeedProgram(request, student.id);
  const { offeringId } = await createClassGroupOffering(request, `Hist ${suffix}`, enrollment.id);
  await syncGroupEnrollments(request, offeringId);
  await registerOccurrence(request, student.id, `Mal-estar no recreio ${suffix}`);

  await login(page, users.instrutor);
  await page.goto(`/teaching/offerings/${offeringId}`);
  await page.getByRole('tab', { name: /Ocorrências/ }).click();
  await page.getByLabel('Aluno do histórico').selectOption({ label: student.name });
  await expect(page.getByText(`Mal-estar no recreio ${suffix}`)).toBeVisible();
  // Registrada pela secretaria: o professor nao remove.
  await expect(page.getByRole('button', { name: /^Remover Saúde/ })).toHaveCount(0);
});

test('admin publica na agenda pela turma-grupo e pela tela da secretaria', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Agenda Adm ${suffix}`);
  const enrollment = await enrollInSeedProgram(request, student.id);
  const name = `AgAdm ${suffix}`;
  const { groupId } = await createClassGroupOffering(request, name, enrollment.id);

  await login(page, users.admin);
  await page.goto(`/admin/academic/class-groups/${groupId}`);
  await page.getByRole('tab', { name: /Agenda/ }).click();
  await page.getByLabel('Título do item').fill(`Reunião de pais ${suffix}`);
  await page.getByLabel('Tipo do item').selectOption('event');
  await page.getByRole('button', { name: 'Publicar' }).click();
  await expectToast(page, 'Publicado na agenda.');

  await page.goto('/admin/secretariat/agenda');
  await page.getByLabel('Período letivo').selectOption({ label: `Período ${name}` });
  await page.getByLabel('Turma').selectOption({ label: name });
  await expect(page.getByText(`Reunião de pais ${suffix}`)).toBeVisible();
  await page.getByLabel('Título do item').fill(`Prova de ciências ${suffix}`);
  await page.getByLabel('Tipo do item').selectOption('test');
  await page.getByRole('button', { name: 'Publicar' }).click();
  await expectToast(page, 'Publicado na agenda.');
  await expect(page.getByText(`Prova de ciências ${suffix}`)).toBeVisible();
});
