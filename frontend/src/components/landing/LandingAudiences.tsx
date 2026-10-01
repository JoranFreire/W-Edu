const AUDIENCES = [
  { title: 'Escolas', text: 'Etapas de ensino, séries e bimestres, agenda de tarefas e portal da família com boletim, ocorrências e mensalidades.' },
  { title: 'Faculdades e universidades', text: 'Matriz por créditos, matrícula por disciplina, atividades complementares, estágio, TCC e histórico com CR.' },
  { title: 'Cursos profissionalizantes', text: 'Cursos técnicos por módulo, aulas práticas com almoxarifado, contratos, mensalidades e certificados.' },
  { title: 'Cursos gratuitos e programas sociais', text: 'Editais com sorteio ou análise de perfil, frequência mínima, lanche e kits entregues e prestação de contas ao financiador.' },
  { title: 'Treinamento corporativo', text: 'Trilhas online, encontros ao vivo, empresas clientes com gestor próprio e certificados por curso.' },
];

/** Tipos de instituicao atendidos. */
export default function LandingAudiences() {
  return (
    <section id="para-quem" className="scroll-mt-20 bg-gray-50 py-20 dark:bg-gray-900/60">
      <div className="mx-auto max-w-6xl px-4">
        <h2 className="text-center text-3xl font-bold text-gray-900 dark:text-white">Feito para o seu tipo de instituição</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-gray-600 dark:text-gray-400">A plataforma usa os termos da sua realidade: série ou semestre, componente ou disciplina, módulo ou ciclo.</p>
        <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {AUDIENCES.map(({ title, text }) => (
            <article key={title} className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
              <h3 className="font-semibold text-indigo-700 dark:text-indigo-300">{title}</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{text}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
