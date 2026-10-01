import Link from 'next/link';

/** Rodape da pagina de contratacao. */
export default function LandingFooter() {
  return (
    <footer className="border-t border-gray-200 py-10 dark:border-gray-800">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 text-sm text-gray-500 sm:flex-row dark:text-gray-400">
        <p>© {new Date().getFullYear()} W-Edu · Plataforma de gestão educacional</p>
        <nav aria-label="Rodapé" className="flex gap-5">
          <Link href="/validate-certificate" className="hover:text-indigo-600">Validar certificado</Link>
          <Link href="/login" className="hover:text-indigo-600">Entrar</Link>
        </nav>
      </div>
    </footer>
  );
}
