/** Identificador de URL: minusculas sem acentos, palavras separadas por hifen. */
export function slugify(value: string, maxLength = 80) {
  return value
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, maxLength);
}
