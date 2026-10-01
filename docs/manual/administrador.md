# Manual do Administrador da Instituição

O administrador configura a instituição, gerencia usuários e permissões, o financeiro e o almoxarifado, e tem acesso a todas as telas da coordenação, secretaria e professores.

## Primeiros passos (implantação)

1. **Instituição**: nome, identidade visual (logo e **cor principal**), tipo de instituição (define os termos usados nas telas: série/semestre/módulo, disciplina/componente) e unidades (campi). O plano contratado aparece na mesma página.
2. **Usuários**: cadastre coordenadores, secretaria, professores e alunos. Em **Empresas**, cadastre organizações parceiras (para turmas corporativas ou gestores de empresa).
3. **Acadêmico**: monte programas, disciplinas, matrizes, períodos letivos e turmas (veja o [manual da coordenação](coordenacao.md)).
4. **Perfis de acesso**: conceda permissões extras quando alguém acumula funções.
5. **Financeiro**: planos de mensalidade e cobranças.
6. **Comunicação**: revise os templates dos avisos.

## Usuários

Em **Usuários**:

- **Usuários**: crie, edite e desative pessoas, definindo o papel básico: Aluno, Professor, Coordenador, Secretaria, Responsável, Gestor de empresa ou Administrador.
  - **Filtros por perfil** no topo da lista (Alunos, Responsáveis, Professores, Coordenação, Secretaria…), com a quantidade de cada um, e **busca** por nome ou e-mail. O último filtro fica lembrado.
  - Clique no nome para abrir o **dossiê** da pessoa: dados pessoais; **responsáveis** do aluno, com parentesco, contato e indicação de financeiro, principal e quem pode buscar; **dependentes** do responsável; matrículas, com o atalho **Abrir ficha** para a ficha completa na Secretaria; cursos e certificados; resumo financeiro; ocorrências recentes; e turmas que o professor leciona. Cada responsável e cada dependente abre o próprio dossiê. As seções aparecem conforme as suas permissões (o financeiro, por exemplo, só para quem tem acesso ao financeiro).
- **Empresas**: organizações vinculadas (o gestor de empresa vê financeiro, documentos, relatórios e usuários só da sua empresa).

## Perfis de acesso

**Perfis de acesso** soma permissões a qualquer pessoa da instituição, sem trocar o papel dela. Exemplos: professor que também opera o almoxarifado; funcionário administrativo com acesso ao financeiro.

1. Veja os **perfis padrão** (o que cada papel já pode fazer).
2. Crie um perfil, dê um nome e marque as permissões:

| Permissão | Libera |
|---|---|
| Administrar a instituição | Configurações, usuários, exclusões, financeiro geral |
| Gerenciar perfis de acesso | Esta tela (só concede o que você mesmo possui) |
| Gerir estrutura acadêmica e cursos | Programas, matrizes, turmas, encontros, certificados, comunicação, financiadores |
| Diário de classe e orientações | Notas, chamada, resultados, estágio e TCC |
| Secretaria acadêmica | Matrículas, ficha do aluno, documentos, editais, contratos, janelas de matrícula, programas sociais |
| Vida escolar e benefícios | Ocorrências, agenda da turma, frequência, entrega de benefícios |
| Financeiro educacional | Bolsas, descontos, extratos, multa e juros |
| Requisitar materiais | Pedir materiais ao almoxarifado |
| Operar o almoxarifado | Materiais, entradas, aprovações, retiradas e devoluções |
| Relatórios do almoxarifado | Consumo, estoque baixo e atrasos |

3. Atribua o perfil às pessoas. O menu delas passa a mostrar os novos itens no próximo acesso. Para retirar, remova a pessoa do perfil.

## Financeiro

Em **Financeiro**:

- **Planos**, **Assinaturas** e **Cobranças**: cobranças avulsas ou recorrentes de cursos livres e empresas.
- **Mensalidades educacionais** (botão no topo):
  1. Crie o **plano de mensalidade**: nome, base de cobrança, período letivo, programa ou turma-grupo, valor, número de parcelas e primeiro vencimento.
  2. Use **Gerar cobranças** para criar as parcelas das matrículas. Bolsas e descontos vigentes entram no valor.
  3. Ao receber, use **Baixar** na parcela; depois do vencimento o sistema calcula multa (2%) e juros (1% ao mês, proporcional aos dias).
- Bolsas e descontos por aluno ficam na ficha do aluno (Secretaria → aba **Financeiro**).

## Almoxarifado

Em **Almoxarifado**:

- **Materiais**: **Cadastrar** o material (nome, tipo **consumo** ou **permanente**, unidade, categoria, local de guarda, estoque mínimo, custo) e lançar **Entradas** de estoque.
- **Requisições**: as requisições dos professores chegam aqui. Analise e **Aprovar** (pode ajustar quantidades, aprovação parcial) ou **Recusar** com observação. Depois, **Registrar retirada** e, para itens permanentes, **Registrar devolução** (com data limite).
- **Relatórios**: consumo por turma, professor e material; estoque baixo; devoluções atrasadas. O custo dos materiais usados em turmas financiadas entra na prestação de contas do financiador.

## Documentos e relatórios

- **Documentos**: contratos, termos e materiais com versão e vínculo.
- **Relatórios**: visão executiva de operação, conclusão, presença e receita.

## Demais rotinas

Tudo o que a coordenação, a secretaria e os professores fazem também está disponível para o administrador:

- [Manual da coordenação](coordenacao.md): estrutura acadêmica, cursos, certificados, comunicação.
- [Manual da secretaria](secretaria.md): matrículas, ficha do aluno, editais, contratos, programas sociais.
- [Manual do professor](professor.md): diário de classe e orientações.

## Mais de uma instituição

Se você administra mais de uma instituição, troque no seletor do topo. Dados, usuários e configurações são sempre da instituição selecionada; nada é compartilhado entre elas.

## Conforme o tipo da instituição

Escolha o **tipo** em **Instituição** antes de montar a estrutura acadêmica: ele define os nomes usados em todas as telas. O roteiro de implantação de cada tipo (escola, universidade, profissionalizante pago, curso gratuito/programa social, corporativo e mista) está no [guia por tipo de instituição](tipos-de-instituicao.md).
