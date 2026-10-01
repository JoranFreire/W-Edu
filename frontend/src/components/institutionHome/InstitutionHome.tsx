import Link from 'next/link';
import AboutSection from '@/components/institutionHome/AboutSection';
import ContactSection from '@/components/institutionHome/ContactSection';
import InstitutionHeader from '@/components/institutionHome/InstitutionHeader';
import InstitutionHero from '@/components/institutionHome/InstitutionHero';
import OfferingsSection from '@/components/institutionHome/OfferingsSection';
import OpenCallsSection from '@/components/institutionHome/OpenCallsSection';
import { brandingStyle, institutionDisplayName } from '@/lib/institution/branding';
import type { InstitutionPage } from '@/types/publicSite';

/**
 * Pagina publica da instituicao, com as cores dela. `slug` vem preenchido quando a pagina e aberta pelo
 * endereco da plataforma (/instituicao/<slug>): os links levam a instituicao junto; no dominio dela, nao precisa.
 */
export default function InstitutionHome({ page, slug = null }: { page: InstitutionPage; slug?: string | null }) {
  return (
    <div style={brandingStyle(page.institution.branding)} className="min-h-screen bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      <InstitutionHeader institution={page.institution} homeHref={slug ? `/instituicao/${slug}` : '/'} />
      <main>
        <InstitutionHero page={page} />
        <OpenCallsSection calls={page.open_calls} slug={slug} />
        <OfferingsSection programs={page.programs} courses={page.courses} />
        <AboutSection profile={page.profile} hasOpenCalls={page.open_calls.length > 0} />
        <ContactSection profile={page.profile} campuses={page.campuses} />
      </main>
      <footer className="border-t border-gray-200 py-8 text-center text-sm text-gray-500 dark:border-gray-800 dark:text-gray-400">
        © {new Date().getFullYear()} {institutionDisplayName(page.institution)} · <Link href="/validate-certificate" className="hover:text-indigo-600">Validar certificado</Link>
      </footer>
    </div>
  );
}
