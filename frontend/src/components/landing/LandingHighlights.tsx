const HIGHLIGHTS = [
  { title: 'Sua marca, seu endereço', text: 'Cada instituição tem cores, logo e página pública própria, no subdomínio da plataforma ou no seu domínio (escola.com.br), com as inscrições abertas.' },
  { title: 'Dados separados por instituição', text: 'Cada instituição só enxerga os próprios dados, com uma segunda barreira de isolamento direto no banco de dados.' },
  { title: 'Uma pessoa, vários papéis', text: 'A professora que faz pós, o funcionário que é pai de aluno: uma conta só, com as áreas de cada papel no mesmo menu.' },
];

/** Diferenciais da plataforma. */
export default function LandingHighlights() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-20">
      <div className="grid gap-8 md:grid-cols-3">
        {HIGHLIGHTS.map(({ title, text }) => (
          <div key={title}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            <p className="mt-2 text-gray-600 dark:text-gray-400">{text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
