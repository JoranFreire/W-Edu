import { createStudent, enrollInSeedProgram, linkGuardian } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('secretaria emite contrato, responsavel financeiro aceita e o codigo valida', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Contrato ${suffix}`);
  const enrollment = await enrollInSeedProgram(request, student.id);
  const guardianEmail = `resp.contrato.${suffix}@alfa.example.com`;
  await linkGuardian(request, student.id, `Responsável ${suffix}`, guardianEmail, 'escola-alfa', true);
  const templateName = `Matrícula ${suffix}`;

  await login(page, users.admin);
  await page.goto('/admin/secretariat/contracts');
  await page.getByRole('button', { name: 'Novo modelo' }).click();
  const modal = page.getByRole('dialog', { name: 'Novo modelo de contrato' });
  await modal.getByLabel('Nome').fill(templateName);
  await modal.getByLabel('Texto do contrato').fill('Contrato entre {institution_name} e {payer_name}, responsável por {student_name}.\n\nCláusula de pagamento.');
  await modal.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Modelo salvo.');

  await page.goto(`/admin/secretariat/enrollments/${enrollment.id}`);
  await page.getByRole('tab', { name: /Contratos/ }).click();
  await page.getByLabel('Modelo de contrato').selectOption({ label: templateName });
  await page.getByRole('button', { name: 'Emitir contrato' }).click();
  await expectToast(page, 'Contrato emitido.');
  await expect(page.getByText('Aguardando aceite')).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, guardianEmail);
  await page.getByRole('link', { name: 'Contratos' }).first().click();
  const card = page.getByRole('listitem').filter({ hasText: templateName });
  await card.getByText('Ler o contrato').click();
  await expect(card.getByText(`Contrato entre Escola Alfa e Responsável ${suffix}, responsável por ${student.name}.`)).toBeVisible();
  const code = (await card.locator('span.font-mono').textContent()) ?? '';
  page.once('dialog', (dialog) => dialog.accept());
  await card.getByRole('button', { name: /^Aceitar/ }).click();
  await expectToast(page, 'Contrato aceito.');
  await expect(card.getByText('Aceito', { exact: true })).toBeVisible();

  await page.goto(`/validate-contract?code=${code}`);
  await expect(page.getByText('Contrato aceito e íntegro')).toBeVisible();
  await expect(page.getByText(`Responsável ${suffix} em`)).toBeVisible();
});
