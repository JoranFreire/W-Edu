/** Autenticacao, instituicoes, plataforma, perfis de acesso e paginas publicas. */
export const identityEndpoints = {
  auth: {
    login: '/auth/login',
    me: '/users/me',
    institutions: '/auth/institutions',
    switchInstitution: '/auth/switch-institution',
  },
  institutions: {
    public: '/institutions/public',
    current: '/institutions/current',
    campuses: '/institutions/campuses',
    campus: (id: string) => `/institutions/campuses/${id}`,
  },
  platform: {
    institutions: '/platform/institutions',
    institution: (id: string) => `/platform/institutions/${id}`,
    institutionDomain: (id: string) => `/platform/institutions/${id}/domain`,
    leads: '/platform/leads',
    lead: (id: string) => `/platform/leads/${id}`,
  },
  access: {
    me: '/access/me',
    permissions: '/access/permissions',
    builtIn: '/access/built-in',
    members: '/access/members',
    roles: '/access/roles',
    role: (id: string) => `/access/roles/${id}`,
    roleMembers: (id: string) => `/access/roles/${id}/members`,
    roleMember: (id: string, userId: string) => `/access/roles/${id}/members/${userId}`,
  },
  publicSite: {
    leads: '/public/leads',
  },
};
