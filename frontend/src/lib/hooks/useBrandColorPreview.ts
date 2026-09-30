'use client';

import { useEffect } from 'react';
import { applyBranding } from '@/lib/institution/branding';
import { useAuthStore } from '@/store/authStore';

/** Aplica a cor em edicao na interface; ao sair, volta a cor salva da instituicao. */
export function useBrandColorPreview(color: string) {
  useEffect(() => {
    applyBranding({ primary_color: color });
    return () => applyBranding(useAuthStore.getState().institution?.branding);
  }, [color]);
}
