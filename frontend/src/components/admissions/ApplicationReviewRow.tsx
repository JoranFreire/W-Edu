'use client';

import { useState } from 'react';
import { inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import { applicationStatusCls, applicationStatusLabels, documentReviewLabels, schoolingLabels } from '@/lib/academic/admissionLabels';
import { formatMoney } from '@/lib/academic/guardianLabels';
import type { Application, ApplicationDocument, ApplicationReviewInput, DocumentReview, SelectionMethod } from '@/types/admissions';

const BEFORE_SELECTION = ['submitted', 'ineligible'];

/** Inscricao na analise da secretaria: respostas, comprovantes e controles (nota, reserva, aptidao). */
export default function ApplicationReviewRow({ application, method, onReview, onDocument, onDownload }: {
  application: Application;
  method: SelectionMethod;
  onReview: (input: ApplicationReviewInput) => void;
  onDocument: (document: ApplicationDocument, review: DocumentReview) => void;
  onDownload: (document: ApplicationDocument) => void;
}) {
  const [score, setScore] = useState(application.review_score === null ? '' : String(application.review_score));
  const editable = BEFORE_SELECTION.includes(application.status);
  const perCapita = Math.round(application.family_income_cents / Math.max(application.household_size, 1));
  const name = application.applicant.name;
  return (
    <li className="space-y-2 py-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="flex flex-wrap items-center gap-2 font-medium text-gray-900 dark:text-white">
            {application.rank ? `${application.rank}º · ` : ''}{name}
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${applicationStatusCls[application.status]}`}>{applicationStatusLabels[application.status]}</span>
            {application.seat_kind === 'reserved' && <span className="text-xs text-gray-500">vaga reservada</span>}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            <span className="font-mono">{application.protocol}</span> · {application.applicant.email} · nasc. {application.birth_date.split('-').reverse().join('/')} ·{' '}
            {schoolingLabels[application.schooling]} · {formatMoney(perCapita)} por pessoa · {application.city}
            {application.claims_reserved ? ` · concorre à reserva${application.reserved_verified === true ? ' (conferida)' : application.reserved_verified === false ? ' (recusada)' : ''}` : ''}
          </p>
          {application.ineligibility_reasons.length > 0 && <p className="text-xs text-red-700 dark:text-red-300">{application.ineligibility_reasons.join('; ')}</p>}
        </div>
        {editable && (
          <div className="flex flex-wrap items-center gap-2">
            {method === 'review' && (
              <>
                <input type="number" min={0} aria-label={`Nota de ${name}`} value={score} onChange={(e) => setScore(e.target.value)} className={`${inputCls} w-20`} />
                <button onClick={() => onReview({ review_score: Number(score) })} disabled={score === ''} className={secondaryButtonCls}>Salvar nota</button>
              </>
            )}
            {application.claims_reserved && (
              <>
                <button onClick={() => onReview({ reserved_verified: true })} aria-label={`Confirmar reserva de ${name}`} className={secondaryButtonCls}>Reserva ok</button>
                <button onClick={() => onReview({ reserved_verified: false })} aria-label={`Recusar reserva de ${name}`} className={secondaryButtonCls}>Recusar reserva</button>
              </>
            )}
            {application.status === 'submitted' ? (
              <button onClick={() => { const reason = globalThis.prompt('Motivo da inaptidão'); if (reason) onReview({ eligible: false, reason }); }}
                aria-label={`Tornar inapta ${name}`} className={secondaryButtonCls}>Inapta</button>
            ) : (
              <button onClick={() => onReview({ eligible: true })} aria-label={`Tornar apta ${name}`} className={secondaryButtonCls}>Apta</button>
            )}
          </div>
        )}
      </div>
      {application.documents.length > 0 && (
        <ul className="space-y-1 text-xs text-gray-700 dark:text-gray-300">
          {application.documents.map((document) => (
            <li key={document.id} className="flex flex-wrap items-center gap-2">
              <button onClick={() => onDownload(document)} className="text-indigo-600 hover:underline dark:text-indigo-400">{document.kind}: {document.file_name}</button>
              <span>{documentReviewLabels[document.review]}</span>
              {document.review !== 'accepted' && <button onClick={() => onDocument(document, 'accepted')} aria-label={`Aceitar ${document.kind} de ${name}`} className="text-emerald-700 hover:underline dark:text-emerald-300">aceitar</button>}
              {document.review !== 'rejected' && <button onClick={() => onDocument(document, 'rejected')} aria-label={`Recusar ${document.kind} de ${name}`} className="text-red-700 hover:underline dark:text-red-300">recusar</button>}
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}
