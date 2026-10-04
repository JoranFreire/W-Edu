import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/agenda/screens/agenda_screen.dart';
import '../features/auth/auth_providers.dart';
import '../features/auth/screens/loading_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/benefits/screens/benefits_screen.dart';
import '../features/attendance/screens/attendance_meetings_screen.dart';
import '../features/attendance/screens/attendance_screen.dart';
import '../features/attendance/screens/attendance_classes_screen.dart';
import '../features/biometrics/screens/biometrics_screen.dart';
import '../features/biometrics/screens/face_enrollment_screen.dart';
import '../features/notices/screens/notices_screen.dart';
import '../features/report_card/screens/report_card_screen.dart';
import '../features/dependents/screens/dependent_screen.dart';
import '../features/dependents/screens/dependents_screen.dart';
import '../features/home/screens/home_screen.dart';
import '../features/face_login/screens/face_login_screen.dart';
import '../features/materials/screens/materials_screen.dart';
import '../features/profile/screens/profile_screen.dart';
import 'routes.dart';
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
              GoRoute(
                path: Rotas.chamada.substring(1),
                builder: (_, _) => const ChamadaTurmasScreen(),
                routes: [
                  GoRoute(
                    path: ':offering',
                    builder: (_, state) => ChamadaEncontrosScreen(turmaId: state.pathParameters['offering']!),
                    routes: [
                      GoRoute(
                        path: ':meeting',
                        builder: (_, state) => ChamadaScreen(
                          turmaId: state.pathParameters['offering']!,
                          encontroId: state.pathParameters['meeting']!,
                          pendenteId: state.uri.queryParameters['pending'],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
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
                path: 'biometrics',
                builder: (_, _) => const BiometriaScreen(),
                routes: [GoRoute(path: 'enrollment', builder: (_, _) => const CadastroFacialScreen())],
              ),
            ],
          )),
        ],
      ),
    ],
  );
});

StatefulShellBranch _aba(GoRoute rota) => StatefulShellBranch(routes: [rota]);
