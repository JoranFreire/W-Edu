import type { APIRequestContext } from '@playwright/test';
import { API_URL, adminHeaders, createOpenTerm } from './api';
import { users } from './users';

async function post<T>(request: APIRequestContext, path: string, headers: Record<string, string>, data: unknown): Promise<T> {
  const response = await request.post(`${API_URL}${path}`, { headers, data });
  if (!response.ok()) throw new Error(`${path}: ${response.status()} ${await response.text()}`);
  return response.json();
}

/**
 * Curso de graduacao novo: INTRO (seg 08-10), ETICA (seg 09-11, choca com INTRO) e AVANC (exige INTRO), ofertas
 * abertas num periodo novo e janela de matricula aberta; o aluno informado fica matriculado no programa.
 */
export async function createRegistrationScenario(request: APIRequestContext, suffix: string, studentId: number, institution = 'escola-alfa') {
  const admin = await adminHeaders(request, institution);
  const term = await createOpenTerm(request, `Semestre ${suffix}`, institution);
  const program = await post<{ id: number }>(request, '/academic/programs', admin, { code: `GR${suffix}`.slice(0, 20).toUpperCase(), name: `Graduação ${suffix}`, level: 'undergraduate' });
  const subjects: Record<string, number> = {};
  for (const code of ['INTRO', 'ETICA', 'AVANC']) {
    const subject = await post<{ id: number }>(request, '/academic/subjects', admin, { code: `${code}${suffix}`.toUpperCase(), name: `${code} ${suffix}`, hours: 60, credits: 4 });
    subjects[code] = subject.id;
  }
  await post(request, `/academic/subjects/${subjects.AVANC}/prerequisites`, admin, { subject_id: subjects.INTRO });
  const curriculum = await post<{ id: number }>(request, `/academic/programs/${program.id}/curricula`, admin, { version: '1' });
  for (const [code, termNumber] of [['INTRO', 1], ['ETICA', 1], ['AVANC', 2]] as const) {
    await post(request, `/academic/curricula/${curriculum.id}/components`, admin, { subject_id: subjects[code], term_number: termNumber });
  }
  await post(request, `/academic/curricula/${curriculum.id}/activate`, admin, {});
  await post(request, '/academic/program-enrollments', admin, { student_id: studentId, program_id: program.id });

  const courses: { id: number; name: string }[] = await (await request.get(`${API_URL}/courses`, { headers: admin })).json();
  const people: { id: number; email: string }[] = await (await request.get(`${API_URL}/admin/users`, { headers: admin })).json();
  const offerings: Record<string, number> = {};
  for (const [code, weekday, start, end] of [['INTRO', 0, '08:00', '10:00'], ['ETICA', 0, '09:00', '11:00'], ['AVANC', 1, '08:00', '10:00']] as const) {
    const offering = await post<{ id: number }>(request, '/schedule/classes', admin, {
      course_id: courses.find((item) => item.name === 'Matemática')?.id, name: `${code} T1 ${suffix}`, capacity: 20, status: 'open',
      instructor_id: people.find((person) => person.email === users.instrutor)?.id, term_id: term.id, subject_id: subjects[code],
      starts_at: '2032-02-01T08:00:00Z', ends_at: '2032-06-30T12:00:00Z',
    });
    await post(request, `/registration/offerings/${offering.id}/time-slots`, admin, { weekday, starts_at: start, ends_at: end });
    offerings[code] = offering.id;
  }
  const now = Date.now();
  await post(request, '/registration/windows', admin, {
    term_id: term.id, program_id: program.id, name: `Matrícula ${suffix}`,
    opens_at: new Date(now - 3_600_000).toISOString(), closes_at: new Date(now + 86_400_000).toISOString(), max_credits: 12,
  });
  return { termName: `Semestre ${suffix}`, programId: program.id, offerings };
}
