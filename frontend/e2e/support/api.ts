import type { APIRequestContext } from '@playwright/test';
import { E2E_PASSWORD, users } from './users';

/** API usada pelo frontend nos testes (mesma de NEXT_PUBLIC_API_URL). */
export const API_URL = process.env.E2E_API_URL ?? 'http://localhost:8000';

export async function adminHeaders(request: APIRequestContext, institution: string) {
  const response = await request.post(`${API_URL}/auth/login`, {
    data: { email: users.admin, password: E2E_PASSWORD, institution },
  });
  const { access_token: token } = await response.json();
  return { Authorization: `Bearer ${token}`, 'X-Institution': institution };
}

/** Cria um aluno novo na instituicao (preparo de dados quando a tela nao e o foco do teste). */
export async function createStudent(request: APIRequestContext, name: string, institution = 'escola-alfa') {
  const email = `${name.toLowerCase().replace(/[^a-z0-9]+/g, '.')}@alfa.example.com`;
  const response = await request.post(`${API_URL}/admin/users`, {
    headers: await adminHeaders(request, institution),
    data: { name, email, password: E2E_PASSWORD, role: 'student' },
  });
  if (!response.ok()) throw new Error(`createStudent: ${response.status()} ${await response.text()}`);
  const { id }: { id: number } = await response.json();
  return { id, name, email };
}

async function tokenHeaders(request: APIRequestContext, email: string, institution: string) {
  const response = await request.post(`${API_URL}/auth/login`, { data: { email, password: E2E_PASSWORD, institution } });
  const { access_token: token } = await response.json();
  return { Authorization: `Bearer ${token}`, 'X-Institution': institution };
}

/** Turma nova do curso Matemática, ministrada pelo Instrutor Alfa, com o aluno informado inscrito. */
export async function createOfferingWithStudent(request: APIRequestContext, name: string, studentEmail: string, institution = 'escola-alfa') {
  const admin = await adminHeaders(request, institution);
  const courses: { id: number; name: string }[] = await (await request.get(`${API_URL}/courses`, { headers: admin })).json();
  const people: { id: number; email: string }[] = await (await request.get(`${API_URL}/admin/users`, { headers: admin })).json();
  const course = courses.find((item) => item.name === 'Matemática');
  const instructor = people.find((person) => person.email === users.instrutor);
  const now = Date.now();
  const response = await request.post(`${API_URL}/schedule/classes`, {
    headers: admin,
    data: {
      course_id: course?.id, name, capacity: 10, status: 'open', instructor_id: instructor?.id,
      starts_at: new Date(now).toISOString(), ends_at: new Date(now + 30 * 86_400_000).toISOString(),
    },
  });
  if (!response.ok()) throw new Error(`createOffering: ${response.status()} ${await response.text()}`);
  const offering: { id: number } = await response.json();
  const join = await request.post(`${API_URL}/schedule/classes/${offering.id}/join`, { headers: await tokenHeaders(request, studentEmail, institution) });
  if (!join.ok()) throw new Error(`join: ${join.status()} ${await join.text()}`);
  return offering;
}

/** Periodo letivo aberto (rematricula exige periodo nao encerrado). */
export async function createOpenTerm(request: APIRequestContext, name: string, institution = 'escola-alfa') {
  const admin = await adminHeaders(request, institution);
  const response = await request.post(`${API_URL}/academic/terms`, {
    headers: admin, data: { name, kind: 'year', starts_on: '2032-02-01', ends_on: '2032-12-15' },
  });
  if (!response.ok()) throw new Error(`createTerm: ${response.status()} ${await response.text()}`);
  const term: { id: number } = await response.json();
  await request.post(`${API_URL}/academic/terms/${term.id}/status`, { headers: admin, data: { status: 'open' } });
  return term;
}

