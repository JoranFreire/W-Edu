import type { RegistrationResult } from '@/types/registration';

/** Mensagem apos a inscricao: vaga garantida ou posicao na lista de espera. */
export function registrationMessage(result: RegistrationResult): string {
  return result.result === 'enrolled' ? 'Inscrição confirmada.' : `Turma lotada: você está na lista de espera (${result.waitlist_position}º).`;
}
