/** Valor para `<input type="datetime-local">` a partir de uma data ISO. */
export const toDateTimeLocal = (value: string) => value.slice(0, 16);

/** Data ISO (UTC) a partir do valor de um `<input type="datetime-local">`. */
export const toApiDateTime = (value: string) => new Date(value).toISOString();

export const dayLabels = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];

/** 'AAAA-MM-DD' -> 'DD/MM/AAAA' sem converter fuso (datas puras do calendario academico). */
export const formatIsoDate = (value: string) => value.split('-').reverse().join('/');
