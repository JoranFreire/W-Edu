'use client';

import { useState } from 'react';
import MyWindowCatalog from '@/components/registration/MyWindowCatalog';
import Spinner from '@/components/common/Spinner';
import { inputCls } from '@/components/common/formStyles';
import { useMyRegistrationWindows } from '@/lib/hooks/registration/useMyRegistrationWindows';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';

export default function RegistrationPage() {
  const terms = useTerminology();
  const { windows, loading, error } = useMyRegistrationWindows();
  const [chosen, setChosen] = useState<number | null>(null);
  useErrorToast(error, 'Erro ao carregar as janelas de matrícula.');
  const current = windows.find((item) => item.window.id === chosen) ?? windows[0];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Matrícula em {terms.subjects.toLowerCase()}</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Escolha as turmas do período respeitando pré-requisitos, horários e vagas.</p>
        </div>
        {windows.length > 1 && (
          <select aria-label="Janela de matrícula" value={current?.window.id ?? ''} onChange={(e) => setChosen(Number(e.target.value))} className={`${inputCls} md:w-80`}>
            {windows.map((item) => <option key={item.window.id} value={item.window.id}>{item.window.name} · {item.program_name}</option>)}
          </select>
        )}
      </div>
      {loading && windows.length === 0 ? <Spinner /> : current
        ? <MyWindowCatalog key={current.window.id} window={current.window} />
        : <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma janela de matrícula aberta no momento.</p>}
    </div>
  );
}
