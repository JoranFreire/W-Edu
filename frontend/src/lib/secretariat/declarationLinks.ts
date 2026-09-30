/** Link publico de validacao impresso/compartilhado com a declaracao. */
export function declarationValidationUrl(code: string): string {
  return typeof window === 'undefined' ? '' : `${window.location.origin}/validate-declaration?code=${encodeURIComponent(code)}`;
}

export function declarationFileName(kind: string, code: string): string {
  return `declaracao_${kind}_${code}.pdf`;
}
