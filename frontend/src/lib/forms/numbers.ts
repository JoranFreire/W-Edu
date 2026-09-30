/** Converte o texto de um input numerico opcional: vazio vira null. */
export function toOptionalInt(value: string): number | null {
  if (value.trim() === '') return null;
  const parsed = Number.parseInt(value, 10);
  return Number.isNaN(parsed) ? null : parsed;
}

export function fromOptionalInt(value: number | null | undefined): string {
  return value === null || value === undefined ? '' : String(value);
}
