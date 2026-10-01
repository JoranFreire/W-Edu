import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('professor requisita material, almoxarifado aprova parcialmente e registra a retirada', async ({ page }) => {
  const suffix = uniqueSuffix();
  const material = `Papel crepom ${suffix}`;
  const purpose = `Festa junina ${suffix}`;

  await login(page, users.admin);
  await page.getByRole('link', { name: 'Almoxarifado' }).first().click();
  await page.getByRole('tab', { name: /Materiais/ }).click();
  await page.getByLabel('Nome do material').fill(material);
  await page.getByLabel('Unidade do material').fill('pacote');
  await page.getByLabel('Estoque mínimo').fill('2');
  await page.getByLabel('Custo unitário do material').fill('3,50');
  await page.getByRole('button', { name: 'Cadastrar' }).click();
  await expectToast(page, 'Material cadastrado.');
  await page.getByLabel(`Quantidade recebida de ${material}`).fill('10');
  await page.getByRole('button', { name: `Lançar entrada de ${material}` }).click();
  await expectToast(page, 'Entrada registrada.');

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.instrutor);
  await page.getByRole('link', { name: 'Requisições de material' }).first().click();
  await page.getByLabel('Finalidade').fill(purpose);
  await page.getByLabel('Data de uso').fill('2032-06-20');
  await page.getByLabel('Material 1').selectOption({ label: `${material} (10 pacote disponível(is))` });
  await page.getByLabel('Quantidade 1').fill('6');
  await page.getByRole('button', { name: 'Enviar requisição' }).click();
  await expectToast(page, 'Requisição enviada para aprovação.');
  await expect(page.getByText('Aguardando aprovação')).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.admin);
  await page.goto('/admin/warehouse');
  await page.getByLabel(`Aprovar ${material}`).fill('4');
  await page.getByRole('button', { name: `Aprovar requisição ${purpose}` }).click();
  await expectToast(page, 'Requisição analisada.');
  await page.getByLabel('Situação das requisições').selectOption('approved');
  await page.getByRole('button', { name: `Registrar retirada de ${purpose}` }).click();
  await expectToast(page, 'Retirada registrada.');

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.instrutor);
  await page.getByRole('link', { name: 'Requisições de material' }).first().click();
  const card = page.getByRole('listitem').filter({ hasText: purpose });
  await expect(card.getByText('Concluída')).toBeVisible();
  await expect(card.getByText(`${material}: 6 pacote pedido(s) · 4 aprovado(s) · 4 retirado(s)`)).toBeVisible();
});
