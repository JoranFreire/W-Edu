import { createStudent } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

// Escola Alfa (tipo "school"): nomenclatura "Ano letivo" e "Bimestre".
async function createTerm(page: import('@playwright/test').Page, name: string) {
  await page.goto('/admin/academic');
  await page.getByRole('tab', { name: /Anos letivos/ }).click();
  await page.getByRole('button', { name: 'Novo ano letivo' }).click();
  const dialog = page.getByRole('dialog', { name: 'Novo ano letivo' });
  await dialog.getByLabel('Nome').fill(name);
  await dialog.getByLabel('Regime').selectOption('year');
  await dialog.getByLabel('Início').fill('2031-02-03');
  await dialog.getByLabel('Fim').fill('2031-02-28');
  await dialog.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Período salvo.');
}

test.beforeEach(async ({ page }) => {
  await login(page, users.admin);
});

test('ano letivo: bimestre, feriado e contagem de dias letivos', async ({ page }) => {
  const name = `AL ${uniqueSuffix()}`;
  await createTerm(page, name);
  await page.getByRole('link', { name }).click();

  await page.getByRole('button', { name: 'Iniciar período' }).click();
  await expectToast(page, 'Situação do período atualizada.');
  await expect(page.getByText('Em andamento')).toBeVisible();

  await page.getByLabel('Nome da etapa').fill('1º bimestre');
  await page.getByLabel('Início da etapa').fill('2031-02-03');
  await page.getByLabel('Fim da etapa').fill('2031-02-28');
  await page.getByRole('button', { name: 'Adicionar etapa' }).click();
  await expectToast(page, 'Etapa criada.');

  await page.getByLabel('Tipo de evento').selectOption('holiday');
  await page.getByLabel('Título do evento').fill('Carnaval');
  await page.getByLabel('Data do evento').fill('2031-02-24');
  await page.getByRole('button', { name: 'Adicionar', exact: true }).click();
  await expectToast(page, 'Evento adicionado.');

  // 20 dias uteis em 03-28/02/2031, menos o feriado.
  const schoolDays = page.locator('dt', { hasText: 'Dias letivos' }).first().locator('xpath=following-sibling::dd');
  await expect(schoolDays).toHaveText('19');

  await page.getByRole('button', { name: 'Encerrar período' }).click();
  await expect(page.getByText('Encerrado').first()).toBeVisible();
  await expect(page.getByRole('button', { name: 'Adicionar etapa' })).toHaveCount(0);
});

test('matricula no programa e alocacao na turma', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluna ${suffix}`);
  const termName = `AL ${suffix}`;
  const groupName = `6º A ${suffix}`;
  await createTerm(page, termName);

  await page.getByRole('tab', { name: /Matrículas/ }).click();
  await page.getByRole('button', { name: 'Nova matrícula' }).click();
  const enrollDialog = page.getByRole('dialog', { name: 'Nova matrícula' });
  await enrollDialog.getByLabel('Aluno').selectOption({ label: `${student.name} (${student.email})` });
  await enrollDialog.getByLabel('Etapa de ensino').selectOption({ label: 'EF-E2E · Fundamental E2E' });
  await enrollDialog.getByLabel(/Ingresso/).selectOption({ label: termName });
  await enrollDialog.getByRole('button', { name: 'Matricular' }).click();
  await expectToast(page, 'Matrícula 2031EFE2E');
  await expect(page.getByRole('row', { name: new RegExp(student.name) })).toContainText('2031EFE2E');

  await page.getByRole('tab', { name: /Turmas/ }).click();
  await page.getByRole('button', { name: 'Nova turma' }).click();
  const groupDialog = page.getByRole('dialog', { name: 'Nova turma' });
  await groupDialog.getByLabel('Etapa de ensino').selectOption({ label: 'EF-E2E · Fundamental E2E' });
  await groupDialog.getByLabel('Ano letivo').selectOption({ label: termName });
  await groupDialog.getByLabel('Nome').fill(groupName);
  await groupDialog.getByLabel('Série da matriz').fill('6');
  await groupDialog.getByLabel('Vagas').fill('30');
  await groupDialog.getByLabel('Professor responsável').selectOption({ label: 'Instrutor Alfa' });
  await groupDialog.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Turma salva.');

  await page.getByLabel('Filtrar por ano letivo').selectOption({ label: termName });
  await page.getByRole('link', { name: groupName }).click();
  const candidate = page.getByLabel('Aluno para incluir');
  const value = await candidate.locator('option', { hasText: student.name }).getAttribute('value');
  await candidate.selectOption(value ?? '');
  await page.getByRole('button', { name: 'Incluir' }).click();
  await expectToast(page, 'Aluno incluído na turma.');
  await expect(page.getByText('Alunos (1)')).toBeVisible();
  await expect(page.getByRole('listitem').filter({ hasText: student.name })).toBeVisible();
});
