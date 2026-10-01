import { headers } from 'next/headers';
import { cache } from 'react';
import type { InstitutionPage, PublicPlan } from '@/types/publicSite';

// Chamadas feitas no servidor do Next (renderizacao das paginas publicas), direto para a API.
const API_URL = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';

async function getJson<T>(path: string, init?: RequestInit): Promise<T | null> {
  const response = await fetch(`${API_URL}${path}`, { cache: 'no-store', ...init });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`API ${path}: ${response.status}`);
  return (await response.json()) as T | null;
}

/** Pagina da instituicao do endereco acessado (subdominio ou dominio proprio); null no dominio da plataforma. */
export const institutionPageForHost = cache(async (): Promise<InstitutionPage | null> => {
  const requestHeaders = await headers();
  const host = requestHeaders.get('x-forwarded-host') ?? requestHeaders.get('host') ?? '';
  return getJson<InstitutionPage>('/public/institution-page', { headers: { 'X-Forwarded-Host': host } });
});

/** Pagina da instituicao pelo slug (endereco /instituicao/<slug>, util sem dominio proprio). */
export const institutionPageBySlug = cache(async (slug: string): Promise<InstitutionPage | null> =>
  getJson<InstitutionPage>(`/public/institution-page?institution=${encodeURIComponent(slug)}`));

export const publicPlans = cache(async (): Promise<PublicPlan[]> => (await getJson<PublicPlan[]>('/public/plans')) ?? []);
