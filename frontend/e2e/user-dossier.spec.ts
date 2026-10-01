import { createStudent, enrollInSeedProgram, linkGuardian, registerOccurrence } from './support/api';
import { expect, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

test('usuarios: filtro por perfil e dossie do aluno com o responsavel', async ({ page, request }) => {
  const suffix = uniqueSuffix();
  const aluno = await createStudent(request, `Dossie ${suffix}`);
  const guardianName = `Mae Dossie ${suffix}`;
  await linkGuardian(request, aluno.id, guardianName, `mae.dossie.${suffix}@alfa.example.com`, 'escola-alfa', true);
  await enrollInSeedProgram(request, aluno.id);
  await registerOccurrence(request, aluno.id, `Febre ${suffix}`);

  await login(page, users.admin);
  await page.goto('/admin/users');
  const role = page.getByLabel('Perfil', { exact: true });
  await role.selectOption('guardians');
  await expect(page.getByRole('link', { name: `Dossiê de ${guardianName}`, exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: `Dossiê de ${aluno.name}`, exact: true })).toHaveCount(0);

  await role.selectOption('students');
  await page.getByLabel('Buscar usuário').fill(`dossie ${suffix}`);
  await expect(page.getByRole('status').filter({ hasText: /^1 de \d+$/ })).toBeVisible();
  await page.getByLabel('Situação').selectOption('inactive');
  await expect(page.getByText('Nenhum usuário encontrado com esse filtro.')).toBeVisible();
  await page.getByLabel('Situação').selectOption('active');
  await page.getByRole('link', { name: `Dossiê de ${aluno.name}`, exact: true }).click();

  await expect(page.getByRole('heading', { name: aluno.name, level: 1 })).toBeVisible();
  const tabs = page.getByRole('tablist', { name: 'Dossiê' });
  const panel = page.getByRole('tabpanel');
  await expect(page.getByRole('complementary', { name: 'Ficha' })).toBeVisible();

  await tabs.getByRole('tab', { name: /Responsáveis/ }).click();
  await expect(panel.getByRole('link', { name: guardianName })).toBeVisible();
  await expect(panel.getByText('Financeiro')).toBeVisible();

  await tabs.getByRole('tab', { name: /Acadêmico/ }).click();
  await expect(panel.getByRole('link', { name: /Abrir ficha/ })).toBeVisible();

  await tabs.getByRole('tab', { name: /Ocorrências/ }).click();
  await expect(panel.getByText(`Febre ${suffix}`)).toBeVisible();

  await tabs.getByRole('tab', { name: /Cursos/ }).click();
  await expect(panel.getByText('Nenhum curso.')).toBeVisible();

  // O responsavel abre o proprio dossie, com o aluno como dependente.
  await tabs.getByRole('tab', { name: /Responsáveis/ }).click();
  await panel.getByRole('link', { name: guardianName }).click();
  await expect(page.getByRole('heading', { name: guardianName, level: 1 })).toBeVisible();
  await page.getByRole('tablist', { name: 'Dossiê' }).getByRole('tab', { name: /Dependentes/ }).click();
  await expect(page.getByRole('tabpanel').getByRole('link', { name: aluno.name, exact: true })).toBeVisible();

  // Volta para a lista no ultimo filtro escolhido.
  await page.getByRole('button', { name: 'Voltar para usuários' }).click();
  await expect(role).toHaveValue('students');
  await page.getByRole('button', { name: /Limpar filtros/ }).click();
  await expect(role).toHaveValue('all');
});
