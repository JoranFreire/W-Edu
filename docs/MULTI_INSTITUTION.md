# W-Edu — Plataforma Multi-Instituicao

Este documento define como o W-Edu evolui de LMS hibrido para uma plataforma SaaS capaz de gerenciar **escolas**, **universidades** e **cursos profissionalizantes** na mesma instalacao.

Decisoes tomadas:

- **Multi-tenant**: uma instalacao atende varias instituicoes com dados isolados.
- **Nucleo academico generico primeiro**: uma unica estrutura academica configuravel por tipo de instituicao, em vez de tres sistemas separados.
- **Nao quebrar o que existe**: cursos, trilhas, turmas, certificados e financeiro atuais continuam funcionando e passam a ser o perfil "curso livre/profissionalizante".

---

## 1. Diagnostico

| Area | Hoje | Lacuna |
|---|---|---|
| Tenant | `organizations` representa empresa cliente B2B | Nao existe a entidade instituicao nem isolamento de dados |
| Estrutura | Curso → Modulo → Aula | Faltam programa, matriz curricular, disciplina, periodo letivo e etapas |
| Turmas | `class_offerings` por curso | Falta turma-serie (escola) e turma por disciplina (universidade) |
| Avaliacao | Quiz, trabalho e avaliacao pratica por curso | Faltam plano de avaliacao, notas por etapa, media, recuperacao e situacao final |
| Frequencia | Presenca por encontro/QR Code | Falta diario de classe por disciplina e percentual minimo por periodo |
| Secretaria | Certificados e GED | Faltam historico, boletim, declaracoes, trancamento, transferencia e rematricula |
| Pessoas | Aluno, instrutor, coordenador, gestor empresa, admin | Faltam responsavel (pais), secretaria, admin da instituicao e super admin da plataforma |

---

## 2. Multi-tenant

### 2.1 Entidades

```text
institutions             id, slug, name, legal_name, document, type, status, settings(json), branding(json), created_at
institution_memberships  id, institution_id, user_id, role, is_active, created_at
campuses                 id, institution_id, name, address, is_active
```

- `institutions.type`: `school`, `university`, `vocational`, `corporate`, `mixed`. Define os presets e a nomenclatura da interface, mas nao limita as funcionalidades.
- `settings`: escala de notas, frequencia minima, tipo de periodo, regra de media, recuperacao e rotulos.
- `institution_memberships` permite que uma mesma pessoa atue em mais de uma instituicao, por exemplo um professor que da aula em duas escolas.
- `locations` passa a pertencer a um `campus`.
- `organizations` (empresas B2B) passa a pertencer a uma instituicao.

### 2.2 Isolamento

- Coluna `institution_id` em todas as tabelas raiz: `courses`, `learning_paths`, `locations`, `class_offerings`, `organizations`, `billing_plans`, `documents`, `notification_templates`, `certificates` e as novas tabelas academicas.
- As tabelas filhas herdam o isolamento pelo pai. Exemplo: `lessons` via `courses`.
- Resolucao do tenant: subdominio (`escola-x.wedu.com.br`) ou header `X-Institution`, validado contra o claim `inst` do JWT.
- Uma dependencia `get_current_institution` injetada nos routers e um filtro obrigatorio aplicado pelo ORM.
- Numa etapa posterior, Row Level Security no PostgreSQL como segunda barreira.

**Implementado (Fase 11, backend):** `app/core/tenancy.py` guarda a instituicao ativa em `Session.info` na autenticacao. Com ela vinculada, toda consulta a models com `TenantMixin` recebe `institution_id = <ativa>` (inclusive relationships e `Session.get`), inserts recebem a instituicao automaticamente e usuarios ficam restritos aos membros da instituicao. Consultas globais deliberadas usam `execution_options(**UNSCOPED)`. Sessoes sem instituicao (worker de notificacoes, rotas publicas) nao sao filtradas. Nesta etapa `users.role` continua sendo o papel efetivo; `institution_memberships.role` e mantido sincronizado e passa a ser a fonte quando os papeis por instituicao forem ativados.

