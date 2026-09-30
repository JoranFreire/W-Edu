# W-Edu — Convenções

Plataforma educacional SaaS multi-instituição: backend FastAPI + SQLAlchemy + PostgreSQL (`backend/`), frontend Next.js 16 + React 19 + Tailwind 4 (`frontend/`). Visão e roadmap: `ROADMAP.md`, `docs/MULTI_INSTITUTION.md`, `docs/PERMISSIONS.md`.

## Princípio obrigatório: responsabilidade única (SRP)

Vale para todo código tocado, novo ou antigo. Ao alterar um arquivo que mistura responsabilidades, divida-o.

**Backend**
- Router: só HTTP (parâmetros, dependências de permissão, status). Sem regra de negócio.
- Service: uma área de negócio por classe (ex.: `TenantAccessService`, `MembershipService`, `CampusService`, `InstitutionService`).
- Repository: só acesso a dados.
- Infraestrutura transversal em `app/core/` com um módulo por preocupação (ex.: `tenancy.py` filtra leitura; `tenant_integrity.py` valida gravação).

**Frontend**
- Página: compõe hooks e componentes; não faz `api.*` direto nem concentra várias telas.
- Dados: hooks em `src/lib/hooks/` (admin em `src/lib/hooks/admin/`) sobre `useApiQuery`. Nada de `useEffect(() => { load() })` com `setState` manual.
- Componentes: um propósito cada; reutilizáveis em `src/components/common/` (`Modal`, `TabNav`, `SectionHeader`, `Spinner`, `StatusBadge`).
- Utilitários puros em `src/lib/` (`dates.ts`, `files/saveBlob.ts`, `api/errors.ts`, `text/slugify.ts`).
- Erros de API: `apiErrorMessage(error, fallback)`; nunca `catch (e: any)`.
- Estado de `localStorage`: `useStoredValue`; formulário que parte de dados carregados: componente filho com `key` e estado inicial por props.

## Multi-tenant

- Todo model de dados de instituição herda `TenantMixin`; o filtro por `institution_id` e o preenchimento no insert são automáticos (`app/core/tenancy.py`, `app/core/tenant_integrity.py`).
- Consulta global deliberada: `.execution_options(**UNSCOPED)`, com comentário justificando.
- Papel efetivo ainda é `users.role`; `institution_memberships.role` é mantido em sincronia.

## Verificações antes de commitar

Backend (`backend/`):
```bash
python scripts/check_permissions.py
python scripts/check_role_guards.py
python scripts/check_api_permissions.py
python scripts/check_tenant_isolation.py        # DATABASE_URL=postgresql://... para rodar no Postgres
alembic upgrade head && alembic check           # migration alinhada aos models
```

Frontend (`frontend/`):
```bash
npx tsc --noEmit
npm run lint      # ESLint flat config (next lint não existe no Next 16)
npm run build
```

Teste de carga: `backend/loadtest/README.md`.
