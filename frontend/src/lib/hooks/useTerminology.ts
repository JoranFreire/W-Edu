'use client';

import { terminologyFor } from '@/lib/institution/terminology';
import { useAuthStore } from '@/store/authStore';

/** Nomenclatura academica da instituicao ativa. */
export function useTerminology() {
  const type = useAuthStore((state) => state.institution?.type);
  return terminologyFor(type);
}
