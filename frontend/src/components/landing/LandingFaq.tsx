const FAQ = [
  { q: 'Preciso instalar alguma coisa?', a: 'Não. A plataforma funciona no navegador, no computador e no celular, para a equipe, os alunos e as famílias.' },
  { q: 'Podemos usar o nosso domínio e a nossa marca?', a: 'Sim. Cada instituição tem cores, logo e página pública próprias, no subdomínio da plataforma ou no seu domínio.' },
  { q: 'Atende cursos gratuitos financiados por programas sociais?', a: 'Sim: editais com sorteio ou análise de perfil, controle de frequência, entrega de lanche e kits e prestação de contas por financiador.' },
  { q: 'Os dados de uma instituição ficam separados das outras?', a: 'Sim. Cada instituição só acessa os próprios dados, com isolamento aplicado também no banco de dados.' },
  { q: 'Uma pessoa pode ter mais de um papel?', a: 'Pode. A mesma conta pode ser professora e aluna, ou funcionária e responsável, com tudo no mesmo menu.' },
];

/** Perguntas frequentes. */
export default function LandingFaq() {
  return (
    <section className="bg-gray-50 py-20 dark:bg-gray-900/60">
      <div className="mx-auto max-w-3xl px-4">
        <h2 className="text-center text-3xl font-bold text-gray-900 dark:text-white">Perguntas frequentes</h2>
        <div className="mt-10 space-y-3">
          {FAQ.map(({ q, a }) => (
            <details key={q} className="group rounded-xl bg-white p-5 ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
              <summary className="cursor-pointer list-none font-medium text-gray-900 dark:text-white">{q}</summary>
              <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">{a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
