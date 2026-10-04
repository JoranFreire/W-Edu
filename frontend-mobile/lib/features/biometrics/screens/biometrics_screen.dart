import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../shared/ds/ds.dart';
import '../biometrics_providers.dart';
import '../widgets/consents_list.dart';
import '../widgets/face_enrollment_card.dart';

/// Reconhecimento facial da própria pessoa: o que está autorizado, o termo de cada uso e o cadastro do rosto.
/// A senha continua valendo sempre; nada aqui é obrigatório.
class BiometriaScreen extends ConsumerWidget {
  const BiometriaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final situacao = ref.watch(minhaSituacaoBiometricaProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Reconhecimento facial')),
      body: switch (situacao) {
        AsyncValue(:final error?, hasValue: false) =>
          ErroView(erro: error, onTentarDeNovo: () => ref.refresh(minhaSituacaoBiometricaProvider.future)),
        AsyncValue(value: final atual?) => RefreshIndicator(
            onRefresh: () => ref.refresh(minhaSituacaoBiometricaProvider.future),
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 16),
              children: [
                Padding(padding: const EdgeInsets.symmetric(horizontal: 16), child: CadastroRostoCard(situacao: atual)),
                const SizedBox(height: 8),
                const Padding(
                  padding: EdgeInsets.fromLTRB(16, 8, 16, 0),
                  child: Text('Cada uso é autorizado separadamente e pode ser revogado quando quiser. '
                      'A senha (e a portaria, na catraca) continua valendo sempre.'),
                ),
                AutorizacoesLista(situacao: atual),
              ],
            ),
          ),
        _ => const Carregando(),
      },
    );
  }
}
