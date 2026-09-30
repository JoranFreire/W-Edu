'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { primaryButtonCls, inputCls } from '@/components/common/formStyles';
import { declarationKindLabels } from '@/lib/academic/secretariatLabels';
import { useDeclarationValidation } from '@/lib/hooks/useDeclarationValidation';

/** Formulario publico de validacao; valida automaticamente o `?code=` do link. */
export default function DeclarationValidator() {
  const codeParam = useSearchParams().get('code');
  const [code, setCode] = useState(codeParam ?? '');
  const { validation, loading, error, validate } = useDeclarationValidation(codeParam);

  return (
    <>
      <form onSubmit={(event) => { event.preventDefault(); validate(code); }} className="mt-6 space-y-3">
        <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Código de validação" aria-label="Código de validação" className={`${inputCls} font-mono`} />
        <button disabled={loading} className={`${primaryButtonCls} w-full`}>{loading ? 'Validando...' : 'Validar'}</button>
      </form>
      {error && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>}
      {validation && !loading && (
        <div role="status" className={`mt-5 rounded-lg border p-4 text-sm ${validation.valid ? 'border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-900/20' : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'}`}>
          <p className={`flex items-center gap-2 font-semibold ${validation.valid ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'}`}>
            {validation.valid ? <CheckCircleIcon className="h-5 w-5" /> : <XCircleIcon className="h-5 w-5" />}
            {validation.message}
          </p>
          {validation.kind && (
            <dl className="mt-3 space-y-1 text-gray-700 dark:text-gray-300">
              <div><dt className="inline font-medium">Tipo: </dt><dd className="inline">{declarationKindLabels[validation.kind]}</dd></div>
              <div><dt className="inline font-medium">Aluno: </dt><dd className="inline">{validation.student_name}</dd></div>
              <div><dt className="inline font-medium">Instituição: </dt><dd className="inline">{validation.institution_name}</dd></div>
              {validation.issued_at && <div><dt className="inline font-medium">Emissão: </dt><dd className="inline">{new Date(validation.issued_at).toLocaleDateString('pt-BR')}</dd></div>}
            </dl>
          )}
        </div>
      )}
    </>
  );
}
