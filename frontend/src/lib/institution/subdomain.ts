/**
 * Instituicao por subdominio: com NEXT_PUBLIC_TENANT_BASE_DOMAIN (ex.: "wedu.com.br"),
 * cada instituicao vive em https://<slug>.<dominio>. Sem a variavel, tudo roda em um so dominio.
 */
const baseDomain = process.env.NEXT_PUBLIC_TENANT_BASE_DOMAIN?.replace(/^\.+|\.+$/g, '').toLowerCase() || null;

/** Endereco de login da instituicao, ou null quando subdominios nao estao configurados. */
export function institutionLoginUrl(slug: string): string | null {
  if (!baseDomain || typeof window === 'undefined') return null;
  const { protocol, port } = window.location;
  return `${protocol}//${slug}.${baseDomain}${port ? `:${port}` : ''}/login`;
}
