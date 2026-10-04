import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/agenda/screens/agenda_screen.dart';
import '../features/attendance/screens/attendance_classes_screen.dart';
import '../features/attendance/screens/attendance_meetings_screen.dart';
import '../features/attendance/screens/attendance_screen.dart';
import '../features/auth/auth_providers.dart';
import '../features/auth/screens/loading_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/benefits/screens/benefits_screen.dart';
import '../features/biometrics/screens/biometrics_screen.dart';
import '../features/biometrics/screens/face_enrollment_screen.dart';
import '../features/dependents/screens/dependent_screen.dart';
import '../features/dependents/screens/dependents_screen.dart';
import '../features/face_login/screens/face_login_screen.dart';
import '../features/home/screens/home_screen.dart';
import '../features/materials/screens/materials_screen.dart';
import '../features/notices/screens/notices_screen.dart';
import '../features/profile/screens/profile_screen.dart';
import '../features/report_card/screens/report_card_screen.dart';
import 'routes.dart';
import 'shell_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  // O router é criado uma vez; o que muda com o login é só o redirect, que
  // roda de novo a cada aviso deste notifier.
  final sessionChanged = ValueNotifier(0);
  ref.listen(authProvider, (_, _) => sessionChanged.value++);
  ref.onDispose(sessionChanged.dispose);

  return GoRouter(
    initialLocation: Routes.loading,
    refreshListenable: sessionChanged,
    redirect: (context, state) => redirect(ref.read(authProvider), state.matchedLocation),
    routes: [
      GoRoute(path: Routes.loading, builder: (_, _) => const LoadingScreen()),
      GoRoute(path: Routes.login, builder: (_, _) => const LoginScreen()),
      GoRoute(path: Routes.faceLogin, builder: (_, _) => const FaceLoginScreen()),
      // Um ramo por aba, na ordem de `AppTab`; cada um guarda a própria pilha e rolagem.
      // A barra mostra só as abas dos papéis da pessoa.
      StatefulShellRoute.indexedStack(
        builder: (_, _, shell) => ShellScreen(shell: shell),
        branches: [
          _tab(
            GoRoute(
              path: Routes.home,
              builder: (_, _) => const HomeScreen(),
              routes: [
                GoRoute(path: Routes.benefits.substring(1), builder: (_, _) => const BenefitsScreen()),
                GoRoute(path: Routes.materials.substring(1), builder: (_, _) => const MaterialsScreen()),
                GoRoute(
                  path: Routes.attendance.substring(1),
                  builder: (_, _) => const AttendanceClassesScreen(),
                  routes: [
                    GoRoute(
                      path: ':offering',
                      builder: (_, state) => AttendanceMeetingsScreen(offeringId: state.pathParameters['offering']!),
                      routes: [
                        GoRoute(
                          path: ':meeting',
                          builder: (_, state) => AttendanceScreen(
                            offeringId: state.pathParameters['offering']!,
                            meetingId: state.pathParameters['meeting']!,
                            pendingId: state.uri.queryParameters['pending'],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
          _tab(GoRoute(path: Routes.notices, builder: (_, _) => const NoticesScreen())),
          _tab(GoRoute(path: Routes.agenda, builder: (_, _) => const AgendaScreen())),
          _tab(GoRoute(path: Routes.reportCard, builder: (_, _) => const ReportCardScreen())),
          _tab(
            GoRoute(
              path: Routes.dependents,
              builder: (_, _) => const DependentsScreen(),
              routes: [
                GoRoute(
                  path: ':id',
                  builder: (_, state) => DependentScreen(studentId: state.pathParameters['id']!),
                ),
              ],
            ),
          ),
          _tab(
            GoRoute(
              path: Routes.profile,
              builder: (_, _) => const ProfileScreen(),
              routes: [
                GoRoute(
                  path: 'biometrics',
                  builder: (_, _) => const BiometricsScreen(),
                  routes: [GoRoute(path: 'enrollment', builder: (_, _) => const FaceEnrollmentScreen())],
                ),
              ],
            ),
          ),
        ],
      ),
    ],
  );
});

StatefulShellBranch _tab(GoRoute route) => StatefulShellBranch(routes: [route]);
