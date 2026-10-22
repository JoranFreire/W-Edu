# W-Edu - Matriz de Permissoes

## Perfis de acesso (RBAC)

A autorizacao e por permissao. Cada guard de `app/dependencies.py` exige uma chave do catalogo (`app/services/access/catalog.py`):

| Permissao | Guard | Papeis que ja a concedem |
| --- | --- | --- |
| `institution.manage` | `get_current_admin` | admin, institution_admin, super_admin |
| `access.manage` | `get_current_access_manager` | admin, institution_admin, super_admin |
| `academic.manage` | `get_current_admin_or_coordinator` | administradores e coordinator |
| `teaching.access` | `get_current_teaching_staff` | administradores, coordinator e instructor |
| `secretariat.access` | `get_current_secretariat` | administradores, coordinator e secretary |
| `school_life.access` | `get_current_school_staff` | administradores, coordinator, instructor e secretary |
| `benefits.redeem` | `get_current_benefit_validator` | administradores, coordinator, instructor e secretary (perfil "Cantina" pode ter só esta) |
| `finance.access` | `get_current_finance_staff` | administradores e secretary |
| `warehouse.request` | `get_current_warehouse_requester` | administradores, coordinator e instructor |
| `warehouse.manage` | `get_current_warehouse_manager` | administradores |
| `warehouse.reports` | `get_current_warehouse_reader` | administradores e coordinator |

Uma pessoa pode acumular varios papeis na mesma instituicao (aluno e professor, por exemplo) e ter papeis diferentes em cada instituicao (`institution_member_roles`); a permissao efetiva e a soma das permissoes de todos os papeis dela na instituicao ativa. Cada papel vira um perfil padrao com exatamente as permissoes acima. Perfis personalizados da instituicao (`/access/roles`) somam permissoes a qualquer membro (exceto responsaveis e super admin); as permissoes efetivas sao carregadas na autenticacao e expostas em `/access/me`. Ninguem concede, altera, atribui ou exclui perfil com permissao que nao possui. Plataforma (`get_current_super_admin`), portal do responsavel (`get_current_guardian`) e os guards com escopo de empresa seguem por identidade/papel. Escopos que dependem dos dados (ex.: o instrutor so nas turmas que ministra) continuam nas policies e consideram todos os papeis da pessoa (`app/policies/roles.py`). Matricular alguem num programa da a essa pessoa o papel de aluno; vincular uma conta como responsavel da a ela o papel de responsavel, sem tirar os que ja tinha.

| Recurso | Quem |
| --- | --- |
| Catalogo, perfis padrao, perfis personalizados, membros e atribuicoes (`/access`) | `access.manage` |
| Proprias permissoes (`/access/me`) | Qualquer usuario autenticado |

Este documento registra a regra operacional por papel. A nomenclatura `User` e `/users` e a direcao nova da API; `Student` e `/students` permanecem como compatibilidade de dominio/API, embora a tabela fisica de identidade seja `users`.

## Papeis

- `student`: aluno.
- `instructor`: instrutor.
- `coordinator`: coordenacao academica.
- `company_manager`: gestor de empresa B2B.
- `admin`: administrador da instituicao (papel legado, equivalente a `institution_admin`).
- `institution_admin`: administrador da instituicao.
- `super_admin`: administrador da plataforma; acessa qualquer instituicao e gere instituicoes em `/platform`.
- `secretary`: secretaria academica (matriculas, movimentacoes, aproveitamento e historico).
- `guardian`: responsavel pelo aluno; acessa apenas o portal (`/guardians/me/...`) dos alunos vinculados a ele.

## Instituicoes (multi-tenant)

- Todo acesso autenticado roda dentro de uma instituicao ativa: header `X-Institution` (slug ou id) ou claim `inst` do JWT; sem nenhum dos dois, a primeira membership ativa do usuario.
- O usuario precisa de membership ativa na instituicao; `super_admin` acessa qualquer uma.
- Nas colunas "Admin" das tabelas abaixo leia `admin`, `institution_admin` ou `super_admin`, sempre dentro da instituicao ativa.
- Somente `super_admin` atribui o papel `super_admin` ou altera/exclui um super admin.
- Cadastro publico (`POST /users`) sempre cria `student`, sem empresa, na instituicao do header (ou na padrao).
- Excluir usuario que pertence a outras instituicoes remove apenas o vinculo com a instituicao ativa.

## Regras Gerais

- Autenticacao e area do aluno exigem usuario autenticado ativo.
- Financeiro, documentos e analytics corporativo continuam restritos a `admin` e `company_manager`, com escopo de empresa aplicado nos services.
- Coordenador pode operar a rotina academica, mas nao acessa financeiro/analytics/documentos corporativos pelo menu.
- Acoes destrutivas sensiveis ficam restritas a `admin`.

