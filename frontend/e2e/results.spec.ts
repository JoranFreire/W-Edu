import { createOfferingWithStudent, createStudent } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('resultado: recuperacao, publicacao e boletim do aluno', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Resultado ${suffix}`);
  const offeringName = `Turma Resultado ${suffix}`;
  const offering = await createOfferingWithStudent(request, offeringName, student.email);
  page.on('dialog', (dialog) => dialog.accept());

  await login(page, users.admin);
  await page.goto(`/teaching/offerings/${offering.id}`);
  await page.getByRole('tab', { name: /Avaliações e notas/ }).click();
  await page.getByLabel('Nome da avaliação').fill('Prova final');
  await page.getByRole('button', { name: 'Incluir', exact: true }).click();
  await expectToast(page, 'Avaliação incluída.');
  await page.getByRole('button', { name: 'Lançar notas de Prova final' }).click();
  await page.getByLabel(`Nota de ${student.name}`).fill('5');
  await page.getByRole('button', { name: 'Salvar notas' }).click();
  await expectToast(page, 'Notas salvas.');

  await page.getByRole('tab', { name: /Resultado/ }).click();
  await page.getByRole('button', { name: 'Calcular resultado' }).click();
  await expectToast(page, 'Resultado calculado.');
  const row = page.getByRole('row', { name: new RegExp(student.name) });
  await expect(row).toContainText('Recuperação');

  await page.getByLabel(`Recuperação de ${student.name}`).fill('7');
  await page.getByRole('button', { name: 'Salvar recuperação' }).click();
  await expectToast(page, 'Recuperação salva.');
  await expect(row).toContainText('Aprovado');

  await page.getByRole('button', { name: 'Publicar resultado' }).click();
  await expectToast(page, 'Resultado publicado.');
  await expect(page.getByText('Resultado publicado').first()).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, student.email);
  await page.getByRole('link', { name: 'Boletim' }).first().click();
  const card = page.getByRole('listitem').filter({ hasText: offeringName });
  await expect(card).toContainText('Aprovado');
  await expect(card).toContainText('7');
});
