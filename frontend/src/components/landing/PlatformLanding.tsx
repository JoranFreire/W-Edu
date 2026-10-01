import LandingAudiences from '@/components/landing/LandingAudiences';
import LandingContact from '@/components/landing/LandingContact';
import LandingFaq from '@/components/landing/LandingFaq';
import LandingFeatures from '@/components/landing/LandingFeatures';
import LandingFooter from '@/components/landing/LandingFooter';
import LandingHeader from '@/components/landing/LandingHeader';
import LandingHero from '@/components/landing/LandingHero';
import LandingHighlights from '@/components/landing/LandingHighlights';
import LandingPlans from '@/components/landing/LandingPlans';
import type { PublicPlan } from '@/types/publicSite';

/** Pagina de contratacao da plataforma (dominio da plataforma). */
export default function PlatformLanding({ plans }: { plans: PublicPlan[] }) {
  return (
    <div className="min-h-screen bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      <LandingHeader />
      <main>
        <LandingHero />
        <LandingFeatures />
        <LandingAudiences />
        <LandingHighlights />
        <LandingPlans plans={plans} />
        <LandingContact plans={plans} />
        <LandingFaq />
      </main>
      <LandingFooter />
    </div>
  );
}
