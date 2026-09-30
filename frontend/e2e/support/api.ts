import type { APIRequestContext } from '@playwright/test';
import { E2E_PASSWORD, users } from './users';

/** API usada pelo frontend nos testes (mesma de NEXT_PUBLIC_API_URL). */
export const API_URL = process.env.E2E_API_URL ?? 'http://localhost:8000';

async function adminHeaders(request: APIRequestContext, institution: string) {
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
  return { name, email };
}
