import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import InstitutionHome from '@/components/institutionHome/InstitutionHome';
import { institutionDisplayName } from '@/lib/institution/branding';
import { institutionPageBySlug } from '@/lib/publicSite/server';

export const dynamic = 'force-dynamic';

type Params = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const page = await institutionPageBySlug((await params).slug);
  if (!page) return { title: 'Instituição não encontrada' };
  const name = institutionDisplayName(page.institution);
  return { title: name, description: page.profile.tagline || `Cursos e matrículas da ${name}.` };
}

/** Pagina da instituicao pelo endereco da plataforma (antes de configurar subdominio ou dominio proprio). */
export default async function InstitutionBySlugPage({ params }: Params) {
  const { slug } = await params;
  const page = await institutionPageBySlug(slug);
  if (!page) notFound();
  return <InstitutionHome page={page} slug={slug} />;
}