### 2.3 Papeis

| Papel | Escopo |
|---|---|
| `super_admin` | Plataforma inteira: cria instituicoes, planos SaaS e suporte |
| `institution_admin` | Administrador da instituicao (substitui o `admin` atual dentro do tenant) |
| `secretary` | Secretaria academica: matriculas, documentos, historico e fechamento |
| `coordinator` | Coordenacao pedagogica ou de curso |
| `instructor` | Professor e docente |
| `student` | Aluno |
| `guardian` | Responsavel legal (escola basica) |
| `company_manager` | Gestor de empresa B2B |

### 2.4 Migracao sem ruptura

1. Criar `institutions` e uma instituicao padrao.
2. Adicionar `institution_id` como nullable e fazer backfill com a instituicao padrao.
3. Tornar `institution_id` NOT NULL e criar indices.
4. Criar `institution_memberships` a partir de `users.role`. `users.role` permanece como papel legado ate a migracao completa das permissoes.

---

## 3. Nucleo Academico Generico

### 3.1 Estrutura

```text
Instituicao
 └─ Unidade academica (segmento, faculdade, departamento, eixo tecnologico)
     └─ Programa (Ensino Fundamental II, Bacharelado em Direito, Tecnico em Enfermagem)
         └─ Matriz curricular (versionada)
             └─ Componente curricular → Disciplina (por serie ou semestre)

Calendario
 └─ Periodo letivo (ano letivo 2027, semestre 2027.1, modulo)
     └─ Etapas de avaliacao (bimestres, trimestres, N1/N2)

Oferta
 └─ Turma-grupo (7o ano A, Enfermagem 2027.1 noite)   [opcional]
     └─ Oferta de disciplina (Matematica 7o A; Direito Civil I turma B)
         └─ Inscricao do aluno → notas, diario, frequencia, resultado
```

### 3.2 Entidades

```text
academic_units           id, institution_id, parent_id, name, kind
programs                 id, institution_id, unit_id, code, name, level, degree, duration_terms, total_hours, total_credits, status
subjects                 id, institution_id, code, name, syllabus, hours, credits, course_id(nullable)
subject_prerequisites    id, subject_id, required_subject_id
subject_equivalences     id, subject_id, equivalent_subject_id
curricula                id, program_id, version, valid_from, status
curriculum_components    id, curriculum_id, subject_id, term_number, kind(mandatory|elective|optional), hours, credits
academic_terms           id, institution_id, name, kind(year|semester|quarter|module), starts_on, ends_on, status
grading_periods          id, term_id, name, order, starts_on, ends_on, weight, status(open|closed)
calendar_events          id, institution_id, term_id, date, kind(holiday|school_day|recess|exam|event), title
program_enrollments      id, student_id, program_id, curriculum_id, entry_term_id, registration_number, status, gpa
class_groups             id, institution_id, program_id, term_id, curriculum_term_number, name, shift, capacity, homeroom_teacher_id
```

As estruturas atuais sao estendidas, nao substituidas:

- `class_offerings` ganha `term_id`, `subject_id` e `class_group_id`, todos nullable. Uma oferta pode ser de curso livre (como hoje) ou de disciplina.
- `class_enrollments` ganha `final_grade`, `attendance_rate` e `result` (`approved`, `failed`, `failed_attendance`, `in_progress`, `transferred`, `dropped`).
- `subjects.course_id` permite reaproveitar o conteudo EAD de um curso atual (aulas, video, quiz, professor IA) como material da disciplina.
- `program_enrollments.status` aceita `active`, `locked` (trancado), `graduated`, `dropped` (evadido), `transferred` e `cancelled`.

### 3.3 Mapeamento por tipo

