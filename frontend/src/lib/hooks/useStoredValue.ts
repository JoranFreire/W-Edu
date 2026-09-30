'use client';

import { useCallback, useSyncExternalStore } from 'react';

const CHANGE_EVENT = 'wedu:storage';

function subscribe(onChange: () => void) {
  window.addEventListener('storage', onChange);
  window.addEventListener(CHANGE_EVENT, onChange);
  return () => {
    window.removeEventListener('storage', onChange);
    window.removeEventListener(CHANGE_EVENT, onChange);
  };
}

function readStorage(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

/** Valor persistido no localStorage, sincronizado entre componentes e abas. `null` quando ausente. */
export function useStoredValue(key: string) {
  const value = useSyncExternalStore(subscribe, () => readStorage(key), () => null);

  const setValue = useCallback((next: string | null) => {
    try {
      if (next === null) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, next);
    } catch {
      // Armazenamento indisponivel (modo privado): mantem apenas a sessao atual sem persistir.
    }
    window.dispatchEvent(new Event(CHANGE_EVENT));
  }, [key]);

  return [value, setValue] as const;
}
