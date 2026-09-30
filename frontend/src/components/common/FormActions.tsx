import { primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';

/** Botoes Cancelar/Salvar do rodape de formularios em modal. */
export default function FormActions({ saving, onCancel, submitLabel = 'Salvar' }: {
  saving: boolean;
  onCancel: () => void;
  submitLabel?: string;
}) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button type="button" onClick={onCancel} className={secondaryButtonCls}>Cancelar</button>
      <button type="submit" disabled={saving} className={primaryButtonCls}>{saving ? 'Salvando...' : submitLabel}</button>
    </div>
  );
}
