'use client';

import { useCallback } from 'react';
import { useStoredValue } from '@/lib/hooks/useStoredValue';

export type ViewMode = 'grid' | 'list';

/** Modo de exibicao (grade ou lista) de uma colecao, lembrado por tela no navegador. */
export function useViewMode(scope: string) {
  const [stored, setStored] = useStoredValue(`w-edu-view:${scope}`);
  const mode: ViewMode = stored === 'list' ? 'list' : 'grid';
  const setMode = useCallback((next: ViewMode) => setStored(next), [setStored]);
  return [mode, setMode] as const;
}