## Usuarios e Organizacoes

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Ver/editar propria conta | Sim | Sim | Sim | Sim | Sim |
| Listar usuarios admin | Nao | Nao | Sim | Empresa propria | Sim |
| Criar usuario | Nao | Nao | Aluno/instrutor | Aluno/instrutor da empresa | Sim |
| Editar usuario | Nao | Nao | Aluno/instrutor | Aluno/instrutor da empresa | Sim |
| Excluir usuario | Nao | Nao | Nao | Nao | Sim |
| Gerir empresa | Nao | Nao | Listar | Empresa propria | Sim |

## Academico

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Listar/ver cursos, aulas, modulos e trilhas | Sim | Sim | Sim | Sim | Sim |
| Criar/editar curso | Nao | Nao | Sim | Nao | Sim |
| Excluir curso | Nao | Nao | Nao | Nao | Sim |
| Criar/editar modulo | Nao | Nao | Sim | Nao | Sim |
| Excluir modulo | Nao | Nao | Nao | Nao | Sim |
| Criar/editar pre-requisito | Nao | Nao | Sim | Nao | Sim |
| Excluir pre-requisito | Nao | Nao | Nao | Nao | Sim |
| Criar/editar trilha | Nao | Nao | Sim | Nao | Sim |
| Excluir trilha | Nao | Nao | Nao | Nao | Sim |
| Vincular curso a trilha | Nao | Nao | Sim | Nao | Sim |
| Remover curso da trilha | Nao | Nao | Nao | Nao | Sim |
| Criar/editar aula | Nao | Nao | Sim | Nao | Sim |
| Excluir aula | Nao | Nao | Nao | Nao | Sim |
| Criar/editar quiz e questoes | Nao | Nao | Sim | Nao | Sim |
| Excluir quiz e questoes | Nao | Nao | Nao | Nao | Sim |

## Estrutura Curricular (`/academic`)

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Ver unidades, programas, disciplinas e matrizes | Sim | Sim | Sim | Sim | Sim |
| Criar/editar unidade, programa e disciplina | Nao | Nao | Sim | Nao | Sim |
| Excluir unidade, programa e disciplina | Nao | Nao | Nao | Nao | Sim |
| Incluir pre-requisito/equivalencia | Nao | Nao | Sim | Nao | Sim |
| Remover pre-requisito/equivalencia | Nao | Nao | Nao | Nao | Sim |
| Criar matriz, nova versao, componentes, ativar/arquivar | Nao | Nao | Sim | Nao | Sim |
| Excluir matriz em rascunho | Nao | Nao | Nao | Nao | Sim |

| Ver periodos letivos, etapas, calendario e turmas-grupo | Sim | Sim | Sim | Sim | Sim |
| Criar/editar periodo, etapa, evento e turma-grupo; mudar situacao | Nao | Nao | Sim | Nao | Sim |
| Excluir periodo planejado, etapa aberta e turma-grupo vazia | Nao | Nao | Nao | Nao | Sim |
| Listar/criar matriculas no programa e mudar situacao | Nao | Nao | Sim | Nao | Sim |
| Ver as proprias matriculas no programa (`/me`) | Sim | Sim | Sim | Sim | Sim |
| Ver alunos da turma-grupo e alocar/remover | Nao | Nao | Sim | Nao | Sim |

Regras: codigo de programa e de disciplina e unico por instituicao; so matrizes em rascunho sao editaveis; ativar uma matriz arquiva a vigente do mesmo programa; disciplina usada em matriz nao pode ser excluida (desative-a).

Calendario e turmas: periodo `planned -> open -> closed` (reabertura permitida); encerrar o periodo encerra as etapas e bloqueia edicao de etapas, eventos do periodo e alocacao de alunos. Matricula no programa usa a matriz vigente por padrao, gera numero `ano + codigo do programa + sequencial` e segue as transicoes `active <-> locked`, `active/locked -> dropped | transferred | cancelled`, `active -> graduated` (finais nao reabrem). Cada matricula ativa fica em no maximo uma turma-grupo por periodo, respeitando as vagas.

