'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { saveBlob } from '@/lib/files/saveBlob';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import { declarationFileName } from '@/lib/secretariat/declarationLinks';
import type { Declaration } from '@/types/secretariat';

/** Declaracoes emitidas para o aluno autenticado, com download do PDF. */
export function useMyDeclarations() {
  const request = useCallback(() => api.get<Declaration[]>(endpoints.secretariat.myDeclarations).then((response) => response.data), []);
  const { data = [], error } = useApiQuery(request);

  const download = async (declaration: Declaration) => {
    const { data: blob } = await api.get<Blob>(endpoints.secretariat.myDeclarationPdf(declaration.id), { responseType: 'blob' });
    saveBlob(blob, declarationFileName(declaration.kind, declaration.validation_code));
  };

  return { declarations: data, error, download };
}
