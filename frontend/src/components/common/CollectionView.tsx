import { Fragment, type Key, type ReactNode } from 'react';
import type { ViewMode } from '@/lib/hooks/useViewMode';

const gridCls = 'grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3';
const listCls = 'divide-y divide-gray-200 overflow-hidden rounded-xl border border-gray-200 bg-white dark:divide-gray-700 dark:border-gray-700 dark:bg-gray-800';

/** Mesma colecao em grade de cartoes ou em lista de linhas, conforme o modo escolhido. */
export default function CollectionView<T>({ mode, items, itemKey, renderCard, renderRow, label }: {
  mode: ViewMode;
  items: T[];
  itemKey: (item: T) => Key;
  renderCard: (item: T) => ReactNode;
  renderRow: (item: T) => ReactNode;
  label?: string;
}) {
  if (mode === 'list') {
    return (
      <ul aria-label={label} className={listCls}>
        {items.map((item) => <li key={itemKey(item)}>{renderRow(item)}</li>)}
      </ul>
    );
  }
  return (
    <div className={gridCls}>
      {items.map((item) => <Fragment key={itemKey(item)}>{renderCard(item)}</Fragment>)}
    </div>
  );
}
