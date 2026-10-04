# W-Edu — Convenções

Plataforma educacional SaaS multi-instituição: backend FastAPI + SQLAlchemy + PostgreSQL (`backend/`), frontend Next.js 16 + React 19 + Tailwind 4 (`frontend/`), app Flutter para alunos e responsáveis (`frontend-mobile/`). Visão e roadmap: `ROADMAP.md`, `docs/MULTI_INSTITUTION.md`, `docs/PERMISSIONS.md`.

## Princípio obrigatório: responsabilidade única (SRP)

Vale para todo código tocado, novo ou antigo. Ao alterar um arquivo que mistura responsabilidades, divida-o.

**Backend**
- Router: só HTTP (parâmetros, dependências de permissão, status). Sem regra de negócio.
- Service: uma área de negócio por classe (ex.: `TenantAccessService`, `MembershipService`, `CampusService`, `InstitutionService`).
- Repository: só acesso a dados.
- Policy (`app/policies/`): regras de autorização que dependem dos dados (ex.: escopo de usuários).
- Autorização por permissão (RBAC): guards em `app/dependencies.py` exigem uma chave do catálogo (`app/services/access/catalog.py`); o papel do usuário concede um conjunto padrão e perfis de acesso da instituição somam permissões. Recurso novo ganha permissão no catálogo, não um novo teste de papel.
- Áreas grandes viram pacote com um módulo por responsabilidade (ex.: `app/services/certificates/`, `app/services/notifications/`, `app/services/academic/`, `app/services/assessment/`, `app/services/secretariat/`, `app/services/registration/`, `app/services/completion/`, `app/services/tuition/`, `app/services/contracts/`, `app/services/saas/`, `app/services/admissions/`, `app/services/retention/`, `app/services/social/`, `app/services/access/`, `app/services/warehouse/`, `app/routers/admin/`).
- Infraestrutura transversal em `app/core/` com um módulo por preocupação (ex.: `tenancy.py` filtra leitura; `tenant_integrity.py` valida gravação).
- Cache dos apps (versão por área): `data_versions` guarda, por instituição, a versão de cada área (`notifications`, `agenda`, `report_card`, `dependents`, `benefits`, `materials`) e `GET /sync/versions` a devolve. A versão sobe sozinha a cada gravação nas tabelas registradas em `app/services/sync/areas.py` (`track(model, area)`, listener em `app/core/change_tracking.py`). Tela nova do app com cache: registre as tabelas que a alimentam na área (ou crie uma).
- Ids: UUID versão 7 gerado pela aplicação (`app/core/ids.py`: `new_id`, crescente no tempo; `parse_id` para texto). Colunas de id e chaves estrangeiras são `Mapped[UUID]` (tipo `IdType`, que aceita o id em texto). Nunca trate id como número: nada de `int(id)`, sentinela `[-1]` em `IN` (lista vazia já funciona) nem aritmética para ordenar.

**Frontend**
- Página: compõe hooks e componentes; não faz `api.*` direto nem concentra várias telas.
- Dados: hooks em `src/lib/hooks/` (admin em `src/lib/hooks/admin/`) sobre `useApiQuery`. Nada de `useEffect(() => { load() })` com `setState` manual.
- Componentes: um propósito cada; reutilizáveis em `src/components/common/` (`Modal`, `TabNav`, `SectionHeader`, `Spinner`, `StatusBadge`, `FormActions`, `formStyles`).
- Utilitários puros em `src/lib/` (`dates.ts`, `files/saveBlob.ts`, `api/errors.ts`, `text/slugify.ts`).
- Rotas da API em `src/lib/api/endpoints/`, um módulo por área (`academic.ts`, `secretariat.ts`, `finance.ts`…); `index.ts` reúne tudo em `endpoints`. Rota nova entra no módulo da área, não num arquivo único.
- Páginas públicas renderizadas no servidor (`/` e `/instituicao/[slug]`) buscam dados por `src/lib/publicSite/server.ts` (chama a API em `API_INTERNAL_URL`). Na raiz, o domínio da plataforma mostra a contratação (`components/landing/`) e o domínio do cliente (subdomínio ou domínio próprio) mostra a instituição (`components/institutionHome/`).
- Nomenclatura acadêmica (série/semestre/módulo, disciplina/componente): `useTerminology()` (presets em `src/lib/institution/terminology.ts`); não fixe esses termos nas telas.
- Erros de API: `apiErrorMessage(error, fallback)`; nunca `catch (e: any)`.
- Ids são `string` (UUID): nada de `Number(id)` em parâmetros de rota ou selects; mapas por id são `Record<string, …>`.
- Estado de `localStorage`: `useStoredValue`; formulário que parte de dados carregados: componente filho com `key` e estado inicial por props.

