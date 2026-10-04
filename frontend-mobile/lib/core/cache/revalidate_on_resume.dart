import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cache_providers.dart';

/// Ao voltar para o app, confere de novo as versões: as telas abertas baixam
/// só o que mudou enquanto ele estava em segundo plano.
class RevalidateOnResume extends ConsumerStatefulWidget {
  const RevalidateOnResume({super.key, required this.child});

  final Widget child;

  @override
  ConsumerState<RevalidateOnResume> createState() => _RevalidateOnResumeState();
}

class _RevalidateOnResumeState extends ConsumerState<RevalidateOnResume> {
  late final AppLifecycleListener _lifecycle;

  @override
  void initState() {
    super.initState();
    _lifecycle = AppLifecycleListener(onResume: () => ref.invalidate(remoteVersionsProvider));
  }

  @override
  void dispose() {
    _lifecycle.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
