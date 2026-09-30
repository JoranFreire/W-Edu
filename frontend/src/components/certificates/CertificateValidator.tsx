'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useCertificateValidation } from '@/lib/hooks/useCertificateValidation';
import CertificateValidationResult from './CertificateValidationResult';

/** Formulario de validacao; valida automaticamente o `?code=` do link publico. */
export default function CertificateValidator() {
  const codeParam = useSearchParams().get('code');
  const [code, setCode] = useState(codeParam ?? '');
  const { validation, loading, error, validate } = useCertificateValidation(codeParam);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    validate(code);
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="mt-6 space-y-3">
        <input
          value={code}
          onChange={(event) => setCode(event.target.value)}
          placeholder="Código de validação"
          aria-label="Código de validação"
          className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 font-mono text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
        />
        <button disabled={loading} className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
          {loading ? 'Validando...' : 'Validar'}
        </button>
      </form>
      {error && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>}
      {validation && !loading && <CertificateValidationResult validation={validation} />}
    </>
  );
}
