import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test.beforeEach(async ({ page }) => {
  await login(page, users.admin);
});

test('financeiro: abas e modal de plano', async ({ page }) => {
  await page.goto('/admin/finance');
  await page.getByRole('tab', { name: /Assinaturas/ }).click();
  await expect(page.getByText('Assinaturas cadastradas')).toBeVisible();
  await page.getByRole('tab', { name: /Cobranças/ }).click();
  await expect(page.getByText('Cobranças cadastradas')).toBeVisible();
  await page.getByRole('tab', { name: /Planos/ }).click();
  await page.getByRole('button', { name: 'Adicionar plano' }).click();
  await expect(page.getByRole('dialog', { name: 'Adicionar plano' })).toBeVisible();
  await page.getByRole('button', { name: 'Fechar modal' }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('trilhas: cria trilha', async ({ page }) => {
  const name = `Trilha ${uniqueSuffix()}`;
  await page.goto('/admin/learning-paths');
  await page.getByRole('button', { name: 'Nova trilha' }).click();
  await page.getByPlaceholder('Nome').fill(name);
  await page.getByRole('button', { name: /Salvar|Criar/ }).last().click();
  await expectToast(page, 'Trilha criada.');
  await expect(page.getByText(name)).toBeVisible();
});

test('comunicacao: eventos e templates', async ({ page }) => {
  await page.goto('/admin/notifications');
  await expect(page.getByText('Eventos recentes')).toBeVisible();
  // A entrega e automatica: sem marcacao manual de enviado/falhou.
  const events = page.getByRole('list', { name: 'Eventos' });
  await expect(events.getByRole('button', { name: 'Enviado' })).toHaveCount(0);
  await expect(events.getByRole('button', { name: 'Falhou' })).toHaveCount(0);

  await page.getByRole('tab', { name: /Templates/ }).click();
  await expect(page.getByText('Modelos disponíveis por canal.')).toBeVisible();
  // Destaque no nome de negocio; o codigo interno aparece so como detalhe.
  await expect(page.getByRole('heading', { name: 'Desligamento por faltas' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'absence_dismissal' })).toHaveCount(0);

  // Novo template: evento + canal ja existentes sao barrados.
  await page.getByRole('button', { name: 'Novo template' }).click();
  const create = page.getByRole('dialog', { name: 'Novo template' });
  await create.getByLabel('Evento').selectOption({ label: 'Desligamento por faltas' });
  await create.getByLabel('Canal').selectOption({ label: 'Interno' });
  await expect(create.getByRole('alert')).toContainText('Já existe um template');
  await expect(create.getByRole('button', { name: 'Criar template' })).toBeDisabled();
  await expect(create.getByText('{absence_percent}')).toBeVisible();
  await create.getByRole('button', { name: 'Cancelar' }).click();

  // Edicao do texto de um template existente.
  const body = `A turma {class_name} foi criada (${uniqueSuffix()}).`;
  await page.getByRole('button', { name: 'Editar template Nova turma criada (Interno)' }).click();
  const edit = page.getByRole('dialog', { name: /Editar: Nova turma criada/ });
  await edit.getByLabel('Mensagem').fill(body);
  await edit.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Template atualizado.');
  await page.getByRole('button', { name: 'Editar template Nova turma criada (Interno)' }).click();
  await expect(page.getByRole('dialog').getByLabel('Mensagem')).toHaveValue(body);
});

test('relatorios carregam', async ({ page }) => {
  await page.goto('/admin/analytics');
  await expect(page.getByText('Relatórios detalhados')).toBeVisible({ timeout: 20_000 });
});
