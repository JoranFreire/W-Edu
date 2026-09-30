# W-Edu — Roadmap de Implementacao

## Status Atual

**Fase:** 2 — Voz com Professor IA (em andamento)  
**Ultima atualizacao:** 2026-09-30  
**Proximo marco:** Fase 11 — Multi-tenant (plataforma multi-instituicao)

## Visao Alvo

O W-Edu deve evoluir de LMS com professor IA para uma plataforma educacional hibrida, capaz de operar cursos online, presenciais e hibridos com trilhas, turmas, agenda, presenca, avaliacoes, certificacao, comunicacao via W-Omni, financeiro, documentos e analytics.

Documento de referencia: [docs/PLATFORM_TARGET.md](docs/PLATFORM_TARGET.md)

Evolucao multi-instituicao: o W-Edu passa a ser uma plataforma SaaS multi-tenant capaz de gerenciar escolas, universidades e cursos profissionalizantes, com nucleo academico generico configurado por tipo de instituicao. Documento de referencia: [docs/MULTI_INSTITUTION.md](docs/MULTI_INSTITUTION.md)

## Estado Atual do Produto

### Ja existe

- Autenticacao JWT.
- Alunos e administrador.
- Cursos.
- Aulas.
- Matriculas.
- Progresso.
- Sessoes de voz.
- Presenca basica vinculada a aula/sessao.
- Quiz por aula.
- Admin basico de cursos, aulas e alunos.
- Frontend Next.js com dashboard, cursos, aulas, progresso e sessoes.

### Lacunas principais

- Falta separar curso, modulo, trilha, turma e encontro.
- Falta modelar instrutor, coordenador, empresa e perfis detalhados.
- Falta agenda academica com vagas, lista de espera, salas e unidades.
- Falta presenca presencial com QR Code e regras de validacao.
- Certificacao automatica e validacao publica de certificado implementadas no backend.
- Comunicacao por eventos estruturada e base de notificacao implementada.
- Financeiro base implementado; faltam documentos, relatorios e analytics.
- Falta arquitetura modular com fronteiras claras para futura separacao em microservicos.

---

## Fases

### Fase 0 — Planejamento

- [x] Definicao de escopo.
- [x] Arquitetura macro W-Edu, BeVox e W-Matrix.
- [x] Stack escolhida: FastAPI, PostgreSQL e Next.js.
- [x] Entidades principais iniciais definidas.
- [x] Estrutura de pastas criada.
- [x] Repositorio inicializado.

### Fase 1 — Fundacao

Backend:

- [x] Setup do projeto.
- [x] Core: config, database e security.
- [x] Models: Student, Course, Lesson, Enrollment, Progress, Session, Attendance.
- [x] Schemas Pydantic.
- [x] Repositories.
- [x] Services.
- [x] Routers.
- [x] Alembic.
- [x] Testes basicos de API.

Frontend:

- [x] Setup Next.js, Tailwind e TypeScript.
- [x] Login.
- [x] Dashboard do aluno.
- [x] Catalogo de cursos.
- [x] Detalhe do curso.
- [x] Tela de aula.
- [x] Tela de progresso.
- [x] Tela de sessoes.
- [x] Admin com CRUD de cursos, aulas e alunos.
- [x] Build sem erros.
- [x] Deploy em producao.

### Fase 2 — Voz com Professor IA

Integracao BeVox:

- [x] Endpoint: iniciar sessao de voz.
- [x] Botao "Falar com professor" no frontend.
- [x] Webhook BeVox para receber fim de sessao.
- [x] Registro automatico de presenca via webhook.
- [x] Armazenamento de transcricao da sessao.

Integracao W-Matrix:

- [x] Configuracao de agente professor por curso.
- [x] Passagem de contexto da aula para o agente.
- [ ] Recebimento de feedback do agente ao W-Edu.

### Fase 3 — Reorganizacao do Dominio Academico

Objetivo: preparar a base correta antes de crescer funcionalidades.

