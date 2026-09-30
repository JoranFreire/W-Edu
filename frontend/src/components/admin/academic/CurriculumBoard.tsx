import { PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';
import { dangerIconButtonCls, iconButtonCls } from '@/components/common/formStyles';
import { componentKindLabels } from '@/lib/academic/labels';
import type { CurriculumComponent } from '@/types/academic';

function groupByTerm(components: CurriculumComponent[]): [number, CurriculumComponent[]][] {
  const groups = new Map<number, CurriculumComponent[]>();
  for (const component of components) {
    groups.set(component.term_number, [...(groups.get(component.term_number) ?? []), component]);
  }
  return [...groups.entries()].sort(([a], [b]) => a - b);
}

/** Componentes agrupados por periodo; acoes so aparecem em rascunho. */
export default function CurriculumBoard({ components, termLabel, editable, onEdit, onRemove }: {
  components: CurriculumComponent[];
  termLabel: string;
  editable: boolean;
  onEdit: (component: CurriculumComponent) => void;
  onRemove: (component: CurriculumComponent) => void;
}) {
  if (components.length === 0) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum componente na matriz.</p>;
  }
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {groupByTerm(components).map(([term, items]) => (
        <section key={term} aria-label={`${termLabel} ${term}`} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <h3 className="mb-3 flex items-center justify-between text-sm font-semibold text-gray-900 dark:text-white">
            <span>{termLabel} {term}</span>
            <span className="text-xs font-normal text-gray-500">{items.reduce((sum, item) => sum + item.hours, 0)}h</span>
          </h3>
          <ul className="space-y-2">
            {items.map((component) => (
              <li key={component.id} className="flex items-start justify-between gap-2 rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-900">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-gray-900 dark:text-white">{component.subject.code} · {component.subject.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {componentKindLabels[component.kind]} · {component.hours}h{component.credits !== null ? ` · ${component.credits} cr` : ''}
                  </p>
                </div>
                {editable && (
                  <div className="flex shrink-0">
                    <button onClick={() => onEdit(component)} aria-label={`Editar componente ${component.subject.code}`} className={iconButtonCls}>
                      <PencilSquareIcon className="h-4 w-4" />
                    </button>
                    <button onClick={() => onRemove(component)} aria-label={`Remover componente ${component.subject.code}`} className={dangerIconButtonCls}>
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
