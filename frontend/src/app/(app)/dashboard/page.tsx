'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import DashboardStats from '@/components/dashboard/DashboardStats';
import EnrolledCoursesGrid from '@/components/dashboard/EnrolledCoursesGrid';
import RecentSessionsList from '@/components/dashboard/RecentSessionsList';
import Spinner from '@/components/common/Spinner';
import { useStudentDashboard } from '@/lib/hooks/useStudentDashboard';
import { useAuthStore } from '@/store/authStore';
import { useCurrentRoles } from '@/lib/hooks/useCurrentRoles';

export default function DashboardPage() {
  const router = useRouter();
  const { student } = useAuthStore();
  const { roles } = useCurrentRoles();
  // Quem e so responsavel vai ao portal dos dependentes; quem tambem estuda ou trabalha aqui fica no painel.
  const isGuardian = roles.length > 0 && roles.every((role) => role === 'guardian');
  const { data, enrolledCourses, loading } = useStudentDashboard(isGuardian ? undefined : student?.id);

  useEffect(() => {
    if (isGuardian) router.replace('/guardian');
  }, [isGuardian, router]);

  if (isGuardian || loading || !data) return <Spinner />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Olá, {student?.name.split(' ')[0]}!</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Aqui está um resumo do seu aprendizado.</p>
      </div>
      <DashboardStats enrollments={data.enrollments} progress={data.progress} sessions={data.sessions} />
      <EnrolledCoursesGrid courses={enrolledCourses} />
      <RecentSessionsList sessions={data.sessions} />
    </div>
  );
}
