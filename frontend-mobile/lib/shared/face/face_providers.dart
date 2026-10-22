import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'face_capture.dart';

/// A câmera da prova de vida (os testes põem uma falsa).
final faceCameraProvider = Provider<DeviceCameraCapture>((ref) => FrontCamera());

/// A câmera da foto da sala (chamada facial).
final roomCameraProvider = Provider<DeviceCameraCapture>((ref) => BackCamera());

/// Tempo para a pessoa fazer cada movimento antes da foto (zero nos testes).
final stepPauseProvider = Provider<Duration>((ref) => const Duration(seconds: 2));
