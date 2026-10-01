'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { applicationStatusCls, applicationStatusLabels, documentReviewLabels } from '@/lib/academic/admissionLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatDateTime } from '@/lib/dates';
import type { Application } from '@/types/admissions';

const ACCEPTS_DOCUMENTS = ['submitted', 'ineligible', 'waitlisted', 'selected'];

/** Inscricao do candidato: situacao, motivos, comprovantes e acoes (confirmar, desistir, cancelar). */
export default function MyApplicationCard({ application, requiredDocuments, onUpload, onAct }: {
  application: Application;
  requiredDocuments: string[];
  onUpload: (kind: string, file: File) => Promise<void>;
  onAct: (action: 'withdraw' | 'confirm' | 'decline') => Promise<void>;
}) {
  const [chosenKind, setKind] = useState<string | null>(null);
  // Os comprovantes do edital podem chegar depois do cartao: o tipo vale so se estiver entre as opcoes.
  const kindOptions = [...requiredDocuments, 'Outro'];
  const kind = chosenKind && kindOptions.includes(chosenKind) ? chosenKind : kindOptions[0];
  const [file, setFile] = useState<File | null>(null);
  const run = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Não foi possível concluir.'));
    }
  };
  const status = application.status;
  return (
    <li className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="flex flex-wrap items-center gap-2 font-medium text-gray-900 dark:text-white">
            {application.call_title}
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${applicationStatusCls[status]}`}>{applicationStatusLabels[status]}</span>
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Protocolo <span className="font-mono">{application.protocol}</span>
            {application.rank ? ` · ${application.rank}º na classificação` : ''}
            {status === 'selected' && application.confirm_until ? ` · confirme até ${formatDateTime(application.confirm_until)}` : ''}
          </p>
          {application.ineligibility_reasons.length > 0 && (
            <p className="text-xs text-red-700 dark:text-red-300">{application.ineligibility_reasons.join('; ')}</p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {status === 'selected' && (
            <button onClick={() => run(() => onAct('confirm'), 'Vaga confirmada.')} aria-label={`Confirmar vaga em ${application.call_title}`} className={primaryButtonCls}>Confirmar vaga</button>
          )}
          {(status === 'selected' || status === 'waitlisted') && (
            <button onClick={() => globalThis.confirm('Desistir da vaga?') && run(() => onAct('decline'), 'Desistência registrada.')} className={secondaryButtonCls}>Desistir</button>
          )}
          {(status === 'submitted' || status === 'ineligible') && (
            <button onClick={() => run(() => onAct('withdraw'), 'Inscrição cancelada.')} className={secondaryButtonCls}>Cancelar inscrição</button>
          )}
        </div>
      </div>
      {application.documents.length > 0 && (
        <ul className="text-xs text-gray-600 dark:text-gray-300">
          {application.documents.map((document) => <li key={document.id}>{document.kind}: {document.file_name} · {documentReviewLabels[document.review]}</li>)}
        </ul>
      )}
      {ACCEPTS_DOCUMENTS.includes(status) && (
        <form onSubmit={(event) => { event.preventDefault(); if (file) run(() => onUpload(kind, file), 'Comprovante enviado.'); }} className="flex flex-wrap items-center gap-2">
          <select aria-label="Tipo de comprovante" value={kind} onChange={(e) => setKind(e.target.value)} className={`${inputCls} w-48`}>
            {kindOptions.map((option) => <option key={option} value={option}>{option}</option>)}
          </select>
          <input type="file" accept=".pdf,.jpg,.jpeg,.png" aria-label="Arquivo do comprovante" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="text-sm" />
          <button disabled={!file} className={secondaryButtonCls}>Enviar comprovante</button>
        </form>
      )}
    </li>
  );
}
