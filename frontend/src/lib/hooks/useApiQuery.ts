'use client';

import { useCallback, useEffect, useState } from 'react';

interface ApiQueryState<T> {
  data: T | undefined;
  loading: boolean;
  error: unknown;
}

/**
 * Executa `request` ao montar e sempre que ele mudar (memorize com useCallback),
 * ignorando respostas de requisicoes antigas. `reload` refaz a busca sob demanda.
 */
export function useApiQuery<T>(request: () => Promise<T>) {
  const [state, setState] = useState<ApiQueryState<T>>({ data: undefined, loading: true, error: null });
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let active = true;
    request()
      .then((data) => { if (active) setState({ data, loading: false, error: null }); })
      .catch((error: unknown) => { if (active) setState((current) => ({ ...current, loading: false, error })); });
    return () => { active = false; };
  }, [request, version]);

  const reload = useCallback(() => {
    setState((current) => ({ ...current, loading: true }));
    setVersion((current) => current + 1);
  }, []);

  return { ...state, reload };
}
