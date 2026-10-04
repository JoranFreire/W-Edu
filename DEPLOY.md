# W-Edu — Deploy

## Ambiente local com Docker

```bash
docker compose up --build -d                  # Postgres (porta 5433), API (8000) e frontend (3000)
docker compose --profile demo run --rm seed   # contas e cursos de demonstracao (opcional)
```

Acesse http://localhost:3000. Contas de demonstracao (senha `e2e-senha-123`): `admin@alfa.example.com`
(admin da Escola Alfa e da Faculdade Beta), `instrutor@alfa.example.com`, `aluno@alfa.example.com` e
`root@e2e.example.com` (super admin). A API conecta com o papel `wedu`, sem superusuario, entao o RLS vale.
`docker compose down -v` apaga banco e arquivos.

## Pré-requisitos
- Ubuntu 22.04+
- Git
- Acesso root (sudo)

## Passo a passo

### 1. Clonar o repositório
```bash
git clone <URL_DO_REPO> w-edu
cd w-edu
```

### 2. Rodar o setup
```bash
sudo bash deploy/setup.sh
```

O script instala e configura automaticamente:
- Python 3 + venv + dependências
- Node.js 20 + build do frontend
- PostgreSQL + banco `wedu`
- Serviços systemd (`wedu-backend`, `wedu-frontend`)
- Nginx como reverse proxy na porta 80

### 3. Criar o primeiro admin
```bash
bash deploy/create-admin.sh "Seu Nome" "seu@email.com" "suasenha"
```

### 4. Acessar
```
http://SEU_IP
```

---

## Gerenciar os serviços
```bash
sudo systemctl status wedu-backend
sudo systemctl status wedu-frontend

sudo systemctl restart wedu-backend
sudo systemctl restart wedu-frontend

# Logs
journalctl -u wedu-backend -f
journalctl -u wedu-frontend -f
```

## Variáveis de ambiente
Edite `/var/www/W-Edu/backend/.env` antes de subir os serviços.  
Troque obrigatoriamente o `SECRET_KEY` em produção.

Para envio de notificações via W-Omni/WhatsApp, configure:

```env
WOMNI_URL=https://seu-womni
WOMNI_API_TOKEN=token-opcional
NOTIFICATION_DISPATCH_TIMEOUT_SECONDS=10
NOTIFICATION_WORKER_ENABLED=true
NOTIFICATION_WORKER_INTERVAL_SECONDS=60
NOTIFICATION_WORKER_BATCH_SIZE=100
```

O W-Edu envia eventos WhatsApp para `POST {WOMNI_URL}/messages`.

Para envio de notificações por email, configure SMTP:

```env
SMTP_HOST=smtp.exemplo.com
SMTP_PORT=587
SMTP_USERNAME=usuario
SMTP_PASSWORD=senha
SMTP_FROM_EMAIL=noreply@exemplo.com
SMTP_USE_TLS=true
```

### Login facial (Persona)

O app pode entrar com o rosto: o Persona confere a pessoa e assina um assertion curto (Ed25519), que a API troca pelo token. Configure a chave pública do Persona (32 bytes em base64url); vazia, `POST /auth/facial-login` fica desativado:

```env
PERSONA_ASSERTION_PUBLIC_KEY=
```

A maioridade (data de nascimento no cadastro do usuário) decide o uso do reconhecimento facial na presença; sem a data, a pessoa não é tida como adulta.

A mesma chave confere os **avisos de passagem na catraca**: o Persona envia `POST /integrations/persona/gate-events` (mensagem assinada com `typ=gate_event`); o W-Edu registra a passagem uma vez só e avisa o aluno e os responsáveis na caixa de avisos. Os horários dos avisos saem no fuso `DISPLAY_TIMEZONE` (padrão `America/Sao_Paulo`).

Em cada instituição que usa o Persona, crie uma **conta de serviço** de coordenação e configure o e-mail e a senha dela no Persona. Ela devolve a chamada facial (`POST /schedule/meetings/{id}/attendance`) e lê os **fins de vínculo** (`GET /integrations/persona/membership-events?since=<último horário visto>`), para o Persona tirar da catraca quem saiu da instituição ou teve a conta desativada.

### Multi-instituição

Instituição por subdomínio (ex.: `escola.wedu.com.br`): configure DNS curinga `*.wedu.com.br`, inclua `*.wedu.com.br` no `server_name` do nginx (e no certificado TLS) e defina:

