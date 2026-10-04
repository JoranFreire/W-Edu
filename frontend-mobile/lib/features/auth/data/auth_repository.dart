import 'package:dio/dio.dart';

import '../../../core/cache/cache_local.dart';
import '../../../core/network/token_store.dart';
import '../../../shared/cofre/cofre_de_arquivos.dart';
import 'instituicao.dart';
import 'usuario.dart';

class AuthRepository {
  AuthRepository(this._dio, this._tokens, this._cache, this._cofre);

  final Dio _dio;
  final TokenStore _tokens;
  final CacheLocal _cache;
  final CofreDeArquivos _cofre;

  /// Pessoa e instituição da última conferência: o app abre com elas sem esperar a rede.
  static const _chaveSessao = 'sessao';

  Future<bool> temSessao() async => await _tokens.ler() != null;

  Future<Usuario> entrar(String email, String senha) async {
    final resposta = await _dio.post<Map<String, dynamic>>(
      'auth/login',
      data: {'email': email.trim(), 'password': senha},
    );
    await _tokens.salvar(resposta.data!['access_token'] as String);
    return eu();
  }

  /// Login facial: troca o assertion que o Persona emitiu (rosto conferido) pelo token.
  Future<Usuario> entrarComRosto(String assertion) async {
    final resposta = await _dio.post<Map<String, dynamic>>('auth/facial-login', data: {'assertion': assertion});
    await _tokens.salvar(resposta.data!['access_token'] as String);
    return eu();
  }

  /// A pessoa, a instituição ativa (a do token) e as permissões nela, juntas. `Future.wait` repassa
  /// o próprio erro da API (o `.wait` de record o embrulharia e o 401 se perderia).
  Future<Usuario> eu() async {
    final [pessoa, instituicao, acesso] = await Future.wait([
      _dio.get<Map<String, dynamic>>('users/me'),
      _dio.get<Map<String, dynamic>>('institutions/current'),
      _dio.get<Map<String, dynamic>>('access/me'),
    ]);
    final dados = {'usuario': pessoa.data!, 'instituicao': instituicao.data!, 'acesso': acesso.data!};
    final usuario = _ler(dados);
    await _cache.salvar(_chaveSessao, EntradaCache(null, dados));
    return usuario;
  }

  Future<Usuario?> sessaoSalva() async {
    final salva = await _cache.ler(_chaveSessao);
    if (salva == null) return null;
    try {
      return _ler(salva.dados);
    } on Object {
      return null;
    }
  }

  /// A API não guarda sessão no servidor: sair é esquecer o token e os dados
  /// pessoais guardados no aparelho (inclusive fotos de chamada ainda não enviadas).
  Future<void> sair() async {
    await _tokens.limpar();
    await _cache.limpar();
    await _cofre.apagarTudo();
  }

  Usuario _ler(Object? dados) {
    final json = dados as Map<String, dynamic>;
    final acesso = json['acesso'] as Map<String, dynamic>? ?? const {};
    return Usuario.fromJson(
      json['usuario'] as Map<String, dynamic>,
      Instituicao.fromJson(json['instituicao'] as Map<String, dynamic>),
      permissoes: (acesso['permissions'] as List<dynamic>? ?? const []).cast<String>(),
    );
  }
}
