import type { InstitutionBranding } from '@/types/institution';

const HEX_COLOR = /^#[0-9a-fA-F]{6}$/;

// A interface usa a paleta indigo do Tailwind; a cor da instituicao substitui os tons principais.
const SHADES: Record<string, string> = {
  '--color-indigo-400': 'color-mix(in oklab, VAR 70%, white)',
  '--color-indigo-500': 'color-mix(in oklab, VAR 85%, white)',
  '--color-indigo-600': 'VAR',
  '--color-indigo-700': 'color-mix(in oklab, VAR 85%, black)',
};

export function isValidBrandColor(color: string | undefined | null): color is string {
  return !!color && HEX_COLOR.test(color);
}

export function applyBranding(branding: InstitutionBranding | undefined | null) {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  const color = branding?.primary_color;
  for (const [variable, value] of Object.entries(SHADES)) {
    if (isValidBrandColor(color)) root.style.setProperty(variable, value.replace('VAR', color));
    else root.style.removeProperty(variable);
  }
}

export function institutionDisplayName(institution: { name: string; branding?: InstitutionBranding } | null | undefined) {
  return institution?.branding?.display_name || institution?.name || 'W-Edu';
}
