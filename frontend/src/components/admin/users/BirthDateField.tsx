import { inputCls, labelCls } from '@/components/common/formStyles';
import { todayIso } from '@/lib/dates';

/** Data de nascimento: define a idade para o reconhecimento facial (16 anos: decide sozinho login e catraca; 18: presenca). */
export default function BirthDateField({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return (
    <label className={labelCls}>Data de nascimento
      <input type="date" max={todayIso()} value={value} onChange={(e) => onChange(e.target.value)} className={`mt-1 ${inputCls}`} />
      <span className="mt-1 block text-xs text-gray-500 dark:text-gray-400">
        A partir de 16 anos a pessoa autoriza sozinha o uso do rosto no login e na catraca (abaixo disso, o responsável);
        a presença por reconhecimento facial exige 18. Sem a data, ela é tratada como menor de 16.
      </span>
    </label>
  );
}
