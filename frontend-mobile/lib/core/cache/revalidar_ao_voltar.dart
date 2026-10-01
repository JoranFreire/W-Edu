import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cache_providers.dart';

/// Ao voltar para o app, confere de novo as versões: as telas abertas baixam
/// só o que mudou enquanto ele estava em segundo plano.
class RevalidarAoVoltar extends ConsumerStatefulWidget {
  const RevalidarAoVoltar({super.key, required this.child});

  final Widget child;

  @override
  ConsumerState<RevalidarAoVoltar> createState() => _RevalidarAoVoltarState();
}

class _RevalidarAoVoltarState extends ConsumerState<RevalidarAoVoltar> {
  late final AppLifecycleListener _ciclo;

  @override
  void initState() {
    super.initState();
    _ciclo = AppLifecycleListener(onResume: () => ref.invalidate(versoesRemotasProvider));
  }

  @override
  void dispose() {
    _ciclo.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
