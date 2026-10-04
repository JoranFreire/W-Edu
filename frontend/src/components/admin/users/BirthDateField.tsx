import { inputCls, labelCls } from '@/components/common/formStyles';
import { todayIso } from '@/lib/dates';

/** Data de nascimento: define a maioridade, exigida pela presenca por reconhecimento facial. */
export default function BirthDateField({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return (
    <label className={labelCls}>Data de nascimento
      <input type="date" max={todayIso()} value={value} onChange={(e) => onChange(e.target.value)} className={`mt-1 ${inputCls}`} />
      <span className="mt-1 block text-xs text-gray-500 dark:text-gray-400">
        Define se a pessoa é maior de idade. Sem a data, ela não pode usar a presença por reconhecimento facial.
      </span>
    </label>
  );
}
