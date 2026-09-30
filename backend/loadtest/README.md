# Teste de carga (Locust)

Simula alunos (90%) e administradores (10%) de varias instituicoes ao mesmo tempo.

| Perfil | Acoes |
|---|---|
| Aluno | login, listar cursos, listar/abrir aulas, progresso, consumir aula, check-in por token, certificados |
| Admin | listar usuarios, turmas, inscritos, relatorio de presenca do encontro, matriculas do curso |

## Como rodar

Use sempre um banco dedicado: o seed cria milhares de registros.

```bash
cd backend
pip install -r requirements.txt -r requirements-loadtest.txt

export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wedu_load
createdb wedu_load            # ou via psql
alembic upgrade head
python loadtest/seed.py --institutions 5 --students 200 --courses 5 --lessons 10

# API sem o worker de notificacoes, com varios processos
NOTIFICATION_WORKER_ENABLED=false uvicorn main:app --port 8010 --workers 4

# Interface web em http://localhost:8089
locust -f loadtest/locustfile.py --host http://localhost:8010

# Ou direto no terminal, salvando CSV
locust -f loadtest/locustfile.py --host http://localhost:8010 --headless -u 100 -r 10 -t 90s --csv resultado
```

`-u` e o numero de usuarios simultaneos, `-r` quantos entram por segundo e `-t` a duracao. Cada usuario espera de 1 a 3 s entre as acoes, entao 100 usuarios geram cerca de 50 req/s.

Para comparar resultados, rode o Locust em outra maquina que a API: na mesma maquina ele disputa CPU com a API e o PostgreSQL.

## Resultados de referencia

Maquina de desenvolvimento com 4 CPUs compartilhadas entre API (`--workers 4`), PostgreSQL e Locust; 5 instituicoes x 200 alunos. Servem para comparar versoes, nao como capacidade de producao.

| Cenario | Req/s | Mediana | p95 | Falhas |
|---|---|---|---|---|
| 100 usuarios, antes das otimizacoes | 48 | 13 ms | 160 ms | 0 |
| 100 usuarios, depois | 48 | 11 ms | 38 ms | 0 |
| 300 usuarios entrando 30/s, antes | 66 | 23 ms | 9,3 s | 67 |
| 300 usuarios entrando 3/s, depois | 110 | 12 ms | 45 ms | 0 |
| 100 usuarios com RLS (usuario comum do Postgres) | 48 | 12 ms | 39 ms | 0 |

Consultas SQL por requisicao, antes e depois: relatorio de presenca 207 -> 8, consumir aula 31 -> 10, check-in 45 -> 20.

### Pico de login

Cada login verifica a senha com bcrypt (custo 12, ~290 ms de CPU). Logins em massa (ex.: 300 usuarios em 10 s) saturam a CPU antes do banco. Em producao, dimensione CPU para o pico de login (inicio de aula/prova) ou distribua a API em mais maquinas; nao reduza o custo do bcrypt.

## Conexoes com o banco

Cada processo da API abre ate `DB_POOL_SIZE + DB_MAX_OVERFLOW` conexoes (padrao 10 + 10). Com `--workers N` o PostgreSQL recebe ate `N * 20`; mantenha abaixo de `max_connections` (padrao 100). Para muitas instancias, use PgBouncer em modo `transaction` entre a API e o banco.
