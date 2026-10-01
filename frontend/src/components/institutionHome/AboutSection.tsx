import Link from 'next/link';
import type { PublicProfile } from '@/types/publicSite';

/** Apresentacao da instituicao e como fazer a matricula. */
export default function AboutSection({ profile, hasOpenCalls }: { profile: PublicProfile; hasOpenCalls: boolean }) {
  return (
    <section className="mx-auto grid max-w-6xl gap-10 px-4 py-14 md:grid-cols-2">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Sobre nós</h2>
        <p className="mt-4 whitespace-pre-line text-gray-600 dark:text-gray-400">{profile.about || 'Em breve, mais informações sobre a instituição.'}</p>
      </div>
      <div id="matricula" className="scroll-mt-6 rounded-2xl bg-indigo-50 p-6 dark:bg-indigo-900/20">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Como se matricular</h2>
        <p className="mt-3 whitespace-pre-line text-gray-700 dark:text-gray-300">
          {profile.enrollment_info
            || (hasOpenCalls
              ? 'Escolha uma das inscrições abertas, preencha seus dados e acompanhe a seleção pela área do aluno.'
              : 'Entre em contato com a secretaria pelos canais abaixo para saber das próximas turmas.')}
        </p>
        {hasOpenCalls
          ? <a href="#inscricoes" className="mt-5 inline-block rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700">Ver inscrições abertas</a>
          : <Link href="/login" className="mt-5 inline-block text-sm font-semibold text-indigo-700 dark:text-indigo-300">Já é aluno? Acesse a área do aluno →</Link>}
      </div>
    </section>
  );
}