## Avaliacao e Diario (`/assessment`)

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Ver esquemas de avaliacao | Sim | Sim | Sim | Sim | Sim |
| Criar/editar esquema | Nao | Nao | Sim | Nao | Sim |
| Excluir esquema sem turmas | Nao | Nao | Nao | Nao | Sim |
| Plano de avaliacoes, notas, boletim, diario e chamada | Nao | Turmas que ministra | Todas | Nao | Todas |
| Inscrever alunos da turma-grupo na oferta | Nao | Nao | Sim | Nao | Sim |
| Fechar etapa na turma, calcular resultado e lancar recuperacao | Nao | Turmas que ministra | Todas | Nao | Todas |
| Reabrir etapa fechada na turma e publicar resultado (finalizar turma) | Nao | Nao | Sim | Nao | Sim |
| Ver o proprio boletim (`/assessment/my/report-card`) | Sim | Sim | Sim | Sim | Sim |

Etapa encerrada na instituicao, etapa fechada na turma ou periodo letivo encerrado bloqueia notas e itens da etapa e o diario das datas dentro dela; turma finalizada bloqueia tudo. Faltas justificadas nao contam na frequencia. O boletim do aluno mostra so etapas fechadas e, apos a publicacao, o resultado final.

## Secretaria Academica (`/secretariat`)

| Recurso | Student | Instructor | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Listar e criar matriculas no programa | Nao | Nao | Sim | Sim | Sim |
| Rematricula, trancamento, reativacao, cancelamento, evasao | Nao | Nao | Sim | Sim | Sim |
| Transferencia interna/externa e mudanca de matriz | Nao | Nao | Sim | Sim | Sim |
| Registrar aproveitamento de estudos | Nao | Nao | Sim | Sim | Sim |
| Deferir/indeferir aproveitamento | Nao | Nao | Sim | Nao | Sim |
| Historico escolar e linha do tempo da matricula | Nao | Nao | Sim | Sim | Sim |
| Proprio historico (`/secretariat/my/transcripts`) | Sim | Sim | Sim | Sim | Sim |
| Emitir declaracoes e baixar PDF | Nao | Nao | Sim | Sim | Sim |
| Revogar declaracao | Nao | Nao | Sim | Nao | Sim |
| Concluir programa e registrar colacao | Nao | Nao | Sim | Sim | Sim |
| Proprias declaracoes (`/secretariat/my/declarations`) | Sim | Sim | Sim | Sim | Sim |
| Validar declaracao por codigo (`/secretariat/declarations/validate/{code}`) | Publico | Publico | Publico | Publico | Publico |

Toda movimentacao fica registrada em `program_enrollment_events` (quem, quando, justificativa), inclusive mudancas feitas pela rota `/academic/program-enrollments/{id}/status`.

## Responsaveis (`/guardians`)

| Recurso | Student | Guardian | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Vincular, editar e desvincular responsaveis do aluno | Nao | Nao | Sim | Sim | Sim |
| Ver dependentes, boletim, historico e comunicados | Nao | Dependentes vinculados | Nao | Nao | Nao |
| Ver cobrancas do dependente | Nao | So o responsavel financeiro | Nao | Nao | Nao |

A conta do responsavel e unica na plataforma: vincular um e-mail ja cadastrado como responsavel (em outra instituicao ou para irmaos) reaproveita a conta e cria o vinculo com a instituicao ativa.

## Vida escolar (`/school`)

| Recurso | Student | Guardian | Instructor | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- | --- |
| Registrar ocorrencia | Nao | Nao | Sim | Sim | Sim | Sim |
| Ver o historico de ocorrencias do aluno | Nao | Nao | Alunos das ofertas que ministra e das turmas-grupo que rege ou em que leciona | Sim | Sim | Sim |
| Remover ocorrencia | Nao | Nao | So as que registrou | Sim | So as que registrou | Sim |
| Ver e dar ciencia de ocorrencias do dependente | Nao | Dependentes vinculados | Nao | Nao | Nao | Nao |
| Ver agenda da turma-grupo | Nao | Nao | Sim | Sim | Sim | Sim |
| Publicar na agenda da turma-grupo | Nao | Nao | Turmas que rege ou em que leciona | Sim | Sim | Sim |
| Remover item da agenda | Nao | Nao | So os que publicou | Sim | So os que publicou | Sim |
| Agenda das proprias turmas (`/school/my/agenda`) | Sim | Do dependente, no portal | Sim | Sim | Sim | Sim |

O guard `get_current_school_staff` cobre a equipe escolar; o escopo por turma e por autor fica em `app/policies/school_life_access.py`.

Cada registro de ocorrencia, publicacao na agenda e resultado final publicado gera um aviso para o aluno e um para cada responsavel vinculado (sem repetir o responsavel de irmaos da mesma turma).

## Matricula por disciplina (`/registration`)

