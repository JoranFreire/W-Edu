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
  const filters = page.getByRole('group', { name: 'Filtrar por perfil' });
  await filters.getByRole('button', { name: /^Responsáveis/ }).click();
  await expect(page.getByRole('link', { name: `Dossiê de ${guardianName}`, exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: `Dossiê de ${aluno.name}`, exact: true })).toHaveCount(0);

  await filters.getByRole('button', { name: /^Alunos/ }).click();
  await page.getByLabel('Buscar usuário').fill(`dossie ${suffix}`);
  await page.getByRole('link', { name: `Dossiê de ${aluno.name}`, exact: true }).click();

  await expect(page.getByRole('heading', { name: aluno.name, level: 1 })).toBeVisible();
  const family = page.getByRole('region', { name: 'Responsáveis' });
  await expect(family.getByRole('link', { name: guardianName })).toBeVisible();
  await expect(family.getByText('Financeiro')).toBeVisible();
  await expect(page.getByRole('region', { name: 'Matrículas' }).getByRole('link', { name: /Abrir ficha/ })).toBeVisible();
  await expect(page.getByRole('region', { name: /Ocorrências/ }).getByText(`Febre ${suffix}`)).toBeVisible();

  // O responsavel abre o proprio dossie, com o aluno como dependente.
  await family.getByRole('link', { name: guardianName }).click();
  await expect(page.getByRole('heading', { name: guardianName, level: 1 })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Dependentes' }).getByRole('link', { name: aluno.name, exact: true })).toBeVisible();

  // Volta para a lista no ultimo filtro escolhido.
  await page.getByRole('button', { name: 'Voltar para usuários' }).click();
  await expect(filters.getByRole('button', { name: /^Alunos/ })).toHaveAttribute('aria-pressed', 'true');
});
