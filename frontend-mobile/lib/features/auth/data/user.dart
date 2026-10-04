import 'institution.dart';

/// Quem está logado, na instituição ativa. Espelha o `StudentOut` do backend.
///
/// A pessoa pode acumular papéis (aluna e professora, funcionário e responsável);
/// as abas do app aparecem conforme `roles`.
class User {
  const User({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    required this.roles,
    required this.institution,
    this.permissions = const [],
  });

  final String id;
  final String name;
  final String email;

  /// O papel principal.
  final String role;

  /// Todos os papéis na instituição ativa, o principal primeiro.
  final List<String> roles;
  final Institution institution;

  /// Permissões na instituição (`/access/me`): papéis padrão mais perfis de acesso.
  final List<String> permissions;

  bool get isStudent => roles.contains('student');
  bool get isGuardian => roles.contains('guardian');
  bool get canRequestMaterials => permissions.contains('warehouse.request');
  bool get teaches => permissions.contains('teaching.access');

  String get firstName => name.split(' ').first;

  /// Separa o cache de cada conta (e instituição) no mesmo aparelho.
  String get cacheOwner => '${institution.id}_$id';

  factory User.fromJson(Map<String, dynamic> json, Institution institution, {List<String> permissions = const []}) {
    final role = json['role'] as String;
    final roles = (json['roles'] as List<dynamic>? ?? const []).cast<String>();
    return User(
      id: json['id'] as String,
      name: (json['name'] as String? ?? '').trim(),
      email: json['email'] as String,
      role: role,
      roles: roles.isEmpty ? [role] : roles,
      institution: institution,
      permissions: permissions,
    );
  }
}
