import type { Course } from '@/types/course';

export const courseModalityLabels: Record<Course['modality'], string> = {
  online: 'Online',
  in_person: 'Presencial',
  hybrid: 'Híbrido',
};
