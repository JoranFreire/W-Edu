import { enrollmentStatusLabels, enrollmentTransitions } from '@/lib/academic/labels';
import type { ProgramEnrollment, ProgramEnrollmentStatus } from '@/types/academicGroups';

/** Situacao atual e as mudancas permitidas a partir dela. */
export default function EnrollmentStatusSelect({ enrollment, onChange }: {
  enrollment: ProgramEnrollment;
  onChange: (status: ProgramEnrollmentStatus) => void;
}) {
  const options = enrollmentTransitions[enrollment.status];
  if (options.length === 0) {
    return <span className="text-sm text-gray-600 dark:text-gray-300">{enrollmentStatusLabels[enrollment.status]}</span>;
  }
  return (
    <select
      aria-label={`Situação da matrícula ${enrollment.registration_number}`}
      value={enrollment.status}
      onChange={(e) => onChange(e.target.value as ProgramEnrollmentStatus)}
      className="rounded-lg border border-gray-300 bg-white px-2 py-1 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
    >
      <option value={enrollment.status}>{enrollmentStatusLabels[enrollment.status]}</option>
      {options.map((status) => <option key={status} value={status}>{enrollmentStatusLabels[status]}</option>)}
    </select>
  );
}