/** Matricula do aluno no programa EF-E2E do seed (matriz vigente). */
export async function enrollInSeedProgram(request: APIRequestContext, studentId: number, institution = 'escola-alfa') {
  const admin = await adminHeaders(request, institution);
  const programs: { id: number; code: string }[] = await (await request.get(`${API_URL}/academic/programs`, { headers: admin })).json();
  const program = programs.find((item) => item.code === 'EF-E2E');
  const response = await request.post(`${API_URL}/academic/program-enrollments`, { headers: admin, data: { student_id: studentId, program_id: program?.id } });
  if (!response.ok()) throw new Error(`enroll: ${response.status()} ${await response.text()}`);
  const enrollment: { id: number } = await response.json();
  return enrollment;
}

/** Responsavel novo (conta criada pela secretaria) vinculado ao aluno; `isFinancial` o torna o pagador. */
export async function linkGuardian(request: APIRequestContext, studentId: number, name: string, email: string, institution = 'escola-alfa', isFinancial = false) {
  const response = await request.post(`${API_URL}/guardians/students/${studentId}/links`, {
    headers: await adminHeaders(request, institution),
    data: { name, email, password: E2E_PASSWORD, relationship_kind: 'mother', is_financial: isFinancial },
  });
  if (!response.ok()) throw new Error(`linkGuardian: ${response.status()} ${await response.text()}`);
}

/** Turma-grupo do programa EF-E2E com a matricula alocada e uma oferta ministrada pelo Instrutor Alfa. */
export async function createClassGroupOffering(request: APIRequestContext, name: string, enrollmentId: number, institution = 'escola-alfa') {
  const admin = await adminHeaders(request, institution);
  const term = await createOpenTerm(request, `Período ${name}`, institution);
  const programs: { id: number; code: string }[] = await (await request.get(`${API_URL}/academic/programs`, { headers: admin })).json();
  const program = programs.find((item) => item.code === 'EF-E2E');
  const group = await request.post(`${API_URL}/academic/class-groups`, { headers: admin, data: { program_id: program?.id, term_id: term.id, name } });
  if (!group.ok()) throw new Error(`classGroup: ${group.status()} ${await group.text()}`);
  const { id: groupId }: { id: number } = await group.json();
  const member = await request.post(`${API_URL}/academic/class-groups/${groupId}/members`, { headers: admin, data: { program_enrollment_id: enrollmentId } });
  if (!member.ok()) throw new Error(`member: ${member.status()} ${await member.text()}`);
  const courses: { id: number; name: string }[] = await (await request.get(`${API_URL}/courses`, { headers: admin })).json();
  const people: { id: number; email: string }[] = await (await request.get(`${API_URL}/admin/users`, { headers: admin })).json();
  const now = Date.now();
  const offering = await request.post(`${API_URL}/schedule/classes`, {
    headers: admin,
    data: {
      course_id: courses.find((item) => item.name === 'Matemática')?.id, name: `Matemática ${name}`, capacity: 10, status: 'open',
      instructor_id: people.find((person) => person.email === users.instrutor)?.id, class_group_id: groupId,
      starts_at: new Date(now).toISOString(), ends_at: new Date(now + 30 * 86_400_000).toISOString(),
    },
  });
  if (!offering.ok()) throw new Error(`offering: ${offering.status()} ${await offering.text()}`);
  const { id: offeringId }: { id: number } = await offering.json();
  return { groupId, offeringId };
}

/** Inscreve na oferta os alunos da turma-grupo (o diario lista os inscritos). */
export async function syncGroupEnrollments(request: APIRequestContext, offeringId: number, institution = 'escola-alfa') {
  const response = await request.post(`${API_URL}/assessment/offerings/${offeringId}/sync-group-enrollments`, {
    headers: await adminHeaders(request, institution),
  });
  if (!response.ok()) throw new Error(`syncGroup: ${response.status()} ${await response.text()}`);
}

/** Ocorrencia registrada pela secretaria (admin), fora da tela em teste. */
export async function registerOccurrence(request: APIRequestContext, studentId: number, description: string, institution = 'escola-alfa') {
  const response = await request.post(`${API_URL}/school/occurrences`, {
    headers: await adminHeaders(request, institution),
    data: { student_id: studentId, kind: 'health', description },
  });
  if (!response.ok()) throw new Error(`registerOccurrence: ${response.status()} ${await response.text()}`);
}
