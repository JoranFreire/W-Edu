import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/features/agenda/data/item_agenda.dart';
import 'package:wedu_mobile/features/auth/data/instituicao.dart';
import 'package:wedu_mobile/features/auth/data/usuario.dart';
import 'package:wedu_mobile/features/avisos/data/aviso.dart';
import 'package:wedu_mobile/features/beneficios/data/beneficio.dart';
import 'package:wedu_mobile/features/boletim/data/boletim.dart';
import 'package:wedu_mobile/features/dependentes/data/dependente.dart';

import '../helpers/fakes.dart';

void main() {
  test('instituição usa o nome exibido e a cor da marca', () {
    final instituicao = Instituicao.fromJson(instituicaoJson());
    expect(instituicao.nome, 'Colégio Alfa');
    expect(instituicao.corPrimaria, const Color(0xFF059669));
  });

  test('usuário com vários papéis', () {
    final usuario = Usuario.fromJson(usuarioJson(role: 'instructor', roles: ['instructor', 'student', 'guardian']), Instituicao.fromJson(instituicaoJson()));
    expect(usuario.ehAluno, isTrue);
    expect(usuario.ehResponsavel, isTrue);
    expect(usuario.primeiroNome, 'Ana');
  });

  test('aviso lido e não lido', () {
    expect(Aviso.fromJson(avisoJson('a1')).lido, isFalse);
    expect(Aviso.fromJson(avisoJson('a1')).marcadoComoLido().lido, isTrue);
  });

  test('item da agenda lê a data como dia local', () {
    final item = ItemAgenda.fromJson(agendaJson('i1', dia: '2026-10-03'));
    expect(item.data, DateTime(2026, 10, 3));
    expect(item.tipo, TipoAgenda.prova);
    expect(TipoAgenda.de('desconhecido'), TipoAgenda.aviso);
  });

  test('disciplina do boletim', () {
    final disciplina = DisciplinaBoletim.fromJson(boletimJson());
    expect(disciplina.resultado, ResultadoDisciplina.aprovado);
    expect(disciplina.etapas.single.faltas, 2);
    expect(disciplina.frequencia, 0.92);
  });

  test('dependente', () {
    final dependente = Dependente.fromJson(dependenteJson());
    expect(dependente.alunoId, 's-1');
    expect(nomesDoParentesco[dependente.parentesco], 'Mãe');
  });

  test('benefícios: para retirar primeiro e validade vale também offline', () {
    final lista = Beneficio.lista([
      beneficioJson('1', status: 'redeemed'),
      beneficioJson('2', validoAte: '2020-01-01'),
      beneficioJson('3', validoAte: '2099-12-31', item: 'Kit'),
    ]);
    expect(lista.map((b) => b.id), ['3', '1', '2']);
    expect(lista.first.paraRetirar, isTrue);
    expect(lista.first.conteudoQr, 'wedu-beneficio:COD3');
    expect(lista.first.tipo, TipoBeneficio.lanche);
    expect(TipoBeneficio.de('uniform'), TipoBeneficio.uniforme);
    expect(TipoBeneficio.de(null), TipoBeneficio.outro);
    expect(lista.last.situacao(), SituacaoBeneficio.vencido);
    expect(lista[1].situacao(), SituacaoBeneficio.retirado);
  });
}