| Recurso | Student | Instructor | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Criar, editar e remover janelas de matricula | Nao | Nao | Sim | Sim | Sim |
| Definir horario semanal das ofertas | Nao | Nao | Sim | Nao | Sim |
| Ver horario das ofertas | Sim | Sim | Sim | Sim | Sim |
| Ver janelas abertas, catalogo, inscrever e cancelar | Janela aberta do proprio programa | Nao | Nao | Nao | Nao |
| Catalogo do aluno e inscricao fora da janela (com excecao opcional) | Nao | Nao | Sim | Sim | Sim |

## Requisitos de conclusao (`/completion`)

| Recurso | Student | Instructor | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Ver integralizacao de qualquer matricula | Nao | Nao | Sim | Sim | Sim |
| Ver a propria integralizacao, atividades, estagios e TCC | Sim | Sim | Sim | Sim | Sim |
| Declarar e retirar atividade complementar | Matricula propria e ativa | Nao | Nao | Nao | Nao |
| Aprovar ou recusar atividade complementar | Nao | Nao | Sim | Sim | Sim |
| Cadastrar e encerrar estagio; cadastrar TCC | Nao | Nao | Sim | Sim | Sim |
| Listar orientadores (docentes e coordenadores) | Nao | Nao | Sim | Sim | Sim |
| Lancar e remover horas de estagio | Estagio proprio em andamento | Nao | Nao | Nao | Nao |
| Ver diario de horas do estagio | Proprio | Se orientador | Sim | Sim | Sim |
| Validar horas de estagio e registrar entrega/defesa do TCC | Nao | Se orientador | Sim | Nao | Sim |
| Orientacoes em andamento (`/completion/advising`) | Nao | As proprias | Todas | Nao | Todas |

## Mensalidades (`/tuition`)

| Recurso | Student | Guardian | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Planos de mensalidade e geracao das parcelas | Nao | Nao | Nao | Nao | Sim |
| Ver multa e juros | Nao | Nao | Nao | Sim | Sim |
| Alterar multa e juros | Nao | Nao | Nao | Nao | Sim |
| Bolsas e descontos da matricula; extrato da matricula | Nao | Nao | Nao | Sim | Sim |
| Baixa da parcela (pagamento) | Nao | Nao | Nao | Nao | Sim |
| Proprio extrato (como aluno ou pagador) e valor a pagar hoje | Sim | Sim | Sim | Sim | Sim |

O guard `get_current_finance_staff` cobre administracao e secretaria; a consulta de uma cobranca pelo aluno ou pagador fica em `app/policies/tuition_access.py`.

## Contratos (`/contracts`)

| Recurso | Student | Guardian | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Modelos de contrato; emitir, listar, baixar e cancelar contratos da matricula | Nao | Nao | Sim | Sim | Sim |
| Ver, baixar e aceitar o contrato | O proprio | Se responsavel financeiro do aluno | Nao | Nao | Nao |
| Validar contrato pelo codigo (`/contracts/validate/{code}`) | Publico | Publico | Publico | Publico | Publico |

## Planos SaaS (`/saas`)

| Recurso | Super admin | Admin da instituicao | Demais |
| --- | --- | --- | --- |
| Catalogo de planos, assinatura da instituicao, faturas e baixa | Sim | Nao | Nao |
| Plano, uso de alunos e faturas da instituicao ativa (`/saas/current`) | Sim | Sim | Nao |

O limite de alunos do plano vale no cadastro de usuarios com papel aluno (409 ao atingir).

## Processo seletivo (`/admissions`)

| Recurso | Publico | Candidato (qualquer usuario) | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Catalogo de editais, edital e resultado por protocolo | Sim | Sim | Sim | Sim | Sim |
| Inscrever-se, enviar comprovantes, cancelar, confirmar ou desistir da vaga | Nao | Propria inscricao | Propria | Propria | Propria |
| Editais, situacao, inscricoes, analise, comprovantes, selecao e prazos | Nao | Nao | Sim | Sim | Sim |

## Programas sociais e evasao (`/social`, `/retention`)

| Recurso | Student | Instructor | Coordinator | Secretary | Admin |
| --- | --- | --- | --- | --- | --- |
| Cadastrar e alterar financiadores | Nao | Nao | Sim | Nao | Sim |
| Listar financiadores e ver/baixar a prestacao de contas | Nao | Nao | Sim | Sim | Sim |
| Itens de beneficio e entradas de estoque | Nao | Ver itens | Sim | Sim | Sim |
| Entregar beneficios e ver entregas da turma | Nao | Turmas que ministra | Sim | Sim | Sim |
| Liberar beneficio com QR (encontro, turma toda ou aluno), ver e cancelar os liberados da turma | Nao | Turmas que ministra | Sim | Sim | Sim |
| Conferir e validar o QR na retirada (`benefits.redeem`) | Nao | Sim | Sim | Sim | Sim |
| Ver frequencia e risco de evasao da turma | Nao | Turmas que ministra | Sim | Sim | Sim |
| Reavaliar desligamentos e readmitir aluno | Nao | Nao | Sim | Sim | Sim |
| Proprios beneficios recebidos e liberados (QR) | Sim | Sim | Sim | Sim | Sim |