- [x] Criar camada semantica `User` sobre o modelo legado `Student`, com rotas `/users` e compatibilidade com `/students`.
- [x] Adicionar papeis: aluno, instrutor, coordenador, gestor empresa e admin.
- [x] Refinar acesso do coordenador para operacoes academicas sem liberar financeiro/analytics.
- [x] Restringir acoes destrutivas sensiveis ao papel admin.
- [x] Criar matriz de permissoes, verificador de dependencias criticas por rota, verificador dos guards por papel e verificador HTTP de permissoes criticas.
- [x] Criar empresas B2B.
- [x] Expandir curso com modalidade: online, presencial e hibrido.
- [x] Criar modulos de curso.
- [x] Expandir aulas com tipos: texto, video, PDF, live, presencial, voz e avaliacao.
- [x] Criar trilhas de aprendizagem.
- [x] Criar pre-requisitos entre cursos.
- [x] Criar regras de conclusao por curso.
- [x] Evoluir frontend/admin para usar a nomenclatura `/admin/users` em todas as chamadas de gestao de usuarios.

Entidades esperadas:

```text
users
organizations
student_profiles
instructor_profiles
courses
course_modules
lessons
learning_paths
learning_path_courses
course_prerequisites
completion_rules
```

### Fase 4 — Turmas, Agenda e Presencial

Objetivo: transformar presencial em capacidade nativa da plataforma.

- [x] Criar unidades/locais.
- [x] Criar salas com capacidade.
- [x] Criar recursos de sala/equipamento.
- [x] Criar turmas por curso, periodo, instrutor, sala, vagas e status.
- [x] Criar inscricao em turma separada de matricula em curso.
- [x] Criar lista de espera.
- [x] Criar encontros presenciais e lives agendadas.
- [x] Criar presenca presencial por encontro.
- [x] Implementar check-in por QR Code.
- [x] Exibir QR Code visual para check-in no admin.
- [x] Bloquear conflitos de sala e instrutor ao agendar encontros.
- [x] Exibir agenda real do professor com disponibilidade, encontros e sugestoes.
- [x] Preparar interface para biometria/facial futura.

Entidades esperadas:

```text
locations
rooms
room_resources
instructor_availability
classes
class_enrollments
waitlist_entries
scheduled_meetings
attendance_records
checkin_tokens
```

### Fase 5 — Progresso, Avaliacao e Certificacao

- [ ] Progresso automatico via sessoes concluidas.
- [ ] Avaliacao do aluno pelo agente IA durante a conversa.
- [x] Dashboard de progresso por curso.
- [x] Historico de sessoes com transcricoes.
- [ ] Relatorio do professor com visao geral da turma.
- [x] Avaliacao hibrida: prova online e entrega avaliativa corrigida.
- [x] Trabalhos/atividades com entrega.
- [x] Avaliacao pratica presencial.
- [x] Regras de aprovacao por nota, presenca e progresso.
- [x] Geracao automatica de certificado PDF.
- [x] Validacao publica de certificado por codigo.
- [x] Assinatura digital interna de integridade.

### Fase 6 — Comunicacao com W-Omni

- [x] Criar eventos de dominio: aula marcada, falta registrada, conteudo publicado, certificado emitido.
- [x] Criar templates de notificacao.
- [x] Criar lembretes de aula agendados.
- [x] Integrar WhatsApp via W-Omni.
- [x] Adicionar email.
- [ ] Preparar push mobile.
- [x] Criar chat aluno/instrutor ou integracao inicial com grupos WhatsApp.
- [x] Criar forum por curso/turma.

### Fase 7 — Financeiro

- [x] Criar planos de curso.
- [x] Criar assinatura.
- [x] Criar pagamento por turma.
- [x] Criar estrutura base para PIX.
- [x] Criar estrutura base para cartao.
- [x] Criar estrutura base para boleto.
- [x] Preparar gateway Asaas para checkout, boleto e Pix.

### Fase 8 — Documentos e GED/ECM

- [x] Criar base GED local com upload e versionamento.
- [x] Conectar documentos com curso, turma, aluno e empresa.
- [ ] Criar contratos.
- [ ] Criar termos de participacao.
- [ ] Criar anexos e materiais didaticos versionados.
- [ ] Integrar Alfresco Community Edition.
- [ ] Integrar OnlyOffice.

### Fase 9 — Relatorios, Analytics e IA

- [x] Base de analytics operacional com overview, curso, turma e aluno.
- [x] Relatorio de conclusao por curso/turma.
- [x] Relatorio de frequencia presencial.
- [x] Relatorio de engajamento online.
- [x] Relatorio de desempenho por turma.
- [x] Relatorio de ROI corporativo.
- [ ] Eventos para Cassandra quando houver volume.
- [ ] Identificacao de risco de evasao.
- [ ] Recomendacao de trilhas por IA.
- [ ] Tutor virtual com contexto de curso, aula e historico do aluno.

