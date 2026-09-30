# Testes de navegador (Playwright)

Cobrem os fluxos principais do frontend contra a API real: multi-instituição, estrutura acadêmica (programas, disciplinas, matriz curricular, períodos letivos, calendário, matrículas e turmas), agenda, financeiro, trilhas, comunicação, relatórios, cursos, certificados, usuários e conta.

## Preparar

```bash
# Backend, em backend/ — banco dedicado aos testes
createdb wedu_e2e
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wedu_e2e
alembic upgrade head
python scripts/seed_e2e.py          # idempotente
NOTIFICATION_WORKER_ENABLED=false uvicorn main:app --port 8000

# Frontend, em frontend/
npm run build
npx playwright install chromium     # uma vez por máquina
```

## Rodar

```bash
npm run test:e2e                     # sobe `next start` se não houver servidor em :3000
npx playwright show-report           # relatório HTML (traces e screenshots de falhas)
```

Variáveis opcionais:

- `E2E_BASE_URL` (padrão `http://localhost:3000`);
- `E2E_API_URL` (padrão `http://localhost:8000`), usada para preparar dados pela API (`e2e/support/api.ts`);
- `PLAYWRIGHT_CHROMIUM_EXECUTABLE` (Chromium já instalado, em vez do baixado pelo Playwright);
- `E2E_TENANT_BASE_DOMAIN=localhost` ativa os testes de instituição por subdomínio (`e2e/subdomain.spec.ts`); a API precisa rodar com `TENANT_BASE_DOMAIN=localhost`.

Os testes criam registros com sufixo único, então o mesmo banco pode ser reutilizado entre execuções.