O responsavel ve os beneficios liberados de cada dependente (`/guardians/me/dependents/{id}/vouchers`).

Escopo do instrutor em `app/policies/retention_access.py`.

## Almoxarifado (`/warehouse`)

| Recurso | Permissao |
| --- | --- |
| Ver materiais e saldo | qualquer permissao do almoxarifado (`get_current_warehouse_user`) |
| Requisitar, acompanhar e cancelar as proprias requisicoes (pendentes ou aprovadas) | `warehouse.request` (turma vinculada: so as que ministra, salvo coordenacao) |
| Cadastrar materiais, lancar entradas, aprovar/recusar (aprovar reserva o saldo), ler o QR de retirada, registrar retirada (sem QR: com motivo) e devolucao, historico por material | `warehouse.manage` |
| QR de retirada da propria requisicao aprovada (so quem pediu recebe o codigo) | `warehouse.request` |
| Estoque baixo, devolucoes atrasadas e consumo | `warehouse.reports` |

O almoxarife e um perfil de acesso com `warehouse.manage` (por padrao so administradores a tem).

## Caixa de avisos (`/notifications/me`)

| Recurso | Todos os papeis |
| --- | --- |
| Listar os proprios avisos (todos ou nao lidos) e a contagem de nao lidos | Sim |
| Marcar um aviso ou todos como lidos | So os enderecados a si |

A caixa lista os eventos internos ja entregues ao usuario na instituicao ativa; aviso de outro usuario responde 404.

## Agenda e Presencial

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Listar locais, salas, turmas e encontros | Sim | Sim | Sim | Sim | Sim |
| Criar/editar locais, salas e turmas | Nao | Nao | Sim | Nao | Sim |
| Entrar em turma | Sim | Sim | Sim | Sim | Sim |
| Listar inscricoes e espera da turma | Nao | Nao | Sim | Nao | Sim |
| Criar/editar/encerrar encontro | Nao | Nao | Sim | Nao | Sim |
| Gerar/listar token de check-in | Nao | Nao | Sim | Nao | Sim |
| Check-in do proprio usuario | Sim | Sim | Sim | Sim | Sim |
| Registro manual/listagem de presenca | Nao | Nao | Sim | Nao | Sim |

## Certificacao

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Ver propria certificacao | Sim | Sim | Sim | Sim | Sim |
| Gerir regra de certificado | Nao | Nao | Sim | Nao | Sim |
| Ver elegibilidade/listagens | Nao | Nao | Sim | Nao | Sim |
| Emitir certificado | Nao | Nao | Sim | Nao | Sim |
| Revogar certificado | Nao | Nao | Nao | Nao | Sim |
| Validar certificado publico | Publico | Publico | Publico | Publico | Publico |

## Comunicacao

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Forum e chat autenticado | Sim | Sim | Sim | Sim | Sim |
| Templates e eventos de notificacao | Nao | Nao | Sim | Nao | Sim |
| Processar eventos pendentes | Nao | Nao | Sim | Nao | Sim |

## Administrativo Corporativo

| Recurso | Student | Instructor | Coordinator | Company Manager | Admin |
| --- | --- | --- | --- | --- | --- |
| Financeiro | Nao | Nao | Nao | Empresa propria | Sim |
| Documentos/GED | Nao | Nao | Nao | Empresa propria | Sim |
| Analytics operacional/corporativo | Proprio | Nao | Nao | Empresa propria | Sim |

## Integração com o Persona (`/integrations/persona`, `/auth/facial-login`)

| Recurso | Permissao |
| --- | --- |
| Login facial (`POST /auth/facial-login`) | publico; vale so mensagem assinada pelo Persona com `typ=facial_login` |
| Aviso de passagem na catraca (`POST /integrations/persona/gate-events`) | publico; vale so mensagem assinada pelo Persona com `typ=gate_event` |
| Fins de vinculo da instituicao (`GET /integrations/persona/membership-events`) | `academic.manage` (conta de servico do Persona) |
| Alunos da turma para a chamada facial (`GET /assessment/offerings/{id}/roster`) | `teaching.access`, so turmas que ministra (salvo coordenacao) |