```env
# backend/.env
TENANT_BASE_DOMAIN=wedu.com.br
# frontend (build): trocar de instituição navega para o subdomínio dela
NEXT_PUBLIC_TENANT_BASE_DOMAIN=wedu.com.br
```

#### Domínio próprio do cliente

Uma instituição pode usar o próprio domínio (ex.: `escola.com.br`): na raiz ele mostra a página pública dela (cursos, inscrições abertas, contatos) e o acesso ao sistema, enquanto o domínio da plataforma mostra a página de contratação.

1. O super admin cadastra o domínio em **Plataforma → Instituições → Domínio**.
2. O cliente aponta o domínio para o servidor (registro `A` para o IP ou `CNAME` para o domínio da plataforma).
3. O nginx precisa aceitar o host (o `server_name _;` padrão já aceita qualquer um) e repassá-lo (`proxy_set_header Host $host;` e `X-Forwarded-Host $host;`, já no `deploy/nginx.conf`).
4. Emita o certificado HTTPS do domínio (ex.: `certbot --nginx -d escola.com.br`), ou use um proxy com TLS sob demanda (Caddy) para muitos clientes.

As páginas públicas são renderizadas no servidor do Next, que chama a API em `API_INTERNAL_URL` (padrão `http://localhost:8000`; no Docker, `http://backend:8000`).

O isolamento no banco usa Row Level Security. A API deve conectar com um usuário **que não seja superusuário** do PostgreSQL (o `setup.sh` já cria o usuário `wedu`, dono do banco); superusuários ignoram as políticas.

## Portas internas
| Serviço   | Porta |
|-----------|-------|
| Backend   | 8000  |
| Frontend  | 3000  |
| Nginx     | 80    |
| PostgreSQL| 5432  |

## Microfone em rede local

Navegadores só liberam `getUserMedia` em contexto seguro: `https://` ou `http://localhost`.
Ao acessar por IP, por exemplo `http://172.16.102.76:3000`, o microfone será bloqueado pelo navegador.

Para testar a aula de voz em outro dispositivo na mesma rede, suba o frontend em HTTPS:

```bash
cd frontend
npm run dev:https
```

Depois acesse:

```text
https://172.16.102.76:3000
```

Na primeira execução, o Next pode pedir a senha do sistema para instalar uma CA local via `mkcert`.
Aceite o certificado local no navegador.

Em produção, não exponha o BeVox diretamente como `https://dominio:8001`. A porta `8001` normalmente fala HTTP/WebSocket puro, então o navegador falha ao abrir `wss://dominio:8001/...` se não houver TLS nessa porta.

O `npm start` do frontend sobe `server.mjs`, que roda o Next e faz proxy WebSocket em `/bevox/` para o BeVox local. Deixe `BEVOX_PUBLIC_URL` vazio quando o BeVox estiver no mesmo servidor. O frontend usará:

```text
wss://seu-dominio/bevox/ws/voice/stream
```

Se o BeVox estiver em outro serviço/domínio com TLS próprio, configure `BEVOX_PUBLIC_URL` com a URL pública HTTPS desse serviço, sem o caminho `/ws/voice/stream`.

Um `404` em `/api/quizzes/lesson/<id>/attempts` significa que a aula não tem quiz cadastrado para esse aluno; essa chamada é opcional e não bloqueia o microfone.

## Atualizar após mudanças

### Opção recomendada

Use o script genérico de atualização:

```bash
cd /var/www/W-Edu
sudo bash deploy/update.sh
```

Se o projeto estiver em outro diretório:

```bash
sudo APP_DIR=/var/www/W-Edu bash /var/www/W-Edu/deploy/update.sh
```

O script aceita variáveis para outros projetos:

```bash
sudo APP_DIR=/var/www/my-app \
  BRANCH=main \
  BACKEND_DIR=api \
  FRONTEND_DIR=web \
  BACKEND_SERVICE=my-api \
  FRONTEND_SERVICE=my-web \
  MIGRATE_CMD="PYTHONPATH=/var/www/my-app/api .venv/bin/alembic --config alembic.ini upgrade head" \
  FRONTEND_BUILD_CMD="npm ci && npm run build" \
  bash /var/www/my-app/deploy/update.sh
```

### Manual

```bash
cd /var/www/W-Edu

# Backend
git pull
cd backend && .venv/bin/pip install -r requirements.txt
PYTHONPATH=/var/www/W-Edu/backend .venv/bin/alembic --config alembic.ini upgrade head
sudo systemctl restart wedu-backend

# Frontend
cd ../frontend && npm ci && npm run build
sudo systemctl restart wedu-frontend
```
