import type { ComponentType } from 'react';
import type { UserRole } from '@/types/auth';
import {
  HomeIcon, BookOpenIcon, ChartBarIcon, MicrophoneIcon, Cog6ToothIcon,
  UsersIcon, AcademicCapIcon, CalendarDaysIcon, ChatBubbleLeftRightIcon,
  BanknotesIcon, Squares2X2Icon, MapIcon, ShieldCheckIcon, DocumentTextIcon,
  BuildingLibraryIcon, GlobeAltIcon, BellIcon, CreditCardIcon, RectangleStackIcon, PencilSquareIcon, ClipboardDocumentCheckIcon, ChartPieIcon, BriefcaseIcon, ArchiveBoxIcon, BuildingStorefrontIcon, KeyIcon, DocumentDuplicateIcon, InboxArrowDownIcon, MegaphoneIcon, GiftIcon, FolderOpenIcon, DocumentChartBarIcon, UserGroupIcon,
} from '@heroicons/react/24/outline';

interface MenuItem { name: string; href: string; icon: ComponentType<{ className?: string }> }

export const studentMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Meus Cursos', href: '/courses', icon: BookOpenIcon },
  { name: 'Progresso', href: '/progress', icon: ChartBarIcon },
  { name: 'Boletim', href: '/report-card', icon: ChartBarIcon },
  { name: 'Matrícula em disciplinas', href: '/registration', icon: ClipboardDocumentCheckIcon },
  { name: 'Agenda escolar', href: '/school-agenda', icon: CalendarDaysIcon },
  { name: 'Avisos', href: '/notifications', icon: BellIcon },
  { name: 'Histórico escolar', href: '/transcript', icon: DocumentChartBarIcon },
  { name: 'Integralização', href: '/completion', icon: ChartPieIcon },
  { name: 'Mensalidades', href: '/payments', icon: BanknotesIcon },
  { name: 'Contratos', href: '/contracts', icon: DocumentDuplicateIcon },
  { name: 'Inscrições', href: '/admissions', icon: MegaphoneIcon },
  { name: 'Benefícios', href: '/benefits', icon: GiftIcon },
  { name: 'Certificados', href: '/certificates', icon: ShieldCheckIcon },
  { name: 'Sessões de Voz', href: '/sessions', icon: MicrophoneIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
];

export const adminMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Acadêmico', href: '/admin/academic', icon: RectangleStackIcon },
  { name: 'Diário de classe', href: '/teaching', icon: PencilSquareIcon },
  { name: 'Orientações', href: '/teaching/advising', icon: BriefcaseIcon },
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
  { name: 'Planos SaaS', href: '/platform/plans', icon: CreditCardIcon },
  { name: 'Interessados', href: '/platform/leads', icon: InboxArrowDownIcon },
  ...adminMenu,
];

export const coordinatorMenu: MenuItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Acadêmico', href: '/admin/academic', icon: RectangleStackIcon },
  { name: 'Diário de classe', href: '/teaching', icon: PencilSquareIcon },
  { name: 'Orientações', href: '/teaching/advising', icon: BriefcaseIcon },
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
  { name: 'Orientações', href: '/teaching/advising', icon: BriefcaseIcon },
  ...studentMenu.filter((item) => !['/dashboard', '/school-agenda', '/registration', '/completion', '/payments', '/contracts', '/admissions', '/benefits'].includes(item.href)),
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
  { name: 'Mensalidades', href: '/payments', icon: BanknotesIcon },
  { name: 'Contratos', href: '/contracts', icon: DocumentDuplicateIcon },
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

/** Itens liberados por permissao (perfis de acesso); entram no menu de quem nao os tem pelo papel. */
const permissionMenu: { permissions: string[]; item: MenuItem }[] = [
  { permissions: ['teaching.access'], item: { name: 'Diário de classe', href: '/teaching', icon: PencilSquareIcon } },
  { permissions: ['secretariat.access'], item: { name: 'Secretaria', href: '/admin/secretariat', icon: FolderOpenIcon } },
  { permissions: ['academic.manage'], item: { name: 'Acadêmico', href: '/admin/academic', icon: RectangleStackIcon } },
  { permissions: ['warehouse.request'], item: { name: 'Requisições de material', href: '/warehouse', icon: ArchiveBoxIcon } },
  { permissions: ['warehouse.manage', 'warehouse.reports'], item: { name: 'Almoxarifado', href: '/admin/warehouse', icon: BuildingStorefrontIcon } },
  { permissions: ['access.manage'], item: { name: 'Perfis de acesso', href: '/admin/access', icon: KeyIcon } },
];

/** Menu de quem acumula papeis: o do principal e, em seguida, o que so os outros papeis trazem. */
function mergedMenu(roles: UserRole[]): MenuItem[] {
  const merged: MenuItem[] = [];
  for (const role of roles.length ? roles : [undefined]) {
    for (const item of menuForRole(role)) {
      if (!merged.some((entry) => entry.href === item.href)) merged.push(item);
    }
  }
  return merged;
}

export function menuForUser(roles: UserRole[], permissions: string[]): MenuItem[] {
  const base = mergedMenu(roles);
  const extra = permissionMenu
    .filter(({ permissions: required, item }) => required.some((key) => permissions.includes(key)) && !base.some((entry) => entry.href === item.href))
    .map(({ item }) => item);
  // Mantem Configuracoes por ultimo.
  const settings = base.filter((entry) => entry.href === '/settings');
  return [...base.filter((entry) => entry.href !== '/settings'), ...extra, ...settings];
}

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
