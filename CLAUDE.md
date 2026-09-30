# W-Edu — Convenções

Plataforma educacional SaaS multi-instituição: backend FastAPI + SQLAlchemy + PostgreSQL (`backend/`), frontend Next.js 16 + React 19 + Tailwind 4 (`frontend/`). Visão e roadmap: `ROADMAP.md`, `docs/MULTI_INSTITUTION.md`, `docs/PERMISSIONS.md`.

## Princípio obrigatório: responsabilidade única (SRP)

Vale para todo código tocado, novo ou antigo. Ao alterar um arquivo que mistura responsabilidades, divida-o.

**Backend**
- Router: só HTTP (parâmetros, dependências de permissão, status). Sem regra de negócio.
- Service: uma área de negócio por classe (ex.: `TenantAccessService`, `MembershipService`, `CampusService`, `InstitutionService`).
- Repository: só acesso a dados.
- Policy (`app/policies/`): regras de autorização que dependem dos dados (ex.: escopo de usuários).
- Áreas grandes viram pacote com um módulo por responsabilidade (ex.: `app/services/certificates/`, `app/services/notifications/`, `app/services/academic/`, `app/services/assessment/`, `app/services/secretariat/`, `app/routers/admin/`).
- Infraestrutura transversal em `app/core/` com um módulo por preocupação (ex.: `tenancy.py` filtra leitura; `tenant_integrity.py` valida gravação).

**Frontend**
- Página: compõe hooks e componentes; não faz `api.*` direto nem concentra várias telas.
- Dados: hooks em `src/lib/hooks/` (admin em `src/lib/hooks/admin/`) sobre `useApiQuery`. Nada de `useEffect(() => { load() })` com `setState` manual.
- Componentes: um propósito cada; reutilizáveis em `src/components/common/` (`Modal`, `TabNav`, `SectionHeader`, `Spinner`, `StatusBadge`, `FormActions`, `formStyles`).
- Utilitários puros em `src/lib/` (`dates.ts`, `files/saveBlob.ts`, `api/errors.ts`, `text/slugify.ts`).
- Nomenclatura acadêmica (série/semestre/módulo, disciplina/componente): `useTerminology()` (presets em `src/lib/institution/terminology.ts`); não fixe esses termos nas telas.
- Erros de API: `apiErrorMessage(error, fallback)`; nunca `catch (e: any)`.
- Estado de `localStorage`: `useStoredValue`; formulário que parte de dados carregados: componente filho com `key` e estado inicial por props.

## Multi-tenant

- Todo model de dados de instituição herda `TenantMixin`; o filtro por `institution_id` e o preenchimento no insert são automáticos (`app/core/tenancy.py`, `app/core/tenant_integrity.py`).
- Consulta global deliberada: `.execution_options(**UNSCOPED)`, com comentário justificando (suspende também o RLS durante a instrução).
- Instituição da requisição: header `X-Institution` > subdomínio (`TENANT_BASE_DOMAIN`) > claim `inst` do token.
- RLS no PostgreSQL (`app/core/tenant_rls.py`) é a segunda barreira; a aplicação nunca deve conectar como superusuário.
- Papel efetivo ainda é `users.role`; `institution_memberships.role` é mantido em sincronia.

## Verificações antes de commitar

Backend (`backend/`):
```bash
python scripts/check_permissions.py
python scripts/check_role_guards.py
python scripts/check_api_permissions.py
python scripts/check_tenant_isolation.py        # DATABASE_URL=postgresql://... para rodar no Postgres
python scripts/check_certificate_flow.py
python scripts/check_curriculum_flow.py
python scripts/check_academic_calendar_flow.py
python scripts/check_assessment_flow.py
python scripts/check_secretariat_flow.py
python scripts/check_rls.py                     # Postgres com superusuario em DATABASE_URL; cria role/banco proprios
alembic upgrade head && alembic check           # migration alinhada aos models
```

Frontend (`frontend/`):
```bash
npx tsc --noEmit
npm run lint      # ESLint flat config (next lint não existe no Next 16)
npm run build
npm run test:e2e  # Playwright; exige API com banco do scripts/seed_e2e.py (ver frontend/e2e/README.md)
```

Teste de carga: `backend/loadtest/README.md`.
