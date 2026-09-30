'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import type { CheckinToken, ScheduledMeeting } from '@/types/schedule';

/** Token de check-in por QR Code de um encontro e o link publico correspondente. */
export function useCheckinToken() {
  const [token, setToken] = useState<CheckinToken | null>(null);
  const [meeting, setMeeting] = useState<ScheduledMeeting | null>(null);

  const url = token && typeof window !== 'undefined' ? `${window.location.origin}/check-in/${token.token}` : '';

  const generate = async (target: ScheduledMeeting) => {
    try {
      const { data } = await api.post<CheckinToken>(endpoints.schedule.checkinTokens(target.id), { valid_minutes: 60 });
      setToken(data);
      setMeeting(target);
    } catch { toast.error('Erro ao gerar token de check-in.'); }
  };

  const copyUrl = async () => {
    if (!url) return;
    try {
      await navigator.clipboard.writeText(url);
      toast.success('Link de check-in copiado.');
    } catch {
      toast.error('Não foi possível copiar o link.');
    }
  };

  const clear = () => { setToken(null); setMeeting(null); };

  return { token, meeting, url, generate, copyUrl, clear };
}
