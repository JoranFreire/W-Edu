/** Valor para `<input type="datetime-local">` a partir de uma data ISO. */
export const toDateTimeLocal = (value: string) => value.slice(0, 16);

/** Data ISO (UTC) a partir do valor de um `<input type="datetime-local">`. */
export const toApiDateTime = (value: string) => new Date(value).toISOString();

export const dayLabels = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];

/** 'AAAA-MM-DD' -> 'DD/MM/AAAA' sem converter fuso (datas puras do calendario academico). */
export const formatIsoDate = (value: string) => value.split('-').reverse().join('/');

/** Data local de hoje em 'AAAA-MM-DD'. */
export function todayIso(): string {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60_000).toISOString().slice(0, 10);
}

/** Valor local para `<input type="datetime-local">` a partir de uma data ISO com fuso. */
export function isoToLocalInput(value: string): string {
  const date = new Date(value);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
}

/** Data e hora locais curtas (DD/MM/AAAA HH:MM). */
export const formatDateTime = (value: string) =>
  new Date(value).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
