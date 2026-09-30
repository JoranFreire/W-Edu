import { isValidBrandColor } from '@/lib/institution/branding';
import { inputCls, labelCls } from '@/components/common/formStyles';

export const DEFAULT_BRAND_COLOR = '#4f46e5';

export interface BrandingValues {
  display_name: string;
  primary_color: string;
  logo_url: string;
}

export default function BrandingFields({ values, namePlaceholder, onChange }: {
  values: BrandingValues;
  namePlaceholder: string;
  onChange: (values: BrandingValues) => void;
}) {
  const set = (key: keyof BrandingValues, value: string) => onChange({ ...values, [key]: value });

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <label className={labelCls}>
        Nome exibido no menu
        <input value={values.display_name} placeholder={namePlaceholder} onChange={(e) => set('display_name', e.target.value)} className={`${inputCls} mt-1`} />
      </label>
      <label className={labelCls}>
        Cor principal
        <div className="mt-1 flex gap-2">
          <input
            type="color"
            aria-label="Selecionar cor principal"
            value={isValidBrandColor(values.primary_color) ? values.primary_color : DEFAULT_BRAND_COLOR}
            onChange={(e) => set('primary_color', e.target.value)}
            className="h-10 w-12 cursor-pointer rounded-lg border border-gray-300 bg-white p-1 dark:border-gray-600 dark:bg-gray-900"
          />
          <input value={values.primary_color} placeholder={DEFAULT_BRAND_COLOR} onChange={(e) => set('primary_color', e.target.value)} className={inputCls} />
        </div>
      </label>
      <label className={`${labelCls} sm:col-span-2`}>
        URL do logotipo
        <input value={values.logo_url} placeholder="https://..." onChange={(e) => set('logo_url', e.target.value)} className={`${inputCls} mt-1`} />
      </label>
    </div>
  );
}
