import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Student, AuthTokens, LoginCredentials } from '@/types/auth';
import type { Institution, InstitutionSummary, Membership } from '@/types/institution';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { institutionLoginUrl } from '@/lib/institution/subdomain';
import { apiErrorMessage } from '@/lib/api/errors';

interface AuthState {
  student: Student | null;
  tokens: AuthTokens | null;
  institution: Institution | InstitutionSummary | null;
  memberships: Membership[];
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  _hasHydrated: boolean;

  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  fetchStudent: () => Promise<void>;
  fetchInstitution: () => Promise<void>;
  switchInstitution: (slug: string) => Promise<void>;
  clearError: () => void;
  setHasHydrated: (v: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      student: null,
      tokens: null,
      institution: null,
      memberships: [],
      isAuthenticated: false,
      isLoading: false,
      error: null,
      _hasHydrated: false,

      login: async (credentials) => {
        try {
          set({ isLoading: true, error: null });

          const { data: tokens } = await api.post<AuthTokens>(endpoints.auth.login, credentials);
          localStorage.setItem('access_token', tokens.access_token);

          const { data: student } = await api.get<Student>(endpoints.auth.me);

          set({ student, tokens, institution: tokens.institution, isAuthenticated: true, isLoading: false, error: null });
          get().fetchInstitution();
        } catch (error) {
          const msg = apiErrorMessage(error, 'Falha ao fazer login. Verifique suas credenciais.');
          set({ student: null, tokens: null, institution: null, memberships: [], isAuthenticated: false, isLoading: false, error: msg });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        set({ student: null, tokens: null, institution: null, memberships: [], isAuthenticated: false, error: null });
        if (typeof window !== 'undefined') window.location.href = '/login';
      },

      fetchStudent: async () => {
        try {
          set({ isLoading: true });
          const { data: student } = await api.get<Student>(endpoints.auth.me);
          set({ student, isAuthenticated: true, isLoading: false });
        } catch {
          set({ student: null, isAuthenticated: false, isLoading: false });
          get().logout();
        }
      },

      fetchInstitution: async () => {
        try {
          const [{ data: institution }, { data: memberships }] = await Promise.all([
            api.get<Institution>(endpoints.institutions.current),
            api.get<Membership[]>(endpoints.auth.institutions),
          ]);
          set({ institution, memberships });
        } catch {
          // Mantem a instituicao em cache; erros de sessao ja sao tratados pelo interceptor.
        }
      },

      switchInstitution: async (slug) => {
        // Com subdominios, cada instituicao tem sua origem (e sessao): vai para o login dela.
        const loginUrl = institutionLoginUrl(slug);
        if (loginUrl) {
          window.location.href = loginUrl;
          return;
        }
        const { data: tokens } = await api.post<AuthTokens>(endpoints.auth.switchInstitution, { institution: slug });
        localStorage.setItem('access_token', tokens.access_token);
        set({ tokens, institution: tokens.institution });
        // Recarrega para descartar dados da instituicao anterior mantidos nas paginas.
        if (typeof window !== 'undefined') window.location.href = '/dashboard';
      },

      clearError: () => set({ error: null }),
      setHasHydrated: (v) => set({ _hasHydrated: v }),
    }),
    {
      name: 'wedu-auth',
      partialize: (s) => ({
        student: s.student,
        tokens: s.tokens,
        institution: s.institution,
        memberships: s.memberships,
        isAuthenticated: s.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => state?.setHasHydrated(true),
    }
  )
);
