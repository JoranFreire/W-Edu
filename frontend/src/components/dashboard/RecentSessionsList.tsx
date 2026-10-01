import Link from 'next/link';
import { MicrophoneIcon } from '@heroicons/react/24/outline';
import type { Session } from '@/types/course';

export default function RecentSessionsList({ sessions }: { sessions: Session[] }) {
  if (sessions.length === 0) return null;
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Últimas Sessões de Voz</h2>
        <Link href="/sessions" className="text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 font-medium">Ver todas</Link>
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700">
        {sessions.slice(0, 3).map((s) => (
          <div key={s.id} className="flex items-center justify-between px-5 py-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <MicrophoneIcon className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Aula #{s.lesson_id}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(s.started_at).toLocaleDateString('pt-BR')}</p>
              </div>
            </div>
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${s.ended_at ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'}`}>
              {s.ended_at ? 'Concluída' : 'Em andamento'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
