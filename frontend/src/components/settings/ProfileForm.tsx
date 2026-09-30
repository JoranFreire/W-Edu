'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { apiErrorMessage } from '@/lib/api/errors';
import type { StudentProfileInput } from '@/lib/hooks/useStudentProfile';
import type { Student, StudentProfile } from '@/types/auth';

const inputCls = 'block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white';
const labelCls = 'block text-sm font-medium text-gray-700 dark:text-gray-300';

const fields: Array<{ key: keyof StudentProfileInput; label: string }> = [
  { key: 'phone', label: 'Telefone' },
  { key: 'document', label: 'Documento' },
  { key: 'position', label: 'Cargo' },
  { key: 'department', label: 'Departamento' },
];

/** Formulario de nome e perfil; inicia com os valores salvos recebidos por props. */
export default function ProfileForm({ student, profile, onSave }: {
  student: Student;
  profile: StudentProfile;
  onSave: (name: string, profile: StudentProfileInput) => Promise<void>;
}) {
  const [name, setName] = useState(student.name);
  const [values, setValues] = useState<Record<keyof StudentProfileInput, string>>({
    phone: profile.phone ?? '',
    document: profile.document ?? '',
    position: profile.position ?? '',
    department: profile.department ?? '',
    bio: profile.bio ?? '',
  });
  const [saving, setSaving] = useState(false);

  const update = (key: keyof StudentProfileInput, value: string) => setValues((current) => ({ ...current, [key]: value }));

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = Object.fromEntries(Object.entries(values).map(([key, value]) => [key, value || null])) as StudentProfileInput;
      await onSave(name, payload);
      toast.success('Perfil atualizado.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao salvar perfil.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={labelCls}>
          Nome
          <input value={name} onChange={(e) => setName(e.target.value)} className={`${inputCls} mt-1`} />
        </label>
        <label className={labelCls}>
          E-mail
          <input value={student.email} disabled className="mt-1 block w-full cursor-not-allowed rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400" />
        </label>
        {fields.map((field) => (
          <label key={field.key} className={labelCls}>
            {field.label}
            <input value={values[field.key]} onChange={(e) => update(field.key, e.target.value)} className={`${inputCls} mt-1`} />
          </label>
        ))}
      </div>
      <label className={labelCls}>
        Bio
        <textarea value={values.bio} onChange={(e) => update('bio', e.target.value)} rows={4} className={`${inputCls} mt-1`} />
      </label>
      <button
        type="button"
        onClick={handleSave}
        disabled={saving}
        className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
      >
        {saving ? 'Salvando...' : 'Salvar alterações'}
      </button>
    </div>
  );
}
