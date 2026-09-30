'use client';

import { useState } from 'react';

/** Marca `saving` enquanto a acao roda; erros seguem para quem chamou. */
export function useSubmitting() {
  const [saving, setSaving] = useState(false);
  const run = async (action: () => Promise<void>) => {
    setSaving(true);
    try {
      await action();
    } finally {
      setSaving(false);
    }
  };
  return { saving, run };
}
