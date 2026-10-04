# W-Edu — App mobile

App Flutter para alunos e responsáveis: início, avisos, agenda, boletim, dependentes, benefícios liberados e requisições de material (QR para a retirada, disponível offline).
As abas seguem os papéis da pessoa na instituição (quem é aluno e responsável vê as duas coisas).

Stack: Riverpod 3 + go_router + dio + flutter_secure_storage, organizado por feature.

```
lib/
  core/       config, tema, rede (dio, interceptor do token, erros), formatação
  shared/ds/  design system (`ds.dart` exporta tudo)
  features/   auth, inicio, avisos, agenda, boletim, dependentes, perfil
              cada uma com data/ (models + repositório), <feature>_providers.dart, screens/, widgets/
  router/     rotas, abas por papel e redirect de autenticação
```

## Cache e uso offline

As telas pessoais (avisos, agenda, boletim, dependentes, benefícios) e a sessão ficam salvas em disco, como o catálogo do
WS-ServicePortal. Ao abrir, o app mostra o que está salvo na hora e consulta `GET /sync/versions`: só baixa de novo
a área cuja versão mudou (a versão sobe sozinha no backend a cada gravação nas tabelas da área). Sem rede, fica com o
que está salvo. Puxar para atualizar ignora a versão e baixa direto; voltar para o app confere as versões de novo; sair
da conta apaga o cache.

## Login facial (Persona)

Com `--dart-define=PERSONA_BASE_URL=https://persona.exemplo/api/v1`, a tela de login oferece **Entrar com o rosto**
para a última conta que entrou com senha no aparelho (o login facial é 1:1). O app fala direto com o Persona:
pede o desafio de prova de vida, tira uma foto por passo (de frente e virando para os dois lados), envia ao Persona,
que confere e assina um assertion, e troca esse assertion pelo token em `POST /auth/facial-login` do W-Edu. As fotos
não passam pelo W-Edu nem ficam no aparelho. Qualquer recusa volta para a senha. Sem a variável, o app fica só com senha.

Em **Perfil → Reconhecimento facial**, cada pessoa vê e decide os usos do rosto, cada um com o próprio termo: entrar no
app, catraca e presença (só maiores de 18). A partir de 16 anos a pessoa autoriza sozinha o login e a catraca; abaixo
disso, quem autoriza é o responsável, na aba **Rosto** do dependente. Com algum uso autorizado, a pessoa cadastra o próprio rosto com a mesma prova de vida
do login. Revogar um uso não desliga os outros.

## Rodar

Com a API no ar (ex.: `docker compose up -d` na raiz e `docker compose --profile demo run --rm seed`):

```bash
flutter pub get
flutter run                                              # emulador Android usa http://10.0.2.2:8000, iOS http://localhost:8000
flutter run --dart-define=API_BASE_URL=http://192.168.0.10:8000   # aparelho físico na mesma rede
```

Conta de demonstração: `aluno@alfa.example.com` / `e2e-senha-123`.

## Verificações

```bash
flutter analyze
flutter test
```