### Fase 10 — Mobile e Diferenciais Avancados

- [ ] App mobile.
- [ ] Acesso offline.
- [ ] Check-in presencial pelo app.
- [ ] Notificacoes push.
- [ ] Avaliacao de performance por visao computacional.
- [ ] Presenca automatica por reconhecimento facial.

### Fase 11 — Multi-tenant (Instituicoes)

Objetivo: uma instalacao atendendo varias instituicoes com dados isolados.

- [x] Criar `institutions` com tipo (`school`, `university`, `vocational`, `corporate`, `mixed`), settings e branding.
- [x] Criar `institution_memberships` (usuario pode atuar em mais de uma instituicao).
- [x] Criar `campuses` e vincular `locations` ao campus.
- [x] Adicionar `institution_id` nas tabelas raiz com backfill para instituicao padrao.
- [x] Resolver tenant por header `X-Institution` validado contra membership e claim `inst` do JWT.
- [ ] Resolver tenant por subdominio.
- [x] Filtro obrigatorio por instituicao (eventos do ORM em `app/core/tenancy.py`, sem depender de cada repository).
- [ ] Isolar acesso direto por id a tabelas filhas (aulas, modulos, inscricoes etc.) validando o pai.
- [x] Novos papeis: `super_admin`, `institution_admin`, `secretary`, `guardian`.
- [ ] Atualizar matriz e verificadores de permissao com escopo de instituicao.
- [x] API da plataforma (super admin) para criar/gerir instituicoes (`/platform/institutions`).
- [ ] Telas do admin da plataforma.
- [ ] Seletor de instituicao e branding por tenant no frontend.
- [ ] Avaliar Row Level Security no PostgreSQL como segunda barreira.

### Fase 12 — Nucleo Academico Formal

Objetivo: estrutura comum a escola, universidade e profissionalizante.

- [ ] Unidades academicas (segmento, faculdade, departamento, eixo).
- [ ] Programas (serie/etapa de ensino, graduacao, tecnico, livre).
- [ ] Disciplinas com ementa, carga horaria, creditos e vinculo opcional a curso EAD.
- [ ] Pre-requisitos e equivalencias entre disciplinas.
- [ ] Matriz curricular versionada com componentes por serie/semestre.
- [ ] Periodos letivos e etapas de avaliacao (bimestre, trimestre, N1/N2).
- [ ] Calendario academico (dias letivos, feriados, recessos, provas).
- [ ] Matricula no programa com numero de matricula e status.
- [ ] Turma-grupo (ex.: 7o ano A) com turno e professor responsavel.
- [ ] Estender `class_offerings` com periodo, disciplina e turma-grupo.
- [ ] Presets de nomenclatura por tipo de instituicao no frontend.

### Fase 13 — Avaliacao, Diario e Frequencia

- [ ] Esquemas de avaliacao configuraveis (numerica/conceito, media, recuperacao, frequencia minima).
- [ ] Plano de avaliacao por oferta e etapa, reaproveitando quiz, trabalho e avaliacao pratica.
- [ ] Lancamento de notas pelo professor.
- [ ] Diario de classe com conteudo ministrado e frequencia por disciplina.
- [ ] Fechamento de etapa com calculo de media, faltas e bloqueio de edicao.
- [ ] Resultado final por disciplina (aprovado, reprovado, reprovado por falta).

### Fase 14 — Secretaria Academica

- [ ] Matricula, rematricula, trancamento, cancelamento e transferencia.
- [ ] Aproveitamento de estudos.
- [ ] Historico escolar e boletim.
- [ ] Declaracoes (matricula, frequencia, conclusao) com validacao publica.
- [ ] CR/IRA e integralizacao curricular.
- [ ] Conclusao do programa.

### Fase 15 — Perfil Escola Basica

- [ ] Responsaveis e vinculo aluno/responsavel (financeiro, retirada).
- [ ] Portal do responsavel: boletim, frequencia, comunicados, financeiro.
- [ ] Ocorrencias e agenda escolar.
- [ ] Futuro: BNCC e exportacao Educacenso.

### Fase 16 — Perfil Universidade

