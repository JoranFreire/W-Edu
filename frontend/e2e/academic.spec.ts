import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

// Escola Alfa e do tipo "school": telas usam a nomenclatura escolar (etapa, componente, serie).
test('estrutura academica: etapa, componentes, pre-requisito e matriz vigente', async ({ page }) => {
  const suffix = uniqueSuffix().toUpperCase();
  const programCode = `EF${suffix}`;
  const [mat6, mat7] = [`M6${suffix}`, `M7${suffix}`];

  await login(page, users.admin);
  await page.goto('/admin/academic');

  await page.getByRole('button', { name: 'Nova etapa de ensino' }).click();
  const programDialog = page.getByRole('dialog', { name: 'Nova etapa de ensino' });
  await programDialog.getByLabel('Código').fill(programCode);
  await programDialog.getByLabel('Nome').fill(`Fundamental II ${suffix}`);
  await programDialog.getByLabel('Nível').selectOption('basic');
  await programDialog.getByLabel(/Duração/).fill('4');
  await programDialog.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Programa salvo.');

  await page.getByRole('tab', { name: /Componentes curriculares/ }).click();
  for (const [code, name] of [[mat6, 'Matemática 6'], [mat7, 'Matemática 7']]) {
    await page.getByRole('button', { name: 'Novo componente curricular' }).click();
    const dialog = page.getByRole('dialog', { name: 'Novo componente curricular' });
    await dialog.getByLabel('Código').fill(code);
    await dialog.getByLabel('Nome').fill(`${name} ${suffix}`);
    await dialog.getByLabel('Carga horária').fill('160');
    await dialog.getByRole('button', { name: 'Salvar' }).click();
    await expectToast(page, 'Disciplina salva.');
  }

  await page.getByRole('button', { name: `Vínculos de ${mat7}` }).click();
  const links = page.getByRole('dialog', { name: new RegExp(mat7) });
  await links.getByLabel('Adicionar pré-requisito').selectOption({ label: `${mat6} · Matemática 6 ${suffix}` });
  await links.getByRole('button', { name: 'Adicionar' }).first().click();
  await expect(links.getByText(`${mat6} · Matemática 6 ${suffix}`).first()).toBeVisible();
  await links.getByRole('button', { name: 'Fechar modal' }).click();

  await page.getByRole('tab', { name: /Etapas de ensino/ }).click();
  await page.getByRole('link', { name: new RegExp(programCode) }).click();
  await page.getByRole('button', { name: 'Criar matriz' }).click();
  await page.getByLabel('Versão').fill('2027');
  await page.getByRole('button', { name: 'Criar', exact: true }).click();
  await expectToast(page, 'Matriz criada em rascunho.');

  // Mesma serie para os dois: a pendencia de pre-requisito aparece.
  for (const label of [`${mat6} · Matemática 6 ${suffix}`, `${mat7} · Matemática 7 ${suffix}`]) {
    await page.getByRole('button', { name: 'Incluir componente curricular' }).click();
    const dialog = page.getByRole('dialog', { name: 'Incluir na matriz' });
    await dialog.getByLabel('Disciplina').selectOption({ label });
    await dialog.getByLabel('Série').fill('1');
    await dialog.getByRole('button', { name: 'Salvar' }).click();
    await expectToast(page, 'Matriz atualizada.');
  }
  await expect(page.getByText(new RegExp(`${mat7} \\(período 1\\) exige ${mat6}`))).toBeVisible();

  await page.getByRole('button', { name: `Editar componente ${mat7}` }).click();
  await page.getByRole('dialog').getByLabel('Série').fill('2');
  await page.getByRole('dialog').getByRole('button', { name: 'Salvar' }).click();
  await expect(page.getByText('Pendências')).toHaveCount(0);
  await expect(page.getByRole('region', { name: 'Série 2' })).toContainText(mat7);
  await expect(page.getByText('320h').first()).toBeVisible();

  await page.getByRole('button', { name: 'Tornar vigente' }).click();
  await expectToast(page, 'Matriz vigente atualizada.');
  await expect(page.getByText('somente leitura', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Incluir componente curricular' })).toHaveCount(0);
});

test('aluno nao acessa a estrutura academica', async ({ page }) => {
  await login(page, users.aluno);
  await page.goto('/admin/academic');
  await expect(page.getByRole('heading', { name: 'Acesso restrito' })).toBeVisible();
});
