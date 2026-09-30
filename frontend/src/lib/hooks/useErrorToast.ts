'use client';

import { useEffect } from 'react';
import toast from 'react-hot-toast';

/** Mostra um toast quando `error` passa a ter valor (ex.: falha de carregamento). */
export function useErrorToast(error: unknown, message: string) {
  useEffect(() => {
    if (error) toast.error(message);
  }, [error, message]);
}
