import type { APIRequestContext } from '@playwright/test';
import { API_URL, adminHeaders } from './api';

/** Programa com 10h de atividades, 4h de estagio obrigatorio e TCC (matriz so com optativa); o aluno fica matriculado nele. */
export async function createCompletionScenario(request: APIRequestContext, suffix: string, studentId: number, institution = 'escola-alfa') {
  const admin = await adminHeaders(request, institution);
  const post = async <T>(path: string, data: unknown): Promise<T> => {
    const response = await request.post(`${API_URL}${path}`, { headers: admin, data });
    if (!response.ok()) throw new Error(`${path}: ${response.status()} ${await response.text()}`);
    return response.json();
  };
  const program = await post<{ id: number }>('/academic/programs', {
    code: `TC${suffix}`.slice(0, 20).toUpperCase(), name: `Bacharelado ${suffix}`, level: 'undergraduate',
    complementary_hours: 10, internship_hours: 4, requires_final_project: true,
  });
  const curriculum = await post<{ id: number }>(`/academic/programs/${program.id}/curricula`, { version: '1' });
  // Matriz so com optativa: a carga obrigatoria nao entra no caminho do teste.
  const subject = await post<{ id: number }>('/academic/subjects', { code: `OPT${suffix}`.toUpperCase(), name: `Optativa ${suffix}`, hours: 30 });
  await post(`/academic/curricula/${curriculum.id}/components`, { subject_id: subject.id, term_number: 1, kind: 'optional' });
  await post(`/academic/curricula/${curriculum.id}/activate`, {});
  const enrollment = await post<{ id: number }>('/academic/program-enrollments', { student_id: studentId, program_id: program.id });
  return { enrollmentId: enrollment.id };
}
