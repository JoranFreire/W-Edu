'use client';

import type { ReactNode } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const sizes = { sm: 'max-w-md', md: 'max-w-lg', lg: 'max-w-xl', xl: 'max-w-2xl' };

export default function Modal({ title, description, size = 'md', onClose, children }: {
  title: string;
  description?: ReactNode;
  size?: keyof typeof sizes;
  onClose: () => void;
  children: ReactNode;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 py-6" role="dialog" aria-modal="true" aria-label={title}>
      <div className={`max-h-full w-full overflow-y-auto ${sizes[size]} rounded-xl bg-white p-6 shadow-xl dark:bg-gray-800`}>
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h2>
            {description && <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{description}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar modal"
            className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-700 dark:hover:text-white"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
