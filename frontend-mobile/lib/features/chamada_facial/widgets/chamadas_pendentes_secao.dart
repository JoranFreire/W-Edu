import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/format/datas.dart';
import '../../../router/rotas.dart';
import '../chamada_facial_providers.dart';
import '../data/chamada_pendente.dart';

/// Chamadas fotografadas sem rede: enviadas sozinhas ao abrir a tela e ao voltar para o app; as já
/// enviadas abrem a revisão. Descartar apaga as fotos do aparelho.
class ChamadasPendentesSecao extends ConsumerStatefulWidget {
  const ChamadasPendentesSecao({super.key});

  @override
  ConsumerState<ChamadasPendentesSecao> createState() => _ChamadasPendentesSecaoState();
}

class _ChamadasPendentesSecaoState extends ConsumerState<ChamadasPendentesSecao> {
  late final AppLifecycleListener _ciclo;
  bool _enviando = false;

  @override
  void initState() {
    super.initState();
    _ciclo = AppLifecycleListener(onResume: _enviar);
  }

  @override
  void dispose() {
    _ciclo.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    if (_enviando) return;
    setState(() => _enviando = true);
    try {
      await ref.read(chamadasPendentesProvider.notifier).enviar();
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Future<void> _descartar(ChamadaPendente chamada) async {
    final confirmou = await showDialog<bool>(
      context: context,
      builder: (contexto) => AlertDialog(
        title: const Text('Descartar esta chamada?'),
        content: Text('As fotos de ${chamada.titulo} serão apagadas do aparelho, sem enviar.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(contexto, false), child: const Text('Manter')),
          FilledButton(onPressed: () => Navigator.pop(contexto, true), child: const Text('Descartar')),
        ],
      ),
    );
    if (confirmou ?? false) await ref.read(chamadasPendentesProvider.notifier).descartar(chamada.id);
  }

  @override
  Widget build(BuildContext context) {
    final pendentes = ref.watch(chamadasPendentesProvider).value ?? const [];
    if (pendentes.isEmpty) return const SizedBox.shrink();
    final tema = Theme.of(context);
    final aEnviar = pendentes.where((c) => !c.enviada).length;
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ListTile(
              leading: const Icon(Icons.cloud_upload_outlined),
              title: Text('Chamadas guardadas no aparelho (${pendentes.length})', style: tema.textTheme.titleSmall),
              trailing: aEnviar == 0
                  ? null
                  : _enviando
                      ? const SizedBox.square(dimension: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : TextButton(onPressed: _enviar, child: const Text('Enviar agora')),
            ),
            for (final chamada in pendentes)
              ListTile(
                title: Text(chamada.titulo),
                subtitle: Text('${chamada.fotos.length} foto(s) · ${formatarDiaHora(chamada.criadaEm)} · '
                    '${chamada.enviada ? 'pronta para revisar' : 'aguardando internet'}'),
                onTap: chamada.enviada
                    ? () => context.go(Rotas.chamadaEncontro(chamada.turmaId, chamada.encontroId, pendenteId: chamada.id))
                    : null,
                trailing: IconButton(
                  tooltip: 'Descartar',
                  icon: const Icon(Icons.delete_outline_rounded),
                  onPressed: () => _descartar(chamada),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
