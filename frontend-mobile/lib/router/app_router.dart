import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/agenda/screens/agenda_screen.dart';
import '../features/auth/auth_providers.dart';
import '../features/auth/screens/carregando_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/beneficios/screens/beneficios_screen.dart';
import '../features/biometria/screens/biometria_screen.dart';
import '../features/biometria/screens/cadastro_facial_screen.dart';
import '../features/avisos/screens/avisos_screen.dart';
import '../features/boletim/screens/boletim_screen.dart';
import '../features/dependentes/screens/dependente_screen.dart';
import '../features/dependentes/screens/dependentes_screen.dart';
import '../features/inicio/screens/inicio_screen.dart';
import '../features/login_facial/screens/login_facial_screen.dart';
import '../features/materiais/screens/materiais_screen.dart';
import '../features/perfil/screens/perfil_screen.dart';
import 'rotas.dart';
import 'shell_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  // O router é criado uma vez; o que muda com o login é só o redirect, que
  // roda de novo a cada aviso deste notifier.
  final sessaoMudou = ValueNotifier(0);
  ref.listen(authProvider, (_, _) => sessaoMudou.value++);
  ref.onDispose(sessaoMudou.dispose);

  return GoRouter(
    initialLocation: Rotas.carregando,
    refreshListenable: sessaoMudou,
    redirect: (context, state) => redirecionar(ref.read(authProvider), state.matchedLocation),
    routes: [
      GoRoute(path: Rotas.carregando, builder: (_, _) => const CarregandoScreen()),
      GoRoute(path: Rotas.login, builder: (_, _) => const LoginScreen()),
      GoRoute(path: Rotas.loginFacial, builder: (_, _) => const LoginFacialScreen()),
      // Um ramo por aba, na ordem de `Aba`; cada um guarda a própria pilha e rolagem.
      // A barra mostra só as abas dos papéis da pessoa.
      StatefulShellRoute.indexedStack(
        builder: (_, _, shell) => ShellScreen(shell: shell),
        branches: [
          _aba(GoRoute(
            path: Rotas.inicio,
            builder: (_, _) => const InicioScreen(),
            routes: [
              GoRoute(path: Rotas.beneficios.substring(1), builder: (_, _) => const BeneficiosScreen()),
              GoRoute(path: Rotas.materiais.substring(1), builder: (_, _) => const MateriaisScreen()),
            ],
          )),
          _aba(GoRoute(path: Rotas.avisos, builder: (_, _) => const AvisosScreen())),
          _aba(GoRoute(path: Rotas.agenda, builder: (_, _) => const AgendaScreen())),
          _aba(GoRoute(path: Rotas.boletim, builder: (_, _) => const BoletimScreen())),
          _aba(GoRoute(
            path: Rotas.dependentes,
            builder: (_, _) => const DependentesScreen(),
            routes: [
              GoRoute(path: ':id', builder: (_, state) => DependenteScreen(alunoId: state.pathParameters['id']!)),
            ],
          )),
          _aba(GoRoute(
            path: Rotas.perfil,
            builder: (_, _) => const PerfilScreen(),
            routes: [
              GoRoute(
                path: 'biometria',
                builder: (_, _) => const BiometriaScreen(),
                routes: [GoRoute(path: 'cadastro', builder: (_, _) => const CadastroFacialScreen())],
              ),
            ],
          )),
        ],
      ),
    ],
  );
});

StatefulShellBranch _aba(GoRoute rota) => StatefulShellBranch(routes: [rota]);
