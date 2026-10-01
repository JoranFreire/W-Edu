import Link from 'next/link';

const NAV = [
  { href: '#recursos', label: 'Recursos' },
  { href: '#para-quem', label: 'Para quem' },
  { href: '#planos', label: 'Planos' },
  { href: '#contato', label: 'Contato' },
];

/** Topo da pagina de contratacao: marca, atalhos para as secoes e acesso ao sistema. */
export default function LandingHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-gray-200/70 bg-white/85 backdrop-blur dark:border-gray-800 dark:bg-gray-950/85">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-bold text-gray-900 dark:text-white">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">W</span>
          W-Edu
        </Link>
        <nav aria-label="Seções" className="hidden gap-6 text-sm text-gray-600 md:flex dark:text-gray-300">
          {NAV.map((item) => <a key={item.href} href={item.href} className="hover:text-indigo-600">{item.label}</a>)}
        </nav>
        <div className="flex items-center gap-2">
          <Link href="/login" className="rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800">Entrar</Link>
          <a href="#contato" className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">Fale com a gente</a>
        </div>
      </div>
    </header>
  );
}