**Mobile** (`frontend-mobile/`)
- Riverpod 3 + go_router + dio + flutter_secure_storage, por feature: `features/<x>/{data/, <x>_providers.dart, screens/, widgets/}`; dependências `features` → `shared` → `core`.
- Repositório só faz HTTP → model; estado remoto em provider com `AsyncValue` (carregando, erro e vazio via `ListaRemota`).
- Abas por papel em `router/rotas.dart` (`Aba.visivelPara`); o redirect bloqueia rota de aba não permitida.
- Persona (reconhecimento facial): o app fala direto com a API dele (`personaDioProvider`, `PERSONA_BASE_URL`); as fotos nunca passam pelo backend do W-Edu. Login facial em `features/login_facial/` (conta lembrada no aparelho, 1:1); autorizações por finalidade (termo com versão e hash) e cadastro do rosto em `features/biometria/`; captura com prova de vida em `shared/rosto/`.
- Cache versionado (como o catálogo do WS-ServicePortal): telas pessoais usam `observarArea` (`core/cache/`), que entrega o JSON salvo em disco, confere `sync/versions` e só baixa a área que mudou; offline fica com o salvo. Repositório devolve o JSON bruto e o model o lê (`Model.lista`). Puxar para atualizar: `ref.atualizarDaApi(provider, chave)`. Sair apaga o cache.

## Multi-tenant

- Todo model de dados de instituição herda `TenantMixin`; o filtro por `institution_id` e o preenchimento no insert são automáticos (`app/core/tenancy.py`, `app/core/tenant_integrity.py`).
- Consulta global deliberada: `.execution_options(**UNSCOPED)`, com comentário justificando (suspende também o RLS durante a instrução).
- Instituição da requisição: header `X-Institution` > subdomínio (`TENANT_BASE_DOMAIN`) > domínio próprio (`institutions.custom_domain`) > claim `inst` do token (`request_institution_ref` em `app/dependencies.py`).
- RLS no PostgreSQL (`app/core/tenant_rls.py`) é a segunda barreira; a aplicação nunca deve conectar como superusuário.
- Papéis por instituição: a pessoa pode acumular vários no mesmo vínculo (aluno e professor, por exemplo) e ter papéis diferentes em cada instituição (`institution_member_roles`; `users.role` e `institution_memberships.role` guardam só o principal). Teste papel com `has_role`/`has_any_role` (`app/policies/roles.py`), que vale para quem faz a requisição e para outras pessoas; nunca `user.role == ...`, exceto `is_super_admin` (papel da plataforma). No frontend: `useCurrentRoles()` para quem está logado e `rolesOf(user)` para os demais.

## Verificações antes de commitar

Backend (`backend/`):
```bash
python scripts/check_permissions.py
python scripts/check_role_guards.py
python scripts/check_api_permissions.py
python scripts/check_tenant_isolation.py        # DATABASE_URL=postgresql://... para rodar no Postgres (banco de teste: os scripts apagam as tabelas e recusam nomes sem check/test/e2e/tmp/scratch)
python scripts/check_certificate_flow.py
python scripts/check_curriculum_flow.py
python scripts/check_academic_calendar_flow.py
python scripts/check_assessment_flow.py
python scripts/check_secretariat_flow.py
python scripts/check_guardians_flow.py
python scripts/check_school_life_flow.py
python scripts/check_registration_flow.py
python scripts/check_completion_flow.py
python scripts/check_tuition_flow.py
python scripts/check_contracts_flow.py
python scripts/check_saas_flow.py
python scripts/check_admissions_flow.py
python scripts/check_social_flow.py
python scripts/check_access_flow.py
python scripts/check_warehouse_flow.py
python scripts/check_notifications_flow.py
python scripts/check_user_dossier_flow.py
python scripts/check_multi_roles_flow.py
python scripts/check_public_site_flow.py
python scripts/check_sync_flow.py
python scripts/check_benefit_vouchers_flow.py
python scripts/check_facial_identity_flow.py
python scripts/check_persona_integration_flow.py
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

Mobile (`frontend-mobile/`):
```bash
flutter analyze
flutter test
```

Teste de carga: `backend/loadtest/README.md`.
