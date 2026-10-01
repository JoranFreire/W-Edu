'use client';

import { useQrScanner } from '@/lib/hooks/social/useQrScanner';

/** Visor da camera; sem camera (ou sem permissao), avisa para digitar o codigo. */
export default function QrScanner({ active, onCode }: { active: boolean; onCode: (value: string) => void }) {
  const { videoRef, state } = useQrScanner(active, onCode);
  if (state === 'unavailable') {
    return <p className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800 dark:bg-amber-900/20 dark:text-amber-200">Câmera indisponível (permissão negada ou acesso sem HTTPS). Digite o código abaixo do QR.</p>;
  }
  return (
    <div className="relative mx-auto aspect-square w-full max-w-sm overflow-hidden rounded-xl bg-black">
      <video ref={videoRef} muted playsInline className="h-full w-full object-cover" aria-label="Câmera para ler o QR" />
      <div className="pointer-events-none absolute inset-10 rounded-lg border-2 border-white/80" />
      {state === 'starting' && <p className="absolute inset-x-0 bottom-3 text-center text-xs text-white">Abrindo a câmera…</p>}
    </div>
  );
}
