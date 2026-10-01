/** Instituicao das paginas publicas: `?institution=` (links compartilhados) ou subdominio (sem header). */
export function institutionHeaders(slug: string | null): Record<string, string> {
  return slug ? { 'X-Institution': slug } : {};
}

/** Mantem `?institution=` nos links entre paginas publicas. */
export function withInstitution(path: string, slug: string | null): string {
  return slug ? `${path}?institution=${encodeURIComponent(slug)}` : path;
}
