import { createOpenTerm, createStudent, linkGuardian } from './support/api';
import { createCompletionScenario } from './support/completion';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('bolsa, plano de mensalidade, baixa e extrato do responsavel financeiro', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const student = await createStudent(request, `Aluno Mensalidade ${suffix}`);
  const { enrollmentId } = await createCompletionScenario(request, suffix, student.id);
  const term = `Ano ${suffix}`;
  await createOpenTerm(request, term);
  const guardianEmail = `resp.financeiro.${suffix}@alfa.example.com`;
  await linkGuardian(request, student.id, `Responsável ${suffix}`, guardianEmail, 'escola-alfa', true);
  const fileUrl = `/admin/secretariat/enrollments/${enrollmentId}`;

  await login(page, users.admin);
  await page.goto(fileUrl);
  await page.getByRole('tab', { name: /Financeiro/ }).click();
  await page.getByLabel('Valor do desconto').fill('50');
  await page.getByLabel('Início da vigência').fill('2020-01-01');
  await page.getByRole('button', { name: 'Conceder' }).click();
  await expectToast(page, 'Desconto concedido.');
  await expect(page.getByText(/Bolsa de 50%/)).toBeVisible();

  await page.goto('/admin/finance/tuition');
  await page.getByRole('button', { name: 'Novo plano' }).click();
  const modal = page.getByRole('dialog', { name: 'Novo plano de mensalidade' });
  await modal.getByLabel('Nome').fill(`Mensalidade ${suffix}`);
  await modal.getByLabel('Período letivo').selectOption({ label: term });
  await modal.getByLabel(/^Programa/).selectOption({ label: `TC${suffix.toUpperCase()} · Bacharelado ${suffix}` });
  await modal.getByLabel(/Valor da parcela/).fill('800,00');
  await modal.getByLabel('Parcelas').fill('2');
  await modal.getByLabel('Primeiro vencimento').fill('2032-02-10');
  await modal.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Plano criado.');
  await page.getByRole('button', { name: `Gerar cobranças de Mensalidade ${suffix}` }).click();
  await expectToast(page, '2 parcela(s) gerada(s) para 1 matrícula(s); 0 já existia(m).');

  await page.goto(fileUrl);
  await page.getByRole('tab', { name: /Financeiro/ }).click();
  await expect(page.getByText(`Mensalidade ${suffix} — parcela 1/2`)).toBeVisible();
  await expect(page.getByText(/R\$\s?800,00 − R\$\s?400,00 de desconto/).first()).toBeVisible();
  await page.getByLabel(`Data do pagamento de Mensalidade ${suffix} — parcela 1/2`).fill('2032-02-10');
  await page.getByRole('button', { name: `Registrar pagamento de Mensalidade ${suffix} — parcela 1/2` }).click();
  await expectToast(page, 'Pagamento registrado.');
  await expect(page.getByText(/Pago: R\$\s?400,00/)).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, guardianEmail);
  await page.getByRole('link', { name: 'Mensalidades' }).first().click();
  await expect(page.getByRole('heading', { name: 'Mensalidades' })).toBeVisible();
  await expect(page.getByText(`${student.name} · Mensalidade ${suffix} — parcela 2/2`)).toBeVisible();
});
