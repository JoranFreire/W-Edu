import { BookOpenIcon, ChartBarIcon, CheckCircleIcon, MicrophoneIcon } from '@heroicons/react/24/outline';
import type { Enrollment, Progress, Session } from '@/types/course';

export default function DashboardStats({ enrollments, progress, sessions }: { enrollments: Enrollment[]; progress: Progress[]; sessions: Session[] }) {
  const stats = [
    { label: 'Cursos Matriculados', value: enrollments.length, icon: BookOpenIcon, color: 'text-indigo-600', bg: 'bg-indigo-50 dark:bg-indigo-900/20' },
    { label: 'Aulas Concluídas', value: progress.filter((p) => p.status === 'done').length, icon: CheckCircleIcon, color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-900/20' },
    { label: 'Sessões de Voz', value: sessions.length, icon: MicrophoneIcon, color: 'text-purple-600', bg: 'bg-purple-50 dark:bg-purple-900/20' },
    { label: 'Em Progresso', value: progress.filter((p) => p.status === 'in_progress').length, icon: ChartBarIcon, color: 'text-yellow-600', bg: 'bg-yellow-50 dark:bg-yellow-900/20' },
  ];
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <div className="flex items-center space-x-4">
            <div className={`w-12 h-12 ${stat.bg} rounded-lg flex items-center justify-center`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
