# W-Edu — App mobile

App Flutter para alunos e responsáveis: início, avisos, agenda, boletim e dependentes.
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
