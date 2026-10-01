# Manual da Secretaria

Matrículas, ficha do aluno, documentos, editais, contratos, janelas de matrícula, programas sociais e agenda das turmas.

## Menu

| Item | Para quê |
|---|---|
| **Secretaria** | Lista de matrículas e atalhos para as demais rotinas |
| **Agenda das turmas** | Publicar tarefas, provas, eventos e avisos para alunos e responsáveis |
| **Avisos** | Sua caixa de comunicados |

Na página **Secretaria**, os botões do topo levam às rotinas: **Programas sociais**, **Editais**, **Janelas de matrícula**, **Modelos de contrato** e **Agenda das turmas**.

## Matrículas e ficha do aluno

1. Em **Secretaria**, localize a matrícula: busque por nome, e-mail ou número de matrícula, ou filtre por programa.
2. Clique para abrir a **ficha do aluno**, organizada em abas:

| Aba | O que fazer |
|---|---|
| **Histórico escolar** | Ver disciplinas, notas, CR e baixar o histórico em PDF |
| **Disciplinas** | Matricular o aluno em turmas do período, inclusive por exceção (fora da janela, sem pré-requisito ou acima do limite de créditos) |
| **Integralização** | Ver o que falta para concluir; avaliar atividades complementares |
| **Estágio e TCC** | Acompanhar estágio e trabalho de conclusão |
| **Aproveitamento** | Registrar aproveitamento de estudos (disciplina cursada em outra instituição): disciplina da matriz, instituição, nota; depois **Deferir** ou **Indeferir** |
| **Documentos e conclusão** | **Emitir declaração** (matrícula, frequência, conclusão…), baixar PDF e registrar a **Conclusão do programa** |
| **Contratos** | **Emitir contrato** a partir de um modelo e acompanhar o aceite |
| **Responsáveis** | **Vincular** responsáveis ao aluno e indicar o responsável financeiro |
| **Ocorrências** | Registrar e consultar ocorrências do aluno (todas as turmas) |
| **Movimentações** | Linha do tempo da matrícula |
| **Financeiro** | Mensalidades, bolsas e descontos do aluno (se você tiver acesso ao financeiro) |

### Movimentar a matrícula

Na ficha, use as ações da matrícula: **Trancar**, **Reativar**, **Rematricular**, **Cancelar matrícula** ou **Concluir programa**. Cada movimentação fica registrada em **Movimentações**.

### Declarações

Em **Documentos e conclusão**, escolha o tipo e clique em **Emitir declaração**. O PDF traz um código que qualquer pessoa confere em `/validate-declaration`.

## Responsáveis

1. Na ficha, aba **Responsáveis**, informe os dados do responsável (ou selecione um já cadastrado) e clique em **Vincular**.
2. Marque se ele é o **responsável financeiro**: ele passa a ver e receber as mensalidades.
3. O responsável recebe acesso próprio, com boletim, comunicados, ocorrências e agenda dos dependentes. Veja o [manual do responsável](responsavel.md).

## Janelas de matrícula (matrícula por disciplina)

Em **Janelas de matrícula**:

1. Crie a janela: nome, período letivo, programa (ou todos), abertura, fechamento, mínimo e máximo de créditos, e se aceita **lista de espera**.
2. Cadastre os **horários** das turmas oferecidas: o sistema usa esses horários para barrar choque entre turmas.
3. Durante a janela, os alunos se matriculam sozinhos. Exceções são feitas pela ficha do aluno, aba **Disciplinas**.

## Editais (processos seletivos e cursos gratuitos)

Em **Editais**:

1. **Crie o edital**: título, curso, vagas, abertura e encerramento, prazo para confirmar (dias) e a forma de seleção:
   - **Ordem de inscrição** (quem se inscreve primeiro);
   - **Sorteio** (com semente registrada, para auditoria);
   - **Análise de perfil** (nota dada pela secretaria).
2. Defina os **requisitos** (idade mínima/máxima, município exigido, renda máxima por pessoa), os **comprovantes** exigidos (separados por vírgula) e as **vagas reservadas** com quem concorre à reserva.
3. **Abrir inscrições**: o edital aparece em `/inscricoes`. Use **Página pública** para ver como o candidato vê.
4. Durante as inscrições, confira os comprovantes de cada candidato (**aceitar**/**recusar**), marque se a reserva está ok (**Reserva ok** / **Recusar reserva**) e, na análise de perfil, use **Salvar nota**.
5. **Encerrar inscrições** e clique em **Executar seleção**: o sistema convoca os aprovados e coloca os demais em lista de espera.
6. Os convocados confirmam a vaga em **Inscrições**. Use **Processar prazos** para liberar as vagas de quem não confirmou a tempo e convocar os próximos.
7. O resultado público fica em `/inscricoes/<edital>/resultado`.

## Modelos de contrato

Em **Modelos de contrato**, cadastre o texto base dos contratos de matrícula e rematrícula. Os contratos são emitidos pela ficha do aluno (aba **Contratos**) e aceitos pelo aluno ou responsável; o aceite pode ser conferido em `/validate-contract`.

## Programas sociais

Em **Programas sociais** (Financiadores):

1. **Cadastrar financiador** (prefeitura, empresa, fundo…) e vincular as turmas que ele financia.
2. Em **Benefícios e estoque**, use **Cadastrar item** (lanche, kit, vale-transporte…) e registre as **entradas** de estoque (compra ou doação).
3. A **entrega** dos benefícios aos presentes em cada encontro é registrada no diário da turma (aba **Benefícios**, botão **Registrar entrega**), pelo professor ou pela coordenação.
4. **Prestação de contas** de cada financiador: inscritos, matriculados, ativos, concluintes, desistentes e desligados, evasão, benefícios entregues e materiais do almoxarifado usados nas turmas. Use **Baixar planilha (CSV)** para enviar ao financiador.

### Frequência e desligamento

Em turmas com limite de faltas, o aluno que passa do limite é desligado automaticamente e avisado. A readmissão (**Readmitir**, quando houver justificativa) é feita pela coordenação na aba **Frequência e evasão** do diário da turma; os desligamentos entram na prestação de contas.

## Agenda das turmas e ocorrências

- **Agenda das turmas**: escolha o período letivo e a turma, o tipo (tarefa, prova, evento, aviso), a data e o texto, e clique em **Publicar**. Alunos e responsáveis recebem aviso.
- **Ocorrências**: registre pela ficha do aluno (aba **Ocorrências**). O histórico reúne as ocorrências registradas pela secretaria e pelos professores.

## Financeiro do aluno

Com acesso ao financeiro, a aba **Financeiro** da ficha mostra as mensalidades do aluno. Ali você pode **Conceder** bolsas e descontos (percentual ou valor fixo, com vigência; o desconto de pontualidade só vale pagando até o vencimento) e **Encerrar** os vigentes; o valor das parcelas futuras é recalculado. Os planos de mensalidade e a geração das cobranças ficam com a administração.
