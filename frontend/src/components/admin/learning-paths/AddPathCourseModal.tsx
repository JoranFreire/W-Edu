'use client';

import { useState } from 'react';
import Modal from '@/components/common/Modal';
import type { Course } from '@/types/course';

export default function AddPathCourseModal({ availableCourses, onAdd, onClose }: {
  availableCourses: Course[];
  onAdd: (courseId: string) => void;
  onClose: () => void;
}) {
  const [selectedId, setSelectedId] = useState('');

  return (
    <Modal title="Adicionar curso" description="Escolha um curso para incluir na trilha." size="sm" onClose={onClose}>
      <select aria-label="Curso" value={selectedId} onChange={(e) => setSelectedId(e.target.value)} className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white">
        <option value="">Selecione um curso</option>
        {availableCourses.map((course) => <option key={course.id} value={course.id}>{course.name}</option>)}
      </select>
      <div className="mt-5 flex justify-end gap-3">
        <button type="button" onClick={onClose} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">Cancelar</button>
        <button type="button" disabled={!selectedId} onClick={() => onAdd(selectedId)} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60">Adicionar</button>
      </div>
    </Modal>
  );
}
