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
