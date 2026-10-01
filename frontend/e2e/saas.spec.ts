import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('plataforma cria plano, atribui a instituicao e fatura; a instituicao ve o plano', async ({ page }) => {
  const suffix = uniqueSuffix();
  const planName = `Ilimitado ${suffix}`;
  // Um periodo novo a cada execucao: a fatura e unica por assinatura e periodo.
  const year = 2100 + (Date.now() % 7000);

  await login(page, users.root);
  await page.goto('/platform/plans');
  await page.getByLabel('Nome do plano').fill(planName);
  await page.getByLabel('Preço mensal').fill('990,00');
  await page.getByRole('button', { name: 'Criar plano' }).click();
  await expectToast(page, 'Plano criado.');

  await page.goto('/platform/institutions');
  await page.getByRole('link', { name: 'Plano de Escola Alfa' }).click();
  await page.getByLabel('Plano da instituição').selectOption({ label: planName });
  await page.getByLabel('Situação da assinatura').selectOption('active');
  await page.getByRole('button', { name: 'Salvar plano' }).click();
  await expectToast(page, 'Plano atualizado.');
  await expect(page.getByText(/Alunos ativos: \d+ \(sem limite\)/)).toBeVisible();
  await page.getByLabel('Início do período da fatura').fill(`${year}-01-01`);
  await page.getByRole('button', { name: 'Gerar fatura do período' }).click();
  await expectToast(page, 'Fatura gerada.');
  await expect(page.getByText(new RegExp(`01/01/${year} a 31/01/${year} · ${planName}`))).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.admin);
  await page.goto('/admin/institution');
  await expect(page.getByRole('heading', { name: 'Plano contratado' })).toBeVisible();
  await expect(page.getByText(planName).first()).toBeVisible();
});
