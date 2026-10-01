/** Variaveis `{nome}` usadas num texto de template, na ordem em que aparecem e sem repeticao. */
export function templateVariables(...texts: string[]): string[] {
  const found = texts.flatMap((text) => [...text.matchAll(/\{(\w+)\}/g)].map((match) => match[1]));
  return [...new Set(found)];
}
