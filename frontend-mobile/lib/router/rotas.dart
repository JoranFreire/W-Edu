import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../features/auth/data/usuario.dart';

class Rotas {
  static const carregando = '/carregando';
  static const login = '/login';
  static const loginFacial = '/login/face';
  static const inicio = '/';
  static const avisos = '/avisos';
  static const agenda = '/agenda';
  static const boletim = '/boletim';
  static const dependentes = '/dependentes';
  static const perfil = '/perfil';
  static const biometria = '/perfil/biometria';
  static const cadastroFacial = '/perfil/biometria/cadastro';
  static const beneficios = '/beneficios';
  static const materiais = '/materiais';
  static const chamada = '/chamada';

  static String dependente(String alunoId) => '$dependentes/$alunoId';
  static String chamadaTurma(String turmaId) => '$chamada/$turmaId';
  static String chamadaEncontro(String turmaId, String encontroId) => '$chamada/$turmaId/$encontroId';
}

/// As abas do app, na ordem dos ramos do router. Cada pessoa vê só as dos papéis
/// que tem: aluno (agenda, boletim), responsável (dependentes); acumulando, vê todas.
enum Aba {
  inicio(Rotas.inicio, 'Início', Icons.home_outlined, Icons.home_rounded),
  avisos(Rotas.avisos, 'Avisos', Icons.notifications_none_rounded, Icons.notifications_rounded),
  agenda(Rotas.agenda, 'Agenda', Icons.event_note_outlined, Icons.event_note_rounded),
  boletim(Rotas.boletim, 'Boletim', Icons.grading_outlined, Icons.grading_rounded),
  dependentes(Rotas.dependentes, 'Dependentes', Icons.family_restroom_outlined, Icons.family_restroom_rounded),
  perfil(Rotas.perfil, 'Perfil', Icons.person_outline_rounded, Icons.person_rounded);

  const Aba(this.rota, this.nome, this.icone, this.iconeSelecionado);
  final String rota;
  final String nome;
  final IconData icone;
  final IconData iconeSelecionado;

  bool visivelPara(Usuario usuario) => switch (this) {
        Aba.agenda || Aba.boletim => usuario.ehAluno,
        Aba.dependentes => usuario.ehResponsavel,
        _ => true,
      };

  static List<Aba> doUsuario(Usuario usuario) => values.where((aba) => aba.visivelPara(usuario)).toList();

  /// A aba dona de um caminho (`/dependentes/123` → dependentes).
  static Aba? doCaminho(String local) => values
      .where((aba) => aba != Aba.inicio && (local == aba.rota || local.startsWith('${aba.rota}/')))
      .firstOrNull ?? (local == Rotas.inicio ? Aba.inicio : null);
}

/// Para onde mandar a pessoa, dado o estado da sessão. `null` = pode ficar.
///
/// Fora do GoRouter para poder ser testada sem montar app nenhum.
String? redirecionar(AsyncValue<Usuario?> auth, String local) {
  final naEntrada = local == Rotas.login || local == Rotas.loginFacial || local == Rotas.carregando;

  // Ainda conferindo o token salvo, ou falhou ao conferir (sem rede): espera
  // na tela de carregamento, que oferece "tentar de novo".
  if (!auth.hasValue || auth.hasError) {
    return local == Rotas.carregando ? null : Rotas.carregando;
  }

  final usuario = auth.value;
  if (usuario == null) return local == Rotas.login || local == Rotas.loginFacial ? null : Rotas.login;
  if (naEntrada) return Rotas.inicio;

  // Benefícios do próprio aluno (o responsável os vê em cada dependente).
  if (local == Rotas.beneficios && !usuario.ehAluno) return Rotas.inicio;
  // Requisições de material: quem tem a permissão de pedir (professores, por padrão).
  if (local == Rotas.materiais && !usuario.podeRequisitarMaterial) return Rotas.inicio;
  // Chamada facial: quem ministra aulas.
  if ((local == Rotas.chamada || local.startsWith('${Rotas.chamada}/')) && !usuario.ministraAulas) return Rotas.inicio;

  // Aba de um papel que a pessoa não tem (ex.: link antigo depois de trocar de papel).
  final aba = Aba.doCaminho(local);
  return aba != null && !aba.visivelPara(usuario) ? Rotas.inicio : null;
}
