import 'package:dio/dio.dart';

import 'item_agenda.dart';

/// Agenda escolar: a do aluno logado ou a de um dependente (portal do responsável).
class AgendaRepository {
  AgendaRepository(this._dio);

  final Dio _dio;

  Future<List<ItemAgenda>> minha() => _listar('school/my/agenda');

  Future<List<ItemAgenda>> doDependente(String alunoId) => _listar('guardians/me/dependents/$alunoId/agenda');

  Future<List<ItemAgenda>> _listar(String caminho) async {
    final resposta = await _dio.get<List<dynamic>>(caminho);
    final itens = resposta.data!.map((item) => ItemAgenda.fromJson(item as Map<String, dynamic>)).toList();
    return itens..sort((a, b) => a.data.compareTo(b.data));
  }
}
