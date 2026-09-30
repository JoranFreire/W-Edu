'use client';

import { useEffect } from 'react';
import { usePublicInstitution } from '@/lib/hooks/usePublicInstitution';
import { applyBranding, institutionDisplayName } from '@/lib/institution/branding';

/** Cabecalho do login com a marca da instituicao do subdominio (ou do W-Edu). */
export default function LoginBrand() {
  const institution = usePublicInstitution();
  const name = institution ? institutionDisplayName(institution) : 'W-Edu';
  const logoUrl = institution?.branding.logo_url;

  useEffect(() => {
    applyBranding(institution?.branding);
  }, [institution]);

  return (
    <div className="text-center">
      {logoUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={logoUrl} alt="" className="mx-auto h-16 w-16 rounded-2xl bg-white object-contain shadow-lg" />
      ) : (
        <div className="mx-auto h-16 w-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
          <span className="text-white text-2xl font-bold">{name.charAt(0).toUpperCase()}</span>
        </div>
      )}
      <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">{institution ? name : 'Bem-vindo ao W-Edu'}</h2>
      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Entre com suas credenciais para continuar</p>
    </div>
  );
}
