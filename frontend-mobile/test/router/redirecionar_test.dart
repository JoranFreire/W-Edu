import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/features/auth/data/instituicao.dart';
import 'package:wedu_mobile/features/auth/data/usuario.dart';
import 'package:wedu_mobile/router/rotas.dart';

import '../helpers/fakes.dart';

Usuario _usuario(List<String> papeis) =>
    Usuario.fromJson(usuarioJson(role: papeis.first, roles: papeis), Instituicao.fromJson(instituicaoJson()));

void main() {
  test('conferindo a sessão espera no carregamento', () {
    expect(redirecionar(const AsyncLoading(), Rotas.inicio), Rotas.carregando);
    expect(redirecionar(const AsyncLoading(), Rotas.carregando), isNull);
  });

  test('sem rede ao conferir não manda para o login', () {
    expect(redirecionar(AsyncError(StateError('x'), StackTrace.empty), Rotas.inicio), Rotas.carregando);
  });

  test('sem sessão vai para o login', () {
    expect(redirecionar(const AsyncData(null), Rotas.avisos), Rotas.login);
    expect(redirecionar(const AsyncData(null), Rotas.login), isNull);
  });

  test('logado sai das telas de entrada', () {
    expect(redirecionar(AsyncData(_usuario(['student'])), Rotas.login), Rotas.inicio);
  });

  test('abas seguem os papéis: aluno, responsável e os dois', () {
    final aluno = _usuario(['student']);
    final responsavel = _usuario(['guardian']);
    final professorEResponsavel = _usuario(['instructor', 'guardian']);

    expect(Aba.doUsuario(aluno), [Aba.inicio, Aba.avisos, Aba.agenda, Aba.boletim, Aba.perfil]);
    expect(Aba.doUsuario(responsavel), [Aba.inicio, Aba.avisos, Aba.dependentes, Aba.perfil]);
    expect(Aba.doUsuario(professorEResponsavel), contains(Aba.dependentes));

    expect(redirecionar(AsyncData(responsavel), Rotas.boletim), Rotas.inicio);
    expect(redirecionar(AsyncData(responsavel), Rotas.dependente('s-1')), isNull);
    expect(redirecionar(AsyncData(aluno), Rotas.dependentes), Rotas.inicio);
  });
}
