import { createStudent } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { createRegistrationScenario } from './support/registration';
import { users } from './support/users';

test('aluno se inscreve na janela; choque de horario e pre-requisito ficam bloqueados', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Matricula ${suffix}`);
  await createRegistrationScenario(request, suffix, student.id);

  await login(page, student.email);
  await page.getByRole('link', { name: 'Matrícula em disciplinas' }).first().click();
  await expect(page.getByRole('heading', { name: new RegExp(`Matrícula ${suffix}`) })).toBeVisible();
  await page.getByRole('button', { name: new RegExp(`^Inscrever em INTRO${suffix}`, 'i') }).click();
  await expectToast(page, 'Inscrição confirmada.');
  await expect(page.getByText(/Choque de horário com INTRO T1/)).toBeVisible();
  await expect(page.getByText(new RegExp(`Pré-requisito pendente: INTRO ${suffix}`))).toBeVisible();
  await expect(page.getByText('4 crédito(s) inscrito(s)', { exact: false })).toBeVisible();

  page.once('dialog', (dialog) => dialog.accept());
  await page.getByRole('button', { name: new RegExp(`^Cancelar INTRO${suffix}`, 'i') }).click();
  await expectToast(page, 'Inscrição cancelada.');
});

test('secretaria abre janela, define horario e inscreve com excecao pela ficha', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Secretaria Mat ${suffix}`);
  const scenario = await createRegistrationScenario(request, suffix, student.id);

  await login(page, users.admin);
  await page.goto('/admin/secretariat/registration');
  await page.getByRole('button', { name: 'Nova janela' }).click();
  await page.getByLabel('Nome').fill(`Ajuste ${suffix}`);
  await page.getByLabel('Período letivo').selectOption({ label: scenario.termName });
  await page.getByLabel('Abertura').fill('2032-01-10T08:00');
  await page.getByLabel('Fechamento').fill('2032-01-20T18:00');
  await page.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Janela salva.');
  await expect(page.getByText(`Ajuste ${suffix}`)).toBeVisible();

  await page.goto('/admin/schedule');
  await page.getByRole('button', { name: `Horários de AVANC T1 ${suffix}` }).click();
  await expect(page.getByText('Terça 08:00–10:00')).toBeVisible();
  await page.getByRole('button', { name: 'Fechar modal' }).click();

  await page.goto('/admin/secretariat');
  await page.getByRole('link', { name: new RegExp(student.name) }).first().click();
  await page.getByRole('tab', { name: /Disciplinas/ }).click();
  await page.getByLabel('Período das disciplinas').selectOption({ label: scenario.termName });
  page.once('dialog', (dialog) => dialog.accept());
  await page.getByRole('button', { name: new RegExp(`^Inscrever com exceção em AVANC${suffix}`, 'i') }).click();
  await expectToast(page, 'Inscrição confirmada.');
  await expect(page.getByRole('button', { name: new RegExp(`^Cancelar AVANC${suffix}`, 'i') })).toBeVisible();
});
