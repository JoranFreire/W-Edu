import { ArchiveBoxIcon, CheckCircleIcon, DocumentDuplicateIcon, TrashIcon } from '@heroicons/react/24/outline';
import { inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import { curriculumStatusLabels } from '@/lib/academic/labels';
import type { Curriculum } from '@/types/academic';
import CurriculumStatusBadge from './CurriculumStatusBadge';

/** Seletor de versao e acoes do ciclo de vida (ativar, arquivar, nova versao, excluir). */
export default function CurriculumVersionBar({ curricula, selected, canDelete, onSelect, onActivate, onArchive, onNewVersion, onDelete }: {
  curricula: Curriculum[];
  selected: Curriculum;
  canDelete: boolean;
  onSelect: (id: string) => void;
  onActivate: () => void;
  onArchive: () => void;
  onNewVersion: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <select aria-label="Versão da matriz" value={selected.id} onChange={(e) => onSelect(e.target.value)} className={`${inputCls} w-auto`}>
        {curricula.map((curriculum) => (
          <option key={curriculum.id} value={curriculum.id}>
            Versão {curriculum.version} ({curriculumStatusLabels[curriculum.status]})
          </option>
        ))}
      </select>
      <CurriculumStatusBadge status={selected.status} />
      <div className="ml-auto flex flex-wrap gap-2">
        {selected.status === 'draft' && (
          <button onClick={onActivate} className={secondaryButtonCls}><CheckCircleIcon className="h-4 w-4" /> Tornar vigente</button>
        )}
        {selected.status === 'active' && (
          <button onClick={onArchive} className={secondaryButtonCls}><ArchiveBoxIcon className="h-4 w-4" /> Arquivar</button>
        )}
        <button onClick={onNewVersion} className={secondaryButtonCls}><DocumentDuplicateIcon className="h-4 w-4" /> Nova versão</button>
        {canDelete && selected.status === 'draft' && (
          <button onClick={onDelete} aria-label="Excluir rascunho" className={secondaryButtonCls}><TrashIcon className="h-4 w-4" /></button>
        )}
      </div>
    </div>
  );
}