- [ ] Janela de matricula por disciplina com pre-requisitos, choque de horario e vagas.
- [ ] Creditos e integralizacao.
- [ ] TCC, estagio e atividades complementares.
- [ ] Futuro: ENADE e e-MEC.

### Fase 17 — Perfil Profissionalizante e Financeiro Educacional

- [ ] Programas tecnicos com estagio supervisionado e carga horaria minima.
- [ ] Mensalidade por programa, turma-grupo ou credito.
- [ ] Contratos de matricula/rematricula no GED.
- [ ] Bolsas, descontos, multa e juros.
- [ ] Responsavel financeiro distinto do aluno.
- [ ] Planos SaaS por instituicao.
- [ ] Futuro: SISTEC.

---

## Decisoes de Arquitetura

| Decisao | Escolha | Motivo |
|---|---|---|
| Backend | FastAPI | Mesmo padrao do W-Matrix, simples para integrar com IA |
| Frontend | Next.js | Mesmo padrao do BeVox frontend |
| Banco operacional | PostgreSQL | Dados transacionais e relacionais |
| Cache/filas leves | Redis | Cache, filas simples e estados temporarios |
| Eventos/telemetria | Cassandra | Logs e eventos quando volume justificar |
| Auth | JWT | Stateless e compativel com outros servicos |
| Arquitetura atual | Monolito modular | Mais rapido para estabilizar dominio |
| Arquitetura futura | Microservicos | Extrair quando houver volume ou fronteira madura |
| Tenancy | Multi-tenant por `institution_id` (banco compartilhado) | SaaS para varias instituicoes; RLS como segunda barreira |
| Dominio academico | Nucleo generico + presets por tipo | Evita tres sistemas paralelos para escola, universidade e profissionalizante |

## Fronteiras de Servico Futuras

- `tenant-service`: instituicoes, campi, memberships e configuracoes.
- `user-service`: usuarios, empresas, perfis e permissoes.
- `academic-service`: programas, matrizes, disciplinas, periodos, notas, diario e secretaria.
- `course-service`: cursos, trilhas, modulos, aulas e pre-requisitos.
- `schedule-service`: turmas, agenda, unidades, salas, instrutores, lista de espera e presenca.
- `payment-service`: planos, cobrancas e gateways.
- `notification-service`: W-Omni, templates e eventos.
- `document-service`: contratos, termos, certificados e GED/ECM.
- `analytics-service`: eventos, engajamento, relatorios e IA.

## Entidades do Banco

Estado atual:

```text
users           id, name, email, password_hash, role, organization_id, is_active, created_at
courses         id, name, description, agent_id, created_at
lessons         id, course_id, title, content, order, type, created_at
enrollments     id, student_id, course_id, enrolled_at
progress        id, student_id, lesson_id, status, updated_at
sessions        id, student_id, lesson_id, bevox_session_id, transcript, started_at, ended_at
attendance      id, student_id, lesson_id, session_id, recorded_at
quizzes         id, lesson_id, passing_score, max_attempts, created_at
quiz_questions  id, quiz_id, question, options, correct_index, order
quiz_attempts   id, student_id, quiz_id, score, passed, answers, attempted_at
```

Proxima expansao critica:

```text
users
organizations
student_profiles
instructor_profiles
learning_paths
learning_path_courses
course_modules
course_prerequisites
completion_rules
locations
rooms
room_resources
classes
class_enrollments
waitlist_entries
scheduled_meetings
attendance_records
checkin_tokens
certificates
notification_events
```

## Pontos Criticos

- Curso nao e turma: curso e o produto academico; turma e uma oferta em periodo, local, instrutor e vagas.
- Aula online nao substitui encontro presencial: ambos precisam de entidades e regras proprias.
- Matricula em curso e inscricao em turma podem ser processos diferentes.
- Certificado depende de regras verificaveis: progresso, provas, presenca e aprovacao pratica.
- Comunicacao precisa nascer por eventos para nao ficar acoplada a telas ou rotas especificas.
- Instituicao nao e empresa: `institutions` e o tenant; `organizations` continua sendo empresa cliente B2B dentro de uma instituicao.
- Disciplina nao e curso: disciplina e componente curricular com carga/creditos; pode reaproveitar conteudo EAD de um curso.
- Toda consulta nova deve ser filtrada por instituicao.
