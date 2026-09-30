import { isAxiosError } from 'axios';

/** Mensagem `detail` da API quando for texto; senao, o fallback informado. */
export function apiErrorMessage(error: unknown, fallback: string): string {
  const detail = isAxiosError(error) ? error.response?.data?.detail : undefined;
  return typeof detail === 'string' ? detail : fallback;
}
