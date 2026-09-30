'use client';

import { useCallback, useState } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import type { DeclarationValidation } from '@/types/secretariat';

/** Validacao publica de uma declaracao pelo codigo; `validate` dispara nova consulta. */
export function useDeclarationValidation(initialCode: string | null) {
  const [submitted, setSubmitted] = useState<{ code: string } | null>(() => (initialCode?.trim() ? { code: initialCode.trim() } : null));
  const request = useCallback(
    () => submitted
      ? api.get<DeclarationValidation>(endpoints.secretariat.validateDeclaration(submitted.code)).then((response) => response.data)
      : Promise.resolve(null),
    [submitted],
  );
  const query = useApiQuery(request);

  const validate = (code: string) => {
    if (code.trim()) setSubmitted({ code: code.trim() });
  };

  return {
    validation: query.data ?? null,
    loading: submitted !== null && query.loading,
    error: query.error ? 'Não foi possível validar este código.' : null,
    validate,
  };
}
