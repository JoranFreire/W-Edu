import { API_URL } from './support/api';
import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('dominio da plataforma: pagina de contratacao e o interessado chega a administracao', async ({ page }) => {
  const institution = `Colégio Interessado ${uniqueSuffix()}`;
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Da matrícula ao certificado');
  await expect(page.locator('#planos')).toBeVisible();

  const contact = page.locator('#contato');
  await contact.getByLabel('Seu nome *').fill('Diretora Teste');
  await contact.getByLabel('E-mail *').fill(`diretora.${uniqueSuffix()}@example.com`);
  await contact.getByLabel('Instituição *').fill(institution);
  await contact.getByLabel('Tipo de instituição').selectOption('vocational');
  await contact.getByLabel('Quantos alunos, aproximadamente?').fill('250');
  await contact.getByLabel('Mensagem').fill('Queremos ver o módulo de editais.');
  await contact.getByRole('button', { name: 'Quero conversar' }).click();
  await expect(page.getByRole('status')).toContainText('Recebemos seu interesse');

  await login(page, users.root);
  await page.goto('/platform/leads');
  const leads = page.getByRole('list', { name: 'Interessados' });
  await expect(leads.getByText(institution)).toBeVisible();
  await leads.getByLabel(`Etapa de ${institution}`).selectOption('contacted');
  await expectToast(page, 'Interessado atualizado.');
});

test('pagina da instituicao: conteudo editado pelo admin, por slug e pelo dominio proprio', async ({ page, request }) => {
  const tagline = `Educação que transforma ${uniqueSuffix()}`;
  await login(page, users.admin);
  await page.goto('/admin/institution');
  const section = page.getByRole('region', { name: 'Página pública' });
  await section.getByLabel('Frase de destaque').fill(tagline);
  await section.getByLabel('Telefone').fill('81 3333-0000');
  await section.getByRole('button', { name: 'Salvar página pública' }).click();
  await expectToast(page, 'Página pública atualizada.');

  await page.goto('/instituicao/escola-alfa');
  await expect(page.getByText(tagline)).toBeVisible();
  await expect(page.getByRole('link', { name: 'Área do aluno', exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Contato' }).getByText('81 3333-0000')).toBeVisible();

  // Dominio proprio: o mesmo endereco raiz passa a mostrar a instituicao em vez da contratacao.
  const domain = `escola-${uniqueSuffix()}.example.com`;
  const rootLogin = await request.post(`${API_URL}/auth/login`, { data: { email: users.root, password: 'e2e-senha-123' } });
  const rootHeaders = { Authorization: `Bearer ${(await rootLogin.json()).access_token}` };
  const institutions: { id: string; slug: string }[] = await (await request.get(`${API_URL}/platform/institutions`, { headers: rootHeaders })).json();
  const alfa = institutions.find((item) => item.slug === 'escola-alfa');
  await request.put(`${API_URL}/platform/institutions/${alfa?.id}/domain`, { headers: rootHeaders, data: { custom_domain: domain } });
  try {
    await page.setExtraHTTPHeaders({ 'X-Forwarded-Host': domain });
    await page.goto('/');
    await expect(page.getByText(tagline)).toBeVisible();
    await expect(page.getByRole('heading', { level: 1 })).not.toContainText('Da matrícula ao certificado');
  } finally {
    await request.put(`${API_URL}/platform/institutions/${alfa?.id}/domain`, { headers: rootHeaders, data: { custom_domain: '' } });
  }
});
