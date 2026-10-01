# Manual da Coordenação

A coordenação monta a estrutura acadêmica, os cursos e as turmas, acompanha professores e alunos e tem acesso a tudo o que a secretaria e os professores fazem.

## Menu

| Item | Para quê |
|---|---|
| **Acadêmico** | Programas, disciplinas, matrizes, períodos letivos, turmas, matrículas, avaliação e unidades |
| **Diário de classe** | Todas as turmas (mesmas telas do professor) |
| **Orientações** | Estágios e TCCs |
| **Secretaria** | Mesmas rotinas da secretaria |
| **Cursos** | Cursos livres/online: módulos, aulas e pré-requisitos |
| **Trilhas** | Sequências de cursos |
| **Agenda** | Turmas de cursos, instrutores, salas e unidades, encontros presenciais ou lives |
| **Certificados** | Regras, emissão e validação |
| **Comunicação** | Avisos enviados e modelos das mensagens |
| **Usuários** | Cadastro de pessoas, filtros por perfil e dossiê de cada pessoa (responsáveis, matrículas, ocorrências) |
| **Almoxarifado** | Relatórios de consumo (operação fica com a administração) |

## Estrutura acadêmica (Acadêmico)

As abas seguem a ordem natural de montagem:

1. **Programas**: cada curso regular (ex.: Ensino Médio, Técnico em Enfermagem, Bacharelado). Abra o programa para montar a **Matriz curricular** (**Criar matriz**, depois incluir as disciplinas por período, com carga horária, créditos e se é obrigatória). No programa também se definem horas de atividades complementares, de estágio e se exige TCC.
2. **Disciplinas**: cadastro das disciplinas e pré-requisitos.
3. **Períodos letivos**: ano/semestre/módulo com início e fim. Abra o período para o **Calendário acadêmico** (feriados, provas, eventos) e as etapas de avaliação (**Adicionar etapa**).
4. **Turmas**: turmas-grupo do período (ex.: 1º ano A). Abra a turma para ver **Alunos** e a **Agenda**.
5. **Matrículas**: matrícula do aluno no programa e na turma.
6. **Avaliação**: esquemas de avaliação (etapas, pesos, média mínima, recuperação).
7. **Unidades**: campi/unidades da instituição.

## Cursos e trilhas

- **Cursos**: **Novo Curso** (nome, descrição, modalidade). Em **Gerenciar curso**: abas **Módulos**, **Aulas** e **Pré-requisitos**. A lista pode ser vista em grade ou lista.
- **Trilhas**: monte sequências de cursos; o aluno vê no catálogo.

## Agenda e turmas de cursos

Em **Agenda**: cadastre **Unidades** e **Salas** (com capacidade), crie **Turmas** (curso, período, capacidade, sala), vincule **Instrutores** e agende os encontros presenciais ou lives. O check-in presencial pode ser feito por QR code.

## Acompanhamento pedagógico

- **Diário de classe**: você abre qualquer turma e vê as mesmas abas do professor (notas, chamada, resultado, agenda, ocorrências, frequência e benefícios). Em **Frequência e evasão**, use **Readmitir** para o aluno desligado por faltas quando houver justificativa. Veja o [manual do professor](professor.md).
- **Integralização**: na ficha do aluno (Secretaria) avalie as **atividades complementares** enviadas pelos alunos (aceitar com as horas, ou recusar com justificativa).
- **Orientações**: acompanhe estágios e TCCs (o orientador é indicado no cadastro do estágio e do TCC).

## Certificados

Em **Certificados**, escolha o curso e use as abas:

- **Regras**: critérios de aprovação (frequência mínima, nota, conclusão das aulas) e **Salvar regra**;
- **Emitir**: alunos elegíveis e emissão;
- **Validação**: como conferir em `/validate-certificate`;
- **Emitidos**: certificados já emitidos.

## Comunicação

Em **Comunicação**:

- **Eventos**: avisos enviados pela plataforma, com a situação (**Pendente**, **Enviado**, **Falhou**). O envio é automático; nos que falharam aparece o motivo e o botão **Tentar novamente**. **Enviar pendentes agora** antecipa a fila.
- **Templates**: o texto de cada aviso por canal (Interno, WhatsApp, E-mail, Push).
  - **Novo template**: escolha o evento e o canal e escreva título e mensagem. As variáveis disponíveis (ex.: `{student_name}`, `{class_name}`) aparecem abaixo da mensagem e são preenchidas com os dados do evento.
  - Lápis de cada template: editar título, mensagem e se está **ativo**. Template desativado é ignorado: o aviso usa o texto do canal interno ou o padrão da plataforma.

## Secretaria, professores e almoxarifado

Você tem as mesmas rotinas da secretaria ([manual da secretaria](secretaria.md)) e pode requisitar materiais como os professores. No **Almoxarifado**, a coordenação vê os **Relatórios** de consumo por turma, professor e material, estoque baixo e empréstimos atrasados.

## Conforme o tipo da instituição

- **Escola**: etapas de ensino, componentes curriculares e matriz por série; ano letivo com bimestres; acompanhamento dos diários e do resultado final.
- **Universidade**: cursos de graduação com créditos, pré-requisitos, optativas, horas complementares, estágio e TCC; avaliação das atividades complementares.
- **Profissionalizante**: cursos técnicos por módulo, ou cursos livres com aulas, trilhas e certificados.
- **Curso gratuito / programa social**: turmas com limite de faltas, readmissão de desligados e regras de certificado.
- **Corporativo**: conteúdos, trilhas, encontros (presenciais ou lives) e certificados por curso.

Detalhes no [guia por tipo de instituição](tipos-de-instituicao.md).
