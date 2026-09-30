import type { ConceptBand } from '@/types/assessment';

/** "A:9, B:7, C:5" <-> [{code: 'A', min_value: 9}, ...] (funcoes puras para o formulario). */
export function formatConceptBands(bands: ConceptBand[]): string {
  return bands.map((band) => `${band.code}:${band.min_value}`).join(', ');
}

export function parseConceptBands(text: string): ConceptBand[] {
  return text
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      const [code, value] = part.split(':').map((piece) => piece.trim());
      return { code, min_value: Number(value?.replace(',', '.')) };
    })
    .filter((band) => band.code && Number.isFinite(band.min_value));
}
