import 'package:flutter/material.dart';

/// Para que o rosto pode ser usado. Cada uma é autorizada (e revogada) separadamente:
/// revogar uma não desliga a outra (ADR 0010 do Persona).
enum Finalidade {
  login('LOGIN', 'Entrar no app com o rosto', 'Usar o rosto em vez da senha ao abrir o app.', Icons.face_rounded),
  catraca('ACCESS', 'Catraca', 'Passar pela catraca da instituição com o rosto (o responsável recebe um aviso).', Icons.door_sliding_rounded),
  presenca('ATTENDANCE', 'Presença em aula', 'O professor registra a chamada com uma foto da sala. Só para maiores de 18 anos.',
      Icons.how_to_reg_rounded);

  const Finalidade(this.valor, this.nome, this.descricao, this.icone);
  final String valor;
  final String nome;
  final String descricao;
  final IconData icone;

  /// O responsável autoriza, pelo dependente menor, só login e catraca.
  bool get responsavelAutoriza => this != Finalidade.presenca;

  static Finalidade? de(String valor) => values.where((f) => f.valor == valor).firstOrNull;
}
