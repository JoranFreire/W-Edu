import { IdentificationIcon } from '@heroicons/react/24/outline';
import DossierSection from '@/components/admin/users/dossier/DossierSection';
import type { DossierContact } from '@/types/userDossier';

const FIELDS: { key: keyof DossierContact; label: string }[] = [
  { key: 'phone', label: 'Telefone' },
  { key: 'document', label: 'Documento' },
  { key: 'position', label: 'Cargo' },
  { key: 'department', label: 'Departamento' },
  { key: 'bio', label: 'Observações' },
];

export default function ContactSection({ contact }: { contact: DossierContact }) {
  const filled = FIELDS.filter(({ key }) => contact[key]);
  return (
    <DossierSection title="Dados pessoais" icon={IdentificationIcon} isEmpty={filled.length === 0} emptyText="Nenhum dado de contato cadastrado.">
      <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
        {filled.map(({ key, label }) => (
          <div key={key} className={key === 'bio' ? 'sm:col-span-2' : ''}>
            <dt className="text-xs text-gray-500 dark:text-gray-400">{label}</dt>
            <dd className="text-gray-900 dark:text-white">{contact[key]}</dd>
          </div>
        ))}
      </dl>
    </DossierSection>
  );
}
