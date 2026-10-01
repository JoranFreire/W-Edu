'use client';

import { Suspense } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import PublicShell from '@/components/admissions/PublicShell';
import { applicationStatusLabels, selectionMethodLabels } from '@/lib/academic/admissionLabels';
import { usePublicCall } from '@/lib/hooks/admissions/usePublicCall';

function Result() {
  const callId = Number(useParams<{ callId: string }>().callId);
  const { result, call } = usePublicCall(callId, useSearchParams().get('institution'));
  if (!call) return <p className="text-sm text-gray-500 dark:text-gray-400">Carregando...</p>;
  if (!result) return <p className="text-sm text-gray-500 dark:text-gray-400">Resultado ainda não publicado.</p>;
  return (
    <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resultado: {result.title}</h1>
      <p className="text-sm text-gray-600 dark:text-gray-300">
        Seleção por {selectionMethodLabels[result.method].toLowerCase()}.
        {result.lottery_seed && <> Semente do sorteio: <span className="font-mono">{result.lottery_seed}</span> (permite refazer o sorteio e conferir a ordem).</>}
      </p>
      <table className="min-w-full text-sm">
        <thead className="text-left text-xs uppercase text-gray-500 dark:text-gray-400">
          <tr><th className="py-2">Posição</th><th>Protocolo</th><th>Vaga</th><th>Situação</th></tr>
        </thead>
        <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
          {result.entries.map((entry) => (
            <tr key={entry.protocol} className="text-gray-800 dark:text-gray-200">
              <td className="py-2">{entry.rank}º</td>
              <td className="font-mono">{entry.protocol}</td>
              <td>{entry.seat_kind === 'reserved' ? 'Reservada' : entry.seat_kind === 'general' ? 'Ampla' : '—'}</td>
              <td>{applicationStatusLabels[entry.status]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function PublicResultPage() {
  return <PublicShell><Suspense fallback={null}><Result /></Suspense></PublicShell>;
}
