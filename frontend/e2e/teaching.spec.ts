import { expect, expectToast, login, test, uniqueSuffix } from './support/fixtures';
import { users } from './support/users';

/** Data unica por execucao (o diario aceita um registro por dia na turma). */
function uniqueLessonDate() {
  const day = new Date(Date.UTC(2030, 0, 1) + (Math.floor(Date.now() / 1000) % 3000) * 86_400_000);
  return day.toISOString().slice(0, 10);
}

// "Turma Matemática" do seed: ministrada pelo Instrutor Alfa, com o Aluno Alfa inscrito.
test('professor lanca avaliacao, nota e chamada da turma', async ({ page }) => {
  const itemName = `Prova ${uniqueSuffix()}`;
  await login(page, users.instrutor);
  await page.getByRole('link', { name: 'Diário de classe' }).first().click();
  await page.getByRole('link', { name: /Turma Matemática/ }).click();

  await page.getByRole('tab', { name: /Avaliações e notas/ }).click();
  await page.getByLabel('Nome da avaliação').fill(itemName);
  await page.getByLabel('Nota máxima').fill('10');
  await page.getByRole('button', { name: 'Incluir', exact: true }).click();
  await expectToast(page, 'Avaliação incluída.');

  await page.getByRole('button', { name: `Lançar notas de ${itemName}` }).click();
  await page.getByLabel('Nota de Aluno Alfa').fill('8');
  await page.getByRole('button', { name: 'Salvar notas' }).click();
  await expectToast(page, 'Notas salvas.');

  await page.getByRole('tab', { name: /Aulas e chamada/ }).click();
  const lessonDate = uniqueLessonDate();
  await page.getByLabel('Data da aula').fill(lessonDate);
  await page.getByLabel('Aulas no dia').selectOption('2');
  await page.getByLabel('Conteúdo ministrado').fill('Equações do 1º grau');
  await page.getByRole('button', { name: 'Registrar' }).click();
  await expectToast(page, 'Aula registrada.');

  const label = lessonDate.split('-').reverse().join('/');
  await page.getByRole('button', { name: `Chamada de ${label}` }).click();
  await page.getByLabel('Faltas de Aluno Alfa').selectOption('1');
  await page.getByRole('button', { name: 'Salvar chamada' }).click();
  await expectToast(page, 'Chamada salva.');

  await page.getByRole('tab', { name: /Boletim/ }).click();
  const row = page.getByRole('row', { name: /Aluno Alfa/ });
  await expect(row).toBeVisible();
  await expect(row).toContainText('%');
});

test('aluno nao acessa o diario de classe', async ({ page }) => {
  await login(page, users.aluno);
  await page.goto('/teaching');
  await expect(page.getByRole('heading', { name: 'Acesso restrito' })).toBeVisible();
});

test('coordenacao cadastra esquema de avaliacao por conceito', async ({ page }) => {
  const name = `Conceitos ${uniqueSuffix()}`;
  await login(page, users.admin);
  await page.goto('/admin/academic');
  await page.getByRole('tab', { name: /Avaliação/ }).click();
  await page.getByRole('button', { name: 'Novo esquema' }).click();
  const dialog = page.getByRole('dialog', { name: 'Novo esquema de avaliação' });
  await dialog.getByLabel('Nome').fill(name);
  await dialog.getByLabel('Escala').selectOption('concept');
  await dialog.getByLabel(/Faixas de conceito/).fill('A:9, B:7, C:5, D:0');
  await dialog.getByRole('button', { name: 'Salvar' }).click();
  await expectToast(page, 'Esquema salvo.');
  await expect(page.getByText(name)).toBeVisible();
});
