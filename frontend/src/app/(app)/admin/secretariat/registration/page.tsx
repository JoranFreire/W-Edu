'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import RegistrationWindowFormModal from '@/components/registration/RegistrationWindowFormModal';
import RegistrationWindowsList from '@/components/registration/RegistrationWindowsList';
import BackButton from '@/components/common/BackButton';
import SectionHeader from '@/components/common/SectionHeader';
import { sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { usePrograms } from '@/lib/hooks/admin/academic/usePrograms';
import { useRegistrationWindows } from '@/lib/hooks/registration/useRegistrationWindows';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { RegistrationWindow, RegistrationWindowInput } from '@/types/registration';

type Editing = RegistrationWindow | 'new' | null;

/** Janelas de matricula por disciplina (periodo, programa, prazo e limite de creditos). */
export default function RegistrationWindowsPage() {
  const router = useRouter();
  const { windows, error, save, remove } = useRegistrationWindows();
  const { terms } = useAcademicTerms();
  const { programs } = usePrograms();
  const [editing, setEditing] = useState<Editing>(null);
  useErrorToast(error, 'Erro ao carregar as janelas.');

  const handleSave = async (input: RegistrationWindowInput) => {
    await save(editing === 'new' || editing === null ? null : editing.id, input);
    toast.success('Janela salva.');
    setEditing(null);
  };
  const handleRemove = async (item: RegistrationWindow) => {
    if (!globalThis.confirm(`Remover a janela "${item.name}"?`)) return;
    try {
      await remove(item.id);
      toast.success('Janela removida.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível remover.'));
    }
  };

  return (
    <div className="space-y-6">
      <BackButton label="Secretaria" onClick={() => router.push('/admin/secretariat')} />
      <section className={`${sectionCls} space-y-4`}>
        <SectionHeader
          title="Janelas de matrícula"
          description="Prazo em que os alunos escolhem as disciplinas do período, com limite de créditos e lista de espera."
          actionLabel="Nova janela"
          onAction={() => setEditing('new')}
        />
        <RegistrationWindowsList windows={windows} onEdit={setEditing} onRemove={handleRemove} />
      </section>
      {editing && (
        <RegistrationWindowFormModal
          window={editing === 'new' ? undefined : editing}
          terms={terms}
          programs={programs}
          onSave={handleSave}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}
