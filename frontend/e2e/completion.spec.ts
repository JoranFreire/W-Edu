import { createStudent } from './support/api';
import { createCompletionScenario } from './support/completion';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('atividades, estagio e TCC levam a integralizacao completa', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Conclusao ${suffix}`);
  const { enrollmentId } = await createCompletionScenario(request, suffix, student.id);
  const fileUrl = `/admin/secretariat/enrollments/${enrollmentId}`;

  // Aluno declara a atividade complementar.
  await login(page, student.email);
  await page.getByRole('link', { name: 'Integralização' }).first().click();
  await expect(page.getByText('0h de 10h')).toBeVisible();
  await page.getByRole('tab', { name: /Atividades complementares/ }).click();
  await page.getByLabel('Título da atividade').fill(`Monitoria ${suffix}`);
  await page.getByLabel('Horas da atividade').fill('10');
  await page.getByRole('button', { name: 'Enviar atividade' }).click();
  await expectToast(page, 'Atividade enviada para análise.');

  // Secretaria aprova, cadastra o estagio e o TCC com o Instrutor Alfa como orientador.
  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.admin);
  await page.goto(fileUrl);
  await page.getByRole('tab', { name: /Integralização/ }).click();
  await page.getByRole('button', { name: `Aprovar Monitoria ${suffix}` }).click();
  await expectToast(page, 'Atividade aprovada.');
  await expect(page.getByText('10h de 10h')).toBeVisible();
  await page.getByRole('tab', { name: /Estágio e TCC/ }).click();
  await page.getByRole('button', { name: 'Novo estágio' }).click();
  const modal = page.getByRole('dialog', { name: 'Novo estágio' });
  await modal.getByLabel('Concedente', { exact: true }).fill(`Escritório ${suffix}`);
  await modal.getByLabel('Orientador').selectOption({ label: 'Instrutor Alfa' });
  await modal.getByLabel('Início').fill('2026-01-05');
  await modal.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Estágio cadastrado.');
  await page.getByLabel('Título do TCC').fill(`Tema ${suffix}`);
  await page.getByLabel('Orientador do TCC').selectOption({ label: 'Instrutor Alfa' });
  await page.getByRole('button', { name: 'Salvar TCC' }).click();
  await expectToast(page, 'TCC salvo.');

  // Aluno lanca as horas de estagio.
  await page.evaluate(() => window.localStorage.clear());
  await login(page, student.email);
  await page.goto('/completion');
  await page.getByRole('tab', { name: /Estágio/ }).click();
  await page.getByLabel('Horas no dia').fill('4');
  await page.getByLabel('Atividades do dia').fill('Pesquisa de jurisprudência');
  await page.getByRole('button', { name: 'Registrar' }).click();
  await expectToast(page, 'Horas registradas.');

  // Orientador valida as horas e registra entrega e defesa do TCC.
  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.instrutor);
  await page.getByRole('link', { name: 'Orientações' }).first().click();
  await page.getByRole('button', { name: /^Validar / }).first().click();
  await expectToast(page, 'Horas validadas.');
  await page.getByRole('button', { name: `Registrar entrega de Tema ${suffix}` }).click();
  await expectToast(page, 'Entrega registrada.');
  await page.getByLabel('Nota do TCC').fill('9');
  await page.getByRole('button', { name: `Aprovar Tema ${suffix}` }).click();
  await expectToast(page, 'Resultado registrado.');

  // Secretaria ve todos os requisitos cumpridos.
  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.admin);
  await page.goto(fileUrl);
  await page.getByRole('tab', { name: /Integralização/ }).click();
  await expect(page.getByText('Todos os requisitos cumpridos')).toBeVisible();
});
