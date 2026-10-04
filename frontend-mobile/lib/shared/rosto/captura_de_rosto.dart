import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/widgets.dart';

/// Uma câmera do aparelho, atrás de uma interface: os testes usam uma falsa.
abstract interface class CapturaDeRosto {
  /// Abre a câmera frontal; falha se não houver câmera ou permissão.
  Future<void> abrir();

  /// O que a câmera está vendo (para a pessoa se posicionar).
  Widget visor();

  /// Uma foto JPEG, só em memória (não é gravada no aparelho depois do envio).
  Future<Uint8List> fotografar();

  Future<void> fechar();
}

/// Câmera frontal (login e cadastro do rosto): resolução média, rosto nítido e foto bem
/// abaixo do limite de 4 MB do Persona.
class CameraFrontal extends CameraDoAparelho {
  CameraFrontal() : super(CameraLensDirection.front, ResolutionPreset.medium);
}

/// Câmera traseira (foto da sala na chamada facial): resolução alta, rostos pequenos ao fundo.
class CameraTraseira extends CameraDoAparelho {
  CameraTraseira() : super(CameraLensDirection.back, ResolutionPreset.high);
}

class CameraDoAparelho implements CapturaDeRosto {
  CameraDoAparelho(this._lente, this._resolucao);

  final CameraLensDirection _lente;
  final ResolutionPreset _resolucao;
  CameraController? _controle;

  @override
  Future<void> abrir() async {
    final cameras = await availableCameras();
    final escolhida = cameras.where((c) => c.lensDirection == _lente).firstOrNull ?? cameras.first;
    final controle = CameraController(escolhida, _resolucao, enableAudio: false, imageFormatGroup: ImageFormatGroup.jpeg);
    await controle.initialize();
    _controle = controle;
  }

  @override
  Widget visor() {
    final controle = _controle;
    return controle == null ? const SizedBox.shrink() : CameraPreview(controle);
  }

  @override
  Future<Uint8List> fotografar() async {
    final arquivo = await _controle!.takePicture();
    final bytes = await arquivo.readAsBytes();
    // O plugin grava num temporário: apaga já, a foto segue só em memória.
    try {
      await File(arquivo.path).delete();
    } on FileSystemException {
      // Já não existe: nada a apagar.
    }
    return bytes;
  }

  @override
  Future<void> fechar() async {
    await _controle?.dispose();
    _controle = null;
  }
}
