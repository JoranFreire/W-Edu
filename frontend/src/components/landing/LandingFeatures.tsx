import {
  AcademicCapIcon, ArchiveBoxIcon, BanknotesIcon, ChatBubbleLeftRightIcon, ClipboardDocumentCheckIcon,
  FolderOpenIcon, GiftIcon, KeyIcon, PencilSquareIcon,
} from '@heroicons/react/24/outline';

const FEATURES = [
  { icon: FolderOpenIcon, title: 'Secretaria acadêmica', text: 'Matrícula, rematrícula, transferências, aproveitamento de estudos, histórico escolar e declarações com validação pública.' },
  { icon: PencilSquareIcon, title: 'Diário de classe', text: 'Chamada, notas por etapa, recuperação e resultado final, com boletim para alunos e responsáveis.' },
  { icon: ClipboardDocumentCheckIcon, title: 'Matrícula por disciplina', text: 'Janelas de matrícula com créditos, pré-requisitos, choque de horário e lista de espera; integralização com estágio e TCC.' },
  { icon: BanknotesIcon, title: 'Financeiro educacional', text: 'Mensalidades, bolsas e descontos, multa e juros automáticos e contratos com aceite eletrônico.' },
  { icon: GiftIcon, title: 'Editais e programas sociais', text: 'Inscrição pública, sorteio auditável ou análise de perfil, vagas reservadas, benefícios entregues e prestação de contas.' },
  { icon: ChatBubbleLeftRightIcon, title: 'Comunicação com famílias', text: 'Agenda da turma, ocorrências e avisos que chegam ao aluno e ao responsável, com modelos por canal.' },
  { icon: AcademicCapIcon, title: 'Cursos e certificados', text: 'Cursos online, trilhas, encontros presenciais com chamada por QR code e certificados com código de validação.' },
  { icon: ArchiveBoxIcon, title: 'Almoxarifado', text: 'Requisições de material pelos professores, aprovação, retirada, devolução e relatórios de consumo.' },
  { icon: KeyIcon, title: 'Perfis de acesso', text: 'Permissões por função e papéis acumulados: a mesma pessoa pode ser aluna, professora e responsável.' },
];

/** Modulos da plataforma. */
export default function LandingFeatures() {
  return (
    <section id="recursos" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20">
      <h2 className="text-center text-3xl font-bold text-gray-900 dark:text-white">Tudo o que a rotina da instituição pede</h2>
      <p className="mx-auto mt-3 max-w-2xl text-center text-gray-600 dark:text-gray-400">Módulos integrados: o que a secretaria registra, o professor, o aluno e a família veem na hora.</p>
      <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, text }) => (
          <article key={title} className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <Icon className="h-8 w-8 text-indigo-600" />
            <h3 className="mt-4 font-semibold text-gray-900 dark:text-white">{title}</h3>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
