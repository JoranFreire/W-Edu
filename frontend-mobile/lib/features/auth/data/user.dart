import 'institution.dart';

/// Quem está logado, na instituição ativa. Espelha o `StudentOut` do backend.
///
/// A pessoa pode acumular papéis (aluna e professora, funcionário e responsável);
/// as abas do app aparecem conforme `papeis`.
class Usuario {
  const Usuario({
    required this.id,
    required this.nome,
    required this.email,
    required this.papel,
    required this.papeis,
    required this.instituicao,
    this.permissoes = const [],
  });

  final String id;
  final String nome;
  final String email;

  /// O papel principal.
  final String papel;

  /// Todos os papéis na instituição ativa, o principal primeiro.
  final List<String> papeis;
  final Instituicao instituicao;

  /// Permissões na instituição (`/access/me`): papéis padrão mais perfis de acesso.
  final List<String> permissoes;

  bool get ehAluno => papeis.contains('student');
  bool get ehResponsavel => papeis.contains('guardian');
  bool get podeRequisitarMaterial => permissoes.contains('warehouse.request');
  bool get ministraAulas => permissoes.contains('teaching.access');

  String get primeiroNome => nome.split(' ').first;

  /// Separa o cache de cada conta (e instituição) no mesmo aparelho.
  String get chaveDoCache => '${instituicao.id}_$id';

  factory Usuario.fromJson(Map<String, dynamic> json, Instituicao instituicao, {List<String> permissoes = const []}) {
    final papel = json['role'] as String;
    final papeis = (json['roles'] as List<dynamic>? ?? const []).cast<String>();
    return Usuario(
      id: json['id'] as String,
      nome: (json['name'] as String? ?? '').trim(),
      email: json['email'] as String,
      papel: papel,
      papeis: papeis.isEmpty ? [papel] : papeis,
      instituicao: instituicao,
      permissoes: permissoes,
    );
  }
}

/// Os nomes dos papéis, iguais aos do site.
const nomesDosPapeis = {
  'student': 'Aluno',
  'instructor': 'Instrutor',
  'coordinator': 'Coordenação',
  'secretary': 'Secretaria',
  'guardian': 'Responsável',
  'company_manager': 'Gestão empresa',
  'institution_admin': 'Admin da instituição',
  'admin': 'Admin',
  'super_admin': 'Admin da plataforma',
};
