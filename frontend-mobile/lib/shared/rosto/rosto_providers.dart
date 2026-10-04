import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'captura_de_rosto.dart';

/// A câmera da prova de vida (os testes põem uma falsa).
final capturaDeRostoProvider = Provider<CapturaDeRosto>((ref) => CameraFrontal());

/// Tempo para a pessoa fazer cada movimento antes da foto (zero nos testes).
final pausaEntrePassosProvider = Provider<Duration>((ref) => const Duration(seconds: 2));
