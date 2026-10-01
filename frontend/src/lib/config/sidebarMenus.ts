import type { ComponentType } from 'react';
import type { UserRole } from '@/types/auth';
import {
  HomeIcon, BookOpenIcon, ChartBarIcon, MicrophoneIcon, Cog6ToothIcon,
  UsersIcon, AcademicCapIcon, CalendarDaysIcon, ChatBubbleLeftRightIcon,
  BanknotesIcon, Squares2X2Icon, MapIcon, ShieldCheckIcon, DocumentTextIcon,
  BuildingLibraryIcon, GlobeAltIcon, BellIcon, RectangleStackIcon, PencilSquareIcon, FolderOpenIcon, DocumentChartBarIcon, UserGroupIcon,
} from '@heroicons/react/24/outline';

interface MenuItem { name: string; href: string; icon: ComponentType<{ className?: string }> }

export const studentMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Meus Cursos', href: '/courses', icon: BookOpenIcon },
  { name: 'Progresso', href: '/progress', icon: ChartBarIcon },
  { name: 'Boletim', href: '/report-card', icon: ChartBarIcon },
  { name: 'Agenda escolar', href: '/school-agenda', icon: CalendarDaysIcon },
  { name: 'Avisos', href: '/notifications', icon: BellIcon },
  { name: 'Histórico escolar', href: '/transcript', icon: DocumentChartBarIcon },
  { name: 'Certificados', href: '/certificates', icon: ShieldCheckIcon },
  { name: 'Sessões de Voz', href: '/sessions', icon: MicrophoneIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
];

export const adminMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Acadêmico', href: '/admin/academic', icon: RectangleStackIcon },
  { name: 'Diário de classe', href: '/teaching', icon: PencilSquareIcon },
  { name: 'Secretaria', href: '/admin/secretariat', icon: FolderOpenIcon },
  { name: 'Cursos', href: '/admin/courses', icon: AcademicCapIcon },
  { name: 'Trilhas', href: '/admin/learning-paths', icon: MapIcon },
  { name: 'Agenda', href: '/admin/schedule', icon: CalendarDaysIcon },
  { name: 'Certificados', href: '/admin/certificates', icon: ShieldCheckIcon },
  { name: 'Comunicação', href: '/admin/notifications', icon: ChatBubbleLeftRightIcon },
  { name: 'Financeiro', href: '/admin/finance', icon: BanknotesIcon },
  { name: 'Documentos', href: '/admin/documents', icon: DocumentTextIcon },
  { name: 'Relatórios', href: '/admin/analytics', icon: ChartBarIcon },
  { name: 'Usuários', href: '/admin/users', icon: UsersIcon },
  { name: 'Instituição', href: '/admin/institution', icon: BuildingLibraryIcon },
  { name: 'Catálogo', href: '/courses', icon: Squares2X2Icon },
  { name: 'Meus certificados', href: '/certificates', icon: ShieldCheckIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
];

export const superAdminMenu: MenuItem[] = [
  { name: 'Plataforma', href: '/platform/institutions', icon: GlobeAltIcon },
  ...adminMenu,
];

export const coordinatorMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Acadêmico', href: '/admin/academic', icon: RectangleStackIcon },
  { name: 'Diário de classe', href: '/teaching', icon: PencilSquareIcon },
  { name: 'Secretaria', href: '/admin/secretariat', icon: FolderOpenIcon },
  { name: 'Cursos', href: '/admin/courses', icon: AcademicCapIcon },
  { name: 'Trilhas', href: '/admin/learning-paths', icon: MapIcon },
  { name: 'Agenda', href: '/admin/schedule', icon: CalendarDaysIcon },
  { name: 'Certificados', href: '/admin/certificates', icon: ShieldCheckIcon },
  { name: 'Comunicação', href: '/admin/notifications', icon: ChatBubbleLeftRightIcon },
  { name: 'Usuários', href: '/admin/users', icon: UsersIcon },
  { name: 'Catálogo', href: '/courses', icon: Squares2X2Icon },
  { name: 'Meus certificados', href: '/certificates', icon: ShieldCheckIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
];

export const instructorMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Diário de classe', href: '/teaching', icon: PencilSquareIcon },
  ...studentMenu.filter((item) => item.href !== '/dashboard' && item.href !== '/school-agenda'),
];

export const secretaryMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Secretaria', href: '/admin/secretariat', icon: FolderOpenIcon },
  { name: 'Agenda das turmas', href: '/admin/secretariat/agenda', icon: CalendarDaysIcon },
  { name: 'Avisos', href: '/notifications', icon: BellIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
];

export const guardianMenu: MenuItem[] = [
  { name: 'Meus dependentes', href: '/guardian', icon: UserGroupIcon },
  { name: 'Avisos', href: '/notifications', icon: BellIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
];

export const companyManagerMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Financeiro', href: '/admin/finance', icon: BanknotesIcon },
  { name: 'Documentos', href: '/admin/documents', icon: DocumentTextIcon },
  { name: 'Relatórios', href: '/admin/analytics', icon: ChartBarIcon },
  { name: 'Usuários', href: '/admin/users', icon: UsersIcon },
  { name: 'Catálogo', href: '/courses', icon: Squares2X2Icon },
  { name: 'Meus certificados', href: '/certificates', icon: ShieldCheckIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
];

export function menuForRole(role: UserRole | undefined): MenuItem[] {
  if (role === 'super_admin') return superAdminMenu;
  if (role === 'admin' || role === 'institution_admin') return adminMenu;
  if (role === 'coordinator') return coordinatorMenu;
  if (role === 'instructor') return instructorMenu;
  if (role === 'secretary') return secretaryMenu;
  if (role === 'guardian') return guardianMenu;
  if (role === 'company_manager') return companyManagerMenu;
  return studentMenu;
}
