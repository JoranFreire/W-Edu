import type { Metadata } from 'next';
import InstitutionHome from '@/components/institutionHome/InstitutionHome';
import PlatformLanding from '@/components/landing/PlatformLanding';
import { institutionDisplayName } from '@/lib/institution/branding';
import { institutionPageForHost, publicPlans } from '@/lib/publicSite/server';

// Depende do endereco acessado: no dominio da plataforma, a pagina de contratacao; no do cliente, a da instituicao.
export const dynamic = 'force-dynamic';

export async function generateMetadata(): Promise<Metadata> {
  const page = await institutionPageForHost();
  if (!page) {
    return {
      title: 'W-Edu · Gestão educacional para escolas, faculdades e cursos profissionalizantes',
      description: 'Secretaria, diário de classe, financeiro, editais, programas sociais e comunicação com as famílias em uma só plataforma.',
    };
  }
  const name = institutionDisplayName(page.institution);
  return { title: name, description: page.profile.tagline || `Cursos e matrículas da ${name}.` };
}

export default async function Home() {
  const page = await institutionPageForHost();
  if (page) return <InstitutionHome page={page} />;
  return <PlatformLanding plans={await publicPlans()} />;
}
