import { createFreeOffering } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

/** Data/hora local para `<input type="datetime-local">`. */
function localInput(offsetMs: number) {
  const date = new Date(Date.now() + offsetMs);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
}

test('edital publico: inscricao sem conta, comprovante, selecao e confirmacao da vaga', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const offeringName = `Turma Social ${suffix}`;
  await createFreeOffering(request, offeringName);
  const title = `Auxiliar administrativo ${suffix}`;
  const email = `candidato.${suffix}@alfa.example.com`;

  await login(page, users.admin);
  await page.goto('/admin/secretariat/admissions');
  await page.getByRole('button', { name: 'Novo edital' }).click();
  const modal = page.getByRole('dialog', { name: 'Novo edital' });
  await modal.getByLabel('Título').fill(title);
  await modal.getByLabel('Turma').selectOption({ label: `${offeringName} (20 lugares)` });
  await modal.getByLabel('Vagas', { exact: true }).fill('2');
  await modal.getByLabel('Abertura das inscrições').fill(localInput(-3_600_000));
  await modal.getByLabel('Encerramento').fill(localInput(86_400_000));
  await modal.getByLabel(/Comprovantes/).fill('RG');
  await modal.getByRole('button', { name: 'Criar edital' }).click();
  await expectToast(page, 'Edital criado.');
  await page.getByRole('button', { name: 'Abrir inscrições' }).click();
  await expectToast(page, 'Inscrições abertas.');

  await page.evaluate(() => window.localStorage.clear());
  await page.goto('/inscricoes?institution=escola-alfa');
  await page.getByRole('link', { name: new RegExp(title) }).click();
  await page.getByLabel('Nome completo').fill(`Candidato ${suffix}`);
  await page.getByLabel('E-mail').fill(email);
  await page.getByLabel('Senha').fill('e2e-senha-123');
  await page.getByLabel('Data de nascimento').fill('2000-01-15');
  await page.getByLabel('Cidade onde mora').fill('Recife');
  await page.getByLabel(/Renda total/).fill('1500,00');
  await page.getByLabel('Pessoas na família').fill('3');
  await page.getByRole('button', { name: 'Confirmar inscrição' }).click();
  await expectToast(page, 'Inscrição enviada.');
  await expect(page.getByRole('heading', { name: 'Minhas inscrições' })).toBeVisible();
  await expect(page.getByText('Inscrição recebida')).toBeVisible();
  await page.getByLabel('Arquivo do comprovante').setInputFiles({ name: 'rg.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 rg') });
  await page.getByRole('button', { name: 'Enviar comprovante' }).click();
  await expectToast(page, 'Comprovante enviado.');
  await expect(page.getByText('RG: rg.pdf · Em conferência')).toBeVisible();

  await page.evaluate(() => window.localStorage.clear());
  await login(page, users.admin);
  await page.goto('/admin/secretariat/admissions');
  await page.getByRole('link', { name: title }).click();
  await page.getByRole('button', { name: `Aceitar RG de Candidato ${suffix}` }).click();
  await expectToast(page, 'Comprovante conferido.');
  await page.getByRole('button', { name: 'Encerrar inscrições' }).click();
  await expectToast(page, 'Inscrições encerradas.');
  await page.getByRole('button', { name: 'Executar seleção' }).click();
  await expectToast(page, '1 convocado(s), 0 em espera.');

  await page.evaluate(() => window.localStorage.clear());
  await login(page, email);
  await page.getByRole('link', { name: 'Inscrições' }).first().click();
  await page.getByRole('button', { name: `Confirmar vaga em ${title}` }).click();
  await expectToast(page, 'Vaga confirmada.');
  await expect(page.getByText('Matriculado')).toBeVisible();
});
