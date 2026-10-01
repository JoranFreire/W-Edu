import { formatMoney } from '@/lib/academic/guardianLabels';
import { schoolingLabels } from '@/lib/academic/admissionLabels';
import type { Schooling } from '@/types/admissions';
import type { FundingReport } from '@/types/socialPrograms';

const wageSources: Record<FundingReport['minimum_wage_source'], string> = {
  bcb: 'Banco Central',
  informed: 'valor informado',
  fallback: 'valor de reserva; Banco Central indisponível',
};

function Distribution({ title, values, labels }: { title: string; values: Record<string, number>; labels?: Record<string, string> }) {
  return (
    <div>
      <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">{title}</h3>
      <ul className="text-sm text-gray-700 dark:text-gray-300">
        {Object.entries(values).map(([key, count]) => <li key={key}>{labels?.[key] ?? key}: {count}</li>)}
      </ul>
    </div>
  );
}

/** Indicadores por turma, perfil do publico e beneficios com custo. */
export default function FundingReportView({ report }: { report: FundingReport }) {
  return (
    <div className="space-y-6">
      <table className="min-w-full text-sm">
        <thead className="text-left text-xs uppercase text-gray-500 dark:text-gray-400">
          <tr><th className="py-2">Turma</th><th>Inscritos</th><th>Matriculados</th><th>Ativos</th><th>Concluintes</th><th>Desligados</th><th>Desistentes</th><th>Evasão</th></tr>
        </thead>
        <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
          {[...report.offerings, report.totals].map((row) => (
            <tr key={row.name + (row.class_offering_id ?? 'total')} className={`text-gray-800 dark:text-gray-200 ${row.class_offering_id === null ? 'font-semibold' : ''}`}>
              <td className="py-2">{row.name}</td><td>{row.applications}</td><td>{row.enrolled}</td><td>{row.active}</td>
              <td>{row.completed}</td><td>{row.dismissed}</td><td>{row.dropped}</td><td>{row.evasion_rate.toLocaleString('pt-BR')}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Distribution title="Idade" values={report.profile.age} />
        <Distribution title="Renda por pessoa" values={report.profile.income_per_capita} />
        <Distribution title="Escolaridade" values={report.profile.schooling} labels={schoolingLabels as Record<Schooling, string>} />
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        Perfil de {report.profile.respondents} matriculado(s) pelo edital; {report.profile.reserved_seats} em vaga reservada.
        Renda em salários mínimos de {formatMoney(report.minimum_wage_cents)} ({wageSources[report.minimum_wage_source]}).
      </p>
      <div>
        <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">Benefícios entregues</h3>
        {report.benefits.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma entrega.</p> : (
          <ul className="text-sm text-gray-700 dark:text-gray-300">
            {report.benefits.map((item) => <li key={item.item_name}>{item.item_name}: {item.quantity} {item.unit} · {formatMoney(item.cost_cents)}</li>)}
          </ul>
        )}
        <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Custo dos benefícios: {formatMoney(report.benefits_cost_cents)} · estoque recebido com este financiador: {formatMoney(report.stock_received_cents)}
          {report.budget_balance_cents !== null ? ` · saldo do financiamento: ${formatMoney(report.budget_balance_cents)}` : ''}
        </p>
      </div>
    </div>
  );
}
