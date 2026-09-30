import { createOpenTerm, createStudent } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

// Programa EF-E2E do seed: matriz vigente com MAT-E2E.
test('secretaria: matricula, rematricula, trancamento, aproveitamento e historico', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluna Secretaria ${suffix}`);
  const termName = `AL ${suffix}`;
  await createOpenTerm(request, termName);
  page.on('dialog', (dialog) => dialog.accept('Ementa compatível'));

  await login(page, users.admin);
  await page.getByRole('link', { name: 'Secretaria' }).first().click();
  await page.getByRole('button', { name: 'Nova matrícula' }).click();
  const dialog = page.getByRole('dialog', { name: 'Nova matrícula' });
  await dialog.getByLabel('Aluno').selectOption({ label: `${student.name} (${student.email})` });
  await dialog.getByLabel('Etapa de ensino').selectOption({ label: 'EF-E2E · Fundamental E2E' });
  await dialog.getByRole('button', { name: 'Matricular' }).click();
  await expectToast(page, 'criada.');

  await page.getByLabel('Buscar matrícula').fill(student.name);
  await page.getByRole('link', { name: new RegExp(student.name) }).click();
  await expect(page.getByRole('heading', { name: student.name })).toBeVisible();

  await page.getByRole('button', { name: 'Rematricular' }).click();
  await page.getByRole('dialog').getByLabel('Período letivo').selectOption({ label: termName });
  await page.getByRole('dialog').getByLabel(/Série\/semestre/).fill('6');
  await page.getByRole('button', { name: 'Confirmar' }).click();
  await expectToast(page, 'Rematricular: registrado.');

  await page.getByRole('button', { name: 'Trancar' }).click();
  await page.getByRole('dialog').getByLabel('Justificativa').fill('Tratamento de saúde');
  await page.getByRole('button', { name: 'Confirmar' }).click();
  await expectToast(page, 'Trancar: registrado.');
  await expect(page.getByText(/· Trancada/)).toBeVisible();
  await page.getByRole('button', { name: 'Reativar' }).click();
  await page.getByRole('button', { name: 'Confirmar' }).click();
  await expectToast(page, 'Reativar: registrado.');

  await page.getByRole('tab', { name: /Movimentações/ }).click();
  await expect(page.getByText('Tratamento de saúde')).toBeVisible();
  await expect(page.getByText(`${termName} · 6º série`)).toBeVisible();

  await page.getByRole('tab', { name: /Aproveitamento/ }).click();
  await page.getByLabel('Disciplina a aproveitar').selectOption({ label: 'MAT-E2E · Matemática E2E' });
  await page.getByLabel('Instituição de origem').fill('Escola Antiga');
  await page.getByLabel('Disciplina cursada').fill('Matemática 6º ano');
  await page.getByLabel('Nota de origem').fill('9');
  await page.getByRole('button', { name: 'Registrar', exact: true }).click();
  await expectToast(page, 'Aproveitamento registrado para análise.');
  await page.getByRole('button', { name: 'Deferir MAT-E2E', exact: true }).click();
  await expectToast(page, 'Aproveitamento deferido.');

  await page.getByRole('tab', { name: /Histórico escolar/ }).click();
  await expect(page.getByRole('row', { name: /MAT-E2E/ })).toContainText('Aproveitada');

  // Com a matriz integralizada (aproveitamento), a secretaria conclui o programa e emite a declaracao.
  await page.getByRole('tab', { name: /Documentos e conclusão/ }).click();
  await page.getByLabel('Tipo de declaração').selectOption('enrollment');
  await page.getByRole('button', { name: 'Emitir declaração' }).click();
  await expectToast(page, 'Declaração emitida.');
  await page.getByRole('button', { name: 'Concluir programa' }).click();
  await expectToast(page, 'Programa concluído.');
  await expect(page.getByText(/Concluído em/)).toBeVisible();
  await page.getByLabel('Tipo de declaração').selectOption('completion');
  await page.getByRole('button', { name: 'Emitir declaração' }).click();
  await expectToast(page, 'Declaração emitida.');
  const code = (await page.getByRole('listitem').filter({ hasText: 'Conclusão ·' }).locator('.font-mono').first().textContent())?.trim() ?? '';

  await page.goto(`/validate-declaration?code=${code}`);
  await expect(page.getByRole('status')).toContainText('Declaração válida');
  await expect(page.getByRole('status')).toContainText(student.name);

  await page.evaluate(() => window.localStorage.clear());
  await login(page, student.email);
  await page.getByRole('link', { name: 'Histórico escolar' }).first().click();
  await expect(page.getByRole('row', { name: /MAT-E2E/ })).toContainText('Aproveitada');
  await expect(page.getByText('Escola Antiga')).toBeVisible();
  await expect(page.getByText('Minhas declarações')).toBeVisible();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Baixar PDF' }).first().click();
  expect((await download).suggestedFilename()).toMatch(/^declaracao_.*\.pdf$/);
});

test('aluno nao acessa a secretaria', async ({ page }) => {
  await login(page, users.aluno);
  await page.goto('/admin/secretariat');
  await expect(page.getByRole('heading', { name: 'Acesso restrito' })).toBeVisible();
});
