import type { InstitutionPage } from '@/types/publicSite';

function whatsappLink(number: string) {
  return `https://wa.me/${number.replace(/\D/g, '')}`;
}

function siteLink(value: string) {
  return /^https?:\/\//i.test(value) ? value : `https://${value}`;
}

/** Contatos e unidades da instituicao. */
export default function ContactSection({ profile, campuses }: Pick<InstitutionPage, 'profile' | 'campuses'>) {
  const items = [
    profile.phone && { label: 'Telefone', value: profile.phone, href: `tel:${profile.phone.replace(/\s/g, '')}` },
    profile.whatsapp && { label: 'WhatsApp', value: profile.whatsapp, href: whatsappLink(profile.whatsapp) },
    profile.email && { label: 'E-mail', value: profile.email, href: `mailto:${profile.email}` },
    profile.website && { label: 'Site', value: profile.website, href: siteLink(profile.website) },
    profile.instagram && { label: 'Instagram', value: profile.instagram, href: `https://instagram.com/${profile.instagram.replace(/^@/, '')}` },
    profile.address && { label: 'Endereço', value: profile.address, href: null },
  ].filter(Boolean) as { label: string; value: string; href: string | null }[];
  if (items.length === 0 && campuses.length === 0) return null;
  return (
    <section aria-label="Contato" className="bg-gray-50 py-14 dark:bg-gray-900/60">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 md:grid-cols-2">
        {items.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Fale com a gente</h2>
            <dl className="mt-5 space-y-3">
              {items.map((item) => (
                <div key={item.label}>
                  <dt className="text-xs uppercase text-gray-500 dark:text-gray-400">{item.label}</dt>
                  <dd className="text-gray-900 dark:text-white">
                    {item.href ? <a href={item.href} className="hover:text-indigo-600" target={item.href.startsWith('http') ? '_blank' : undefined} rel="noreferrer">{item.value}</a> : item.value}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        )}
        {campuses.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Unidades</h2>
            <ul className="mt-5 space-y-3">
              {campuses.map((campus) => (
                <li key={campus.name}><p className="font-medium text-gray-900 dark:text-white">{campus.name}</p>{campus.address && <p className="text-sm text-gray-600 dark:text-gray-400">{campus.address}</p>}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