| Conceito | Escola basica | Universidade | Profissionalizante |
|---|---|---|---|
| Programa | Ensino Fundamental II | Bacharelado em Direito | Tecnico em Enfermagem / curso livre |
| Periodo letivo | Ano letivo | Semestre | Modulo ou turma |
| Etapa | Bimestre / trimestre | N1, N2, exame | Modulo |
| Turma-grupo | 7o ano A (fixa) | Opcional | Turma do curso |
| Oferta | Disciplina da turma | Turma da disciplina | Turma do curso (atual) |
| Matricula do aluno | Na turma-grupo, que herda as disciplinas | Por disciplina, com janela e pre-requisitos | No curso ou turma (atual) |
| Resultado | Boletim | Historico + CR/IRA | Certificado |
| Pessoas extras | Responsaveis | — | Empresa B2B |

---

## 4. Avaliacao, Diario e Frequencia

```text
grading_schemes          id, institution_id, name, scale(numeric|concept), min_value, max_value, passing_grade, formula(arithmetic|weighted), recovery_rule, min_attendance
assessment_items         id, offering_id, grading_period_id, name, kind(test|assignment|quiz|practical|participation), weight, max_score, quiz_id, due_at
grade_entries            id, assessment_item_id, enrollment_id, score, concept, notes, graded_by_id, graded_at
period_results           id, enrollment_id, grading_period_id, average, absences, recovery_score, final_average, status
class_diary_entries      id, offering_id, date, lesson_count, content_taught, instructor_id, meeting_id
diary_attendance         id, diary_entry_id, enrollment_id, present, absences, justification
```

- Os itens de avaliacao podem apontar para o quiz, o trabalho ou a avaliacao pratica que ja existem, e a nota entra automaticamente.
- O diario de classe reaproveita `scheduled_meetings` quando o encontro estiver agendado.
- Fechamento de etapa: calcula a media e as faltas, bloqueia a edicao e dispara um evento de notificacao (boletim disponivel).
- O resultado final aplica o `grading_scheme`: media, recuperacao, frequencia minima e situacao.

---

## 5. Secretaria Academica

- Matricula, rematricula, trancamento, cancelamento e transferencia (interna e externa).
- Aproveitamento de estudos e equivalencias.
- Historico escolar calculado a partir de `class_enrollments` + `program_enrollments`.
- Boletim por etapa.
- Declaracoes: matricula, frequencia e conclusao. Geradas pelo motor de PDF e pela assinatura de integridade dos certificados atuais, com validacao publica por codigo.
- Colacao e conclusao do programa.

---

## 6. Perfis Especificos

### Escola basica

- Responsaveis (`guardians`, `student_guardians` com parentesco, responsavel financeiro e autorizacao de retirada).
- Portal e app do responsavel: boletim, frequencia, comunicados e financeiro.
- Ocorrencias disciplinares e agenda escolar.
- Futuro: habilidades BNCC por disciplina e exportacao para o Educacenso.

### Universidade

- Janela de matricula por disciplina, com validacao de pre-requisitos, choque de horario e vagas.
- Creditos, CR/IRA e integralizacao curricular.
- TCC, estagio e atividades complementares com carga horaria.
- Futuro: ENADE e integracao com o e-MEC.

### Profissionalizante

- Continua usando cursos, trilhas, turmas e certificados atuais.
- Programas tecnicos com matriz, estagio supervisionado e carga horaria minima.
- Futuro: integracao com o SISTEC.

---

## 7. Financeiro Educacional

- Mensalidade por programa, turma-grupo ou credito cursado.
- Contrato de matricula e rematricula gerado no GED.
- Bolsas, descontos (irmaos, pontualidade, convenio) e multa/juros.
- Responsavel financeiro distinto do aluno.
- Planos SaaS por instituicao, cobrados pelo `super_admin`.

---

## 8. Principios de Implementacao

- Cada fase entrega migracao Alembic, models, schemas, repositories, services, routers, testes e telas admin, seguindo o padrao atual do monolito modular.
- Toda query nova filtra por `institution_id`, e a verificacao entra nos checadores de permissao existentes.
- Presets por `institutions.type` ajustam os rotulos e os campos exibidos no frontend, sem ramificar regras de negocio.
- Nada do fluxo atual de curso livre e removido. As novas entidades sao opcionais para quem nao as usa.
