import 'package:dio/dio.dart';

import '../../../core/network/api_error.dart';

/// O Persona responde com códigos (`detail`); aqui viram frases para a pessoa.
const _mensagens = {
  'adult_only': 'Só maiores de 18 anos autorizam por si. Se a data de nascimento estiver errada, fale com a secretaria.',
  'subject_is_adult': 'O aluno é maior de idade: ele mesmo autoriza pelo app.',
  'guardian_purpose_not_allowed': 'O responsável autoriza só o login e a catraca.',
  'terms_outdated': 'O termo foi atualizado. Leia a nova versão e autorize de novo.',
  'institution_required': 'Entre de novo no app e tente outra vez.',
  'no_active_consent': 'Autorize pelo menos um uso do rosto antes de cadastrá-lo.',
  'challenge_invalid': 'O tempo da conferência acabou. Tente de novo.',
};

String mensagemDoPersona(Object erro, String padrao) {
  if (erro is DioException) {
    final detalhe = (erro.response?.data is Map) ? (erro.response!.data as Map)['detail'] : null;
    if (detalhe is String && _mensagens.containsKey(detalhe)) return _mensagens[detalhe]!;
    if (erro.response?.statusCode == 422) {
      return 'Não deu para conferir o rosto (luz, enquadramento ou movimentos). Tente de novo.';
    }
  }
  return mensagemDeErro(erro, padrao);
}
