import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/features/auth/data/institution.dart';
import 'package:wedu_mobile/features/auth/data/user.dart';
import 'package:wedu_mobile/router/routes.dart';

import '../helpers/fakes.dart';

User _user(List<String> roles, {List<String> permissions = const []}) => User.fromJson(
  userJson(role: roles.first, roles: roles),
  Institution.fromJson(institutionJson()),
  permissions: permissions,
);

void main() {
  test('conferindo a sessão espera no carregamento', () {
    expect(redirect(const AsyncLoading(), Routes.home), Routes.loading);
    expect(redirect(const AsyncLoading(), Routes.loading), isNull);
  });

  test('sem rede ao conferir não manda para o login', () {
    expect(redirect(AsyncError(StateError('x'), StackTrace.empty), Routes.home), Routes.loading);
  });

  test('sem sessão vai para o login', () {
    expect(redirect(const AsyncData(null), Routes.notices), Routes.login);
    expect(redirect(const AsyncData(null), Routes.login), isNull);
  });

  test('logado sai das telas de entrada', () {
    expect(redirect(AsyncData(_user(['student'])), Routes.login), Routes.home);
  });

  test('abas seguem os papéis: aluno, responsável e os dois', () {
    final student = _user(['student']);
    final guardian = _user(['guardian']);
    final teacherAndGuardian = _user(['instructor', 'guardian']);

    expect(AppTab.forUser(student), [AppTab.home, AppTab.notices, AppTab.agenda, AppTab.reportCard, AppTab.profile]);
    expect(AppTab.forUser(guardian), [AppTab.home, AppTab.notices, AppTab.dependents, AppTab.profile]);
    expect(AppTab.forUser(teacherAndGuardian), contains(AppTab.dependents));

    expect(redirect(AsyncData(guardian), Routes.reportCard), Routes.home);
    expect(redirect(AsyncData(guardian), Routes.dependent('s-1')), isNull);
    expect(redirect(AsyncData(student), Routes.dependents), Routes.home);
  });

  test('benefícios próprios só para quem é aluno', () {
    expect(redirect(AsyncData(_user(['student'])), Routes.benefits), isNull);
    expect(redirect(AsyncData(_user(['guardian'])), Routes.benefits), Routes.home);
  });

  test('requisições de material só para quem pode requisitar', () {
    final teacher = _user(['instructor'], permissions: ['warehouse.request']);
    expect(redirect(AsyncData(teacher), Routes.materials), isNull);
    expect(redirect(AsyncData(_user(['student'])), Routes.materials), Routes.home);
  });

  test('login facial é tela de entrada', () {
    expect(redirect(const AsyncData(null), Routes.faceLogin), isNull);
    expect(redirect(AsyncData(_user(['student'])), Routes.faceLogin), Routes.home);
  });

  test('chamada facial só para quem ministra aulas', () {
    final teacher = _user(['instructor'], permissions: ['teaching.access']);
    expect(redirect(AsyncData(teacher), Routes.attendanceMeeting('t', 'e')), isNull);
    expect(redirect(AsyncData(_user(['student'])), Routes.attendance), Routes.home);
  });
}
