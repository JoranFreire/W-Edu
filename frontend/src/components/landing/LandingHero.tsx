const HIGHLIGHTS = ['Escolas, faculdades e cursos profissionalizantes', 'Sua marca e seu domínio', 'Uma conta, vários papéis'];

/** Chamada principal da pagina de contratacao. */
export default function LandingHero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-indigo-50 to-white dark:from-gray-900 dark:to-gray-950">
      <div className="mx-auto max-w-6xl px-4 py-20 text-center sm:py-28">
        <p className="mb-4 inline-block rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
          Plataforma de gestão educacional
        </p>
        <h1 className="mx-auto max-w-3xl text-4xl font-extrabold leading-tight text-gray-900 sm:text-5xl dark:text-white">
          Da matrícula ao certificado, toda a sua instituição em um só lugar
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-gray-600 dark:text-gray-300">
          Secretaria, diário de classe, financeiro, editais, programas sociais e comunicação com as famílias,
          para escolas, faculdades e cursos profissionalizantes, pagos ou gratuitos.
        </p>
        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <a href="#contato" className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-indigo-700">Quero uma demonstração</a>
          <a href="#planos" className="rounded-lg border border-gray-300 bg-white px-6 py-3 font-semibold text-gray-800 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100">Ver planos</a>
        </div>
        <ul className="mt-10 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-gray-600 dark:text-gray-400">
          {HIGHLIGHTS.map((item) => <li key={item} className="flex items-center gap-2"><span className="text-indigo-600">✓</span>{item}</li>)}
        </ul>
      </div>
    </section>
  );
}
