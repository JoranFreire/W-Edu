# Manual do Aluno

O que você encontra no menu e como usar cada parte. Alguns itens só aparecem se a sua instituição usa o recurso (por exemplo, mensalidades ou matrícula por disciplina).

## Primeiros passos

1. Entre em `/login` com o e-mail e a senha recebidos.
2. Em **Configurações**, confira seus dados e troque a senha.
3. O **Dashboard** mostra um resumo: cursos em andamento, progresso e últimas atividades.

## Cursos e aulas

- **Meus Cursos** (catálogo): lista os cursos disponíveis. Clique em **Matricular** para entrar num curso livre; nos que você já faz, aparece **Matriculado** e o link **Continuar →**.
  - As **Trilhas de aprendizagem** (no topo da página) mostram uma sequência recomendada de cursos.
  - Use o botão de grade/lista ao lado do título para mudar a exibição.
- Dentro do curso, abra as aulas em ordem. Aulas com pré-requisito só liberam depois de concluir o curso anterior.
- **Progresso**: avanço por curso, aulas concluídas e atividades recentes.
- **Sessões de Voz**: histórico das conversas com o professor IA (quando disponível no curso), com duração e transcrição.

## Notas, frequência e histórico

- **Boletim**: médias de cada etapa já fechada pelo professor e o resultado final quando publicado (aprovado, reprovado, em recuperação).
- **Histórico escolar**: todas as disciplinas da sua matriz curricular, notas, coeficiente de rendimento (CR) e quanto da matriz já foi cumprido.
- **Integralização**: o que falta para concluir o curso, em quatro abas:
  - **Requisitos**: disciplinas obrigatórias, créditos, horas de atividades complementares, estágio e TCC, com o que já foi cumprido.
  - **Atividades complementares**: cadastre a atividade (título, tipo, horas) e anexe o comprovante. A coordenação avalia; o resultado chega em **Avisos**.
  - **Estágio**: registre empresa, supervisor e período; lance as horas no diário de estágio. O orientador valida cada lançamento.
  - **TCC**: tema, orientador e entrega final.

## Matrícula em disciplinas (cursos por disciplina/crédito)

Disponível quando a instituição abre uma **janela de matrícula**.

1. Abra **Matrícula em disciplinas**. A página mostra o período, o prazo da janela e o limite de créditos.
2. Escolha as turmas. O sistema avisa antes de confirmar se houver:
   - pré-requisito não cumprido;
   - **choque de horário** com outra turma escolhida;
   - turma sem vagas (nesse caso você pode entrar na **lista de espera**, se a janela permitir).
3. Confirme. Você pode trocar ou cancelar disciplinas enquanto a janela estiver aberta.
4. Se abrir uma vaga numa turma em que você está na lista de espera, a matrícula é feita automaticamente e você recebe o aviso **Vaga confirmada**.

Precisa de uma exceção (pré-requisito, limite de créditos)? Fale com a secretaria; ela pode matricular você por fora da regra.

## Agenda escolar e avisos

- **Agenda escolar**: tarefas, provas, eventos e avisos publicados para as suas turmas, por data.
- **Avisos**: comunicados da instituição (ocorrências, agenda, boletim, vagas, convocações, requisições). Clique para marcar como lido ou use **Marcar todos como lidos**. O sino no topo mostra quantos estão sem ler.

## Mensalidades e contratos

- **Mensalidades**: parcelas da sua matrícula com vencimento e situação.
  - Pagando **até o vencimento**, vale o desconto de pontualidade (quando houver).
  - Depois do vencimento incidem **multa** e **juros** proporcionais aos dias de atraso; o valor atualizado aparece na parcela.
  - Bolsas e descontos concedidos já vêm aplicados.
  - Se um responsável financeiro foi cadastrado, ele também vê essas parcelas.
- **Contratos**: contratos de matrícula e rematrícula. Leia, baixe o PDF e clique em **Aceitar**. O aceite fica registrado com data e um código, que pode ser conferido em `/validate-contract`.

## Editais e cursos gratuitos

1. Acesse `/inscricoes` (sem login), escolha o edital e preencha a inscrição. A conta é criada na hora; anote o **protocolo**.
2. Em **Inscrições** (já logado), envie os comprovantes pedidos: escolha o **tipo de comprovante**, selecione o arquivo (PDF, JPG ou PNG) e clique em **Enviar comprovante**. Cada documento mostra se está *em conferência*, *aceito* ou *recusado*.
3. Acompanhe a situação: *inscrição recebida*, *selecionado*, *lista de espera* ou *não elegível*. O resultado público fica em `/inscricoes/<edital>/resultado`.
4. Se for **convocado**, você recebe um aviso e precisa **confirmar a vaga até a data indicada**; sem confirmação, a vaga passa para o próximo da lista.
5. É possível **cancelar a inscrição** enquanto o edital estiver em andamento.

## Benefícios

**Benefícios** lista o que você recebeu de programas sociais da instituição (lanche, kit de material, vale-transporte…), com data e quantidade. Em cursos com limite de faltas, a frequência abaixo do mínimo pode levar ao desligamento: você é avisado em **Avisos**.

## Certificados

**Certificados** mostra os certificados emitidos, com download do PDF e o **código de validação**. Qualquer pessoa confere a autenticidade em `/validate-certificate`.

## Dúvidas frequentes

- **Não vejo meu boletim**: as notas só aparecem depois que o professor fecha a etapa.
- **A matrícula em disciplinas não abre**: a janela pode estar fechada ou não ser do seu programa. Confira as datas na página ou fale com a secretaria.
- **O valor da mensalidade mudou**: depois do vencimento entram multa e juros; antes dele pode valer o desconto de pontualidade.
