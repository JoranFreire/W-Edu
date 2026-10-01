'use client';

import { useCallback } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { saveBlob } from '@/lib/files/saveBlob';
import { useApiQuery } from '@/lib/hooks/useApiQuery';
import { declarationFileName } from '@/lib/secretariat/declarationLinks';
import type { Declaration, DeclarationKind } from '@/types/secretariat';

/** Declaracoes emitidas para a matricula: emissao, download e revogacao. */
export function useDeclarations(enrollmentId: string) {
  const request = useCallback(
    () => api.get<Declaration[]>(endpoints.secretariat.declarations(enrollmentId)).then((response) => response.data),
    [enrollmentId],
  );
  const { data = [], loading, error, reload } = useApiQuery(request);

  const issue = async (kind: DeclarationKind, termId: string | null) => {
    const { data: created } = await api.post<Declaration>(endpoints.secretariat.declarations(enrollmentId), { kind, term_id: termId });
    reload();
    return created;
  };
  const download = async (declaration: Declaration) => {
    const { data: blob } = await api.get<Blob>(endpoints.secretariat.declarationPdf(declaration.id), { responseType: 'blob' });
    saveBlob(blob, declarationFileName(declaration.kind, declaration.validation_code));
  };
  const revoke = async (declarationId: string, reason: string) => {
    await api.post(endpoints.secretariat.declarationRevoke(declarationId), { reason });
    reload();
  };

  return { declarations: data, loading, error, issue, download, revoke };
}
