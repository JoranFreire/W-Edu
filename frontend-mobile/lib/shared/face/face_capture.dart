import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/widgets.dart';

/// Uma câmera do aparelho, atrás de uma interface: os testes usam uma falsa.
abstract interface class DeviceCameraCapture {
  /// Abre a câmera; falha se não houver câmera ou permissão.
  Future<void> open();

  /// O que a câmera está vendo (para a pessoa se posicionar).
  Widget preview();

  /// Uma foto JPEG, só em memória (não é gravada no aparelho depois do envio).
  Future<Uint8List> takePhoto();

  Future<void> close();
}

/// Câmera frontal (login e cadastro do rosto): resolução média, rosto nítido e foto bem
/// abaixo do limite de 4 MB do Persona.
class FrontCamera extends DeviceCamera {
  FrontCamera() : super(CameraLensDirection.front, ResolutionPreset.medium);
}

/// Câmera traseira (foto da sala na chamada facial): resolução alta, rostos pequenos ao fundo.
class BackCamera extends DeviceCamera {
  BackCamera() : super(CameraLensDirection.back, ResolutionPreset.high);
}

class DeviceCamera implements DeviceCameraCapture {
  DeviceCamera(this._lens, this._resolution);

  final CameraLensDirection _lens;
  final ResolutionPreset _resolution;
  CameraController? _controller;

  @override
  Future<void> open() async {
    final cameras = await availableCameras();
    final chosen = cameras.where((c) => c.lensDirection == _lens).firstOrNull ?? cameras.first;
    final controller = CameraController(chosen, _resolution, enableAudio: false, imageFormatGroup: ImageFormatGroup.jpeg);
    await controller.initialize();
    _controller = controller;
  }

  @override
  Widget preview() {
    final controller = _controller;
    return controller == null ? const SizedBox.shrink() : CameraPreview(controller);
  }

  @override
  Future<Uint8List> takePhoto() async {
    final file = await _controller!.takePicture();
    final bytes = await file.readAsBytes();
    // O plugin grava num temporário: apaga já, a foto segue só em memória.
    try {
      await File(file.path).delete();
    } on FileSystemException {
      // Já não existe: nada a apagar.
    }
    return bytes;
  }

  @override
  Future<void> close() async {
    await _controller?.dispose();
    _controller = null;
  }
}
