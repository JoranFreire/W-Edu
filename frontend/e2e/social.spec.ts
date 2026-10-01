import { createClosedMeeting, createFreeOffering, createStudent, joinOffering } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('financiador, lanche so para presentes, desligamento por faltas e prestacao de contas', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const offeringName = `Cozinha ${suffix}`;
  const offering = await createFreeOffering(request, offeringName);
  const present = await createStudent(request, `Aluna Presente ${suffix}`);
  const absent = await createStudent(request, `Aluno Faltoso ${suffix}`);
  await joinOffering(request, offering.id, present.email);
  await joinOffering(request, offering.id, absent.email);
  const fundingName = `Convênio ${suffix}`;
  const itemName = `Lanche ${suffix}`;

  await login(page, users.admin);
  await page.goto('/admin/secretariat/social');
  await page.getByLabel('Nome do financiador').fill(fundingName);
  await page.getByLabel('Valor do financiamento').fill('1000,00');
  await page.getByRole('button', { name: 'Cadastrar financiador' }).click();
  await expectToast(page, 'Financiador cadastrado.');
  await page.getByLabel(`Financiador da turma ${offeringName}`).selectOption({ label: fundingName });
  await page.getByLabel(`Limite de faltas da turma ${offeringName}`).fill('40');
  await page.getByRole('button', { name: `Salvar turma ${offeringName}` }).click();
  await expectToast(page, 'Turma atualizada.');
  await page.getByLabel('Nome do item').fill(itemName);
  await page.getByLabel('Custo unitário').fill('5,00');
  await page.getByRole('button', { name: 'Cadastrar item' }).click();
  await expectToast(page, 'Item cadastrado.');
  await page.getByLabel(`Quantidade de ${itemName}`).fill('10');
  await page.getByLabel(`Financiador de ${itemName}`).selectOption({ label: fundingName });
  await page.getByRole('button', { name: `Lançar entrada de ${itemName}` }).click();
  await expectToast(page, 'Estoque atualizado.');

  await createClosedMeeting(request, offering.id, `Aula 1 ${suffix}`, [present.id]);

  await page.goto(`/teaching/offerings/${offering.id}`);
  await page.getByRole('tab', { name: /Benefícios/ }).click();
  await page.getByLabel('Encontro da entrega').selectOption({ index: 1 });
  await page.getByLabel('Item entregue').selectOption({ label: `${itemName} (disponível 10)` });
  await page.getByRole('button', { name: 'Registrar entrega' }).click();
  await expectToast(page, '1 entrega(s) registrada(s); estoque restante: 9.');
  await expect(page.getByText(`${itemName} × 1 · ${present.name}`)).toBeVisible();
  await page.getByRole('tab', { name: /Frequência e evasão/ }).click();
  await expect(page.getByText(/Desligado: 1 falta\(s\) em 1 sessões previstas/)).toBeVisible();

  await page.goto('/admin/secretariat/social');
  await page.getByRole('listitem').filter({ hasText: fundingName }).getByRole('link', { name: 'Prestação de contas' }).click();
  await expect(page.getByRole('heading', { name: `Prestação de contas: ${fundingName}` })).toBeVisible();
  await expect(page.getByRole('row', { name: new RegExp(`${offeringName} 0 2 1 0 1 0 50%`) })).toBeVisible();
  await expect(page.getByText(`${itemName}: 1 unidade · R$ 5,00`)).toBeVisible();
});
