import { createClosedMeeting, createFreeOffering, createStudent, joinOffering } from './support/api';
import { createBenefitItemWithStock } from './support/benefits';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('lanche liberado com QR: o aluno ve o QR e a equipe valida a retirada', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const offering = await createFreeOffering(request, `Cantina ${suffix}`);
  const student = await createStudent(request, `Aluna QR ${suffix}`);
  await joinOffering(request, offering.id, student.email);
  const item = await createBenefitItemWithStock(request, `Lanche QR ${suffix}`, 5);
  await createClosedMeeting(request, offering.id, `Aula ${suffix}`, [student.id]);

  await login(page, users.admin);
  await page.goto(`/teaching/offerings/${offering.id}`);
  await page.getByRole('tab', { name: /Benefícios/ }).click();
  await page.getByLabel('Encontro', { exact: true }).selectOption({ index: 1 });
  await page.getByLabel('Item liberado').selectOption({ label: `${item.name} (disponível 5)` });
  await page.getByRole('button', { name: 'Liberar com QR' }).click();
  await expectToast(page, '1 benefício(s) liberado(s); disponível no estoque: 4.');
  await expect(page.getByText(`${student.name} · ${item.name} × 1`)).toBeVisible();

  const studentPage = await page.context().browser()!.newPage();
  await login(studentPage, student.email);
  await studentPage.goto('/benefits');
  await expect(studentPage.getByRole('img', { name: `QR do benefício ${item.name}` })).toBeVisible();
  const code = (await studentPage.locator('p.font-mono').first().textContent())!.trim();
  await studentPage.close();

  await page.goto('/benefit-validation');
  await page.getByLabel('Código do benefício').fill(code);
  await page.getByRole('button', { name: 'Conferir' }).click();
  await expect(page.getByText(student.name)).toBeVisible();
  await page.getByRole('button', { name: 'Confirmar retirada' }).click();
  await expect(page.getByText('Retirada confirmada.')).toBeVisible();
  await page.getByRole('button', { name: 'Ler o próximo' }).click();
  await page.getByLabel('Código do benefício').fill(code);
  await page.getByRole('button', { name: 'Conferir' }).click();
  await expect(page.getByText('Este QR não pode ser usado.')).toBeVisible();

  await page.goto(`/teaching/offerings/${offering.id}`);
  await page.getByRole('tab', { name: /Benefícios/ }).click();
  await expect(page.getByText(new RegExp(`${item.name} × 1 · ${student.name}`))).toBeVisible();
});
