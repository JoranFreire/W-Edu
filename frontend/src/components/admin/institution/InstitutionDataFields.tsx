import { type InstitutionType, institutionTypeLabels } from '@/types/institution';
import { inputCls, labelCls } from '@/components/common/formStyles';

export interface InstitutionDataValues {
  name: string;
  legal_name: string;
  document: string;
  type: InstitutionType;
}

export default function InstitutionDataFields({ values, onChange }: {
  values: InstitutionDataValues;
  onChange: (values: InstitutionDataValues) => void;
}) {
  const set = <K extends keyof InstitutionDataValues>(key: K, value: InstitutionDataValues[K]) => onChange({ ...values, [key]: value });

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <label className={labelCls}>
        Nome
        <input value={values.name} onChange={(e) => set('name', e.target.value)} className={`${inputCls} mt-1`} />
      </label>
      <label className={labelCls}>
        Tipo
        <select value={values.type} onChange={(e) => set('type', e.target.value as InstitutionType)} className={`${inputCls} mt-1`}>
          {Object.entries(institutionTypeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </label>
      <label className={labelCls}>
        Razão social
        <input value={values.legal_name} onChange={(e) => set('legal_name', e.target.value)} className={`${inputCls} mt-1`} />
      </label>
      <label className={labelCls}>
        CNPJ
        <input value={values.document} onChange={(e) => set('document', e.target.value)} className={`${inputCls} mt-1`} />
      </label>
    </div>
  );
}
