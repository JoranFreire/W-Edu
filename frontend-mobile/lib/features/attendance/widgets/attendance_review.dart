import 'package:flutter/material.dart';

import '../attendance_providers.dart';
import '../data/attendance_result.dart';
import 'persona_image.dart';

/// Revisão antes de gravar: reconhecidos já marcados; os "para conferir" mostram o rosto achado ao
/// lado da foto do cadastro; os sem autorização o professor marca à mão.
class RevisaoChamada extends StatelessWidget {
  const RevisaoChamada({super.key, required this.etapa, required this.onAlternar, required this.onConfirmar});

  final Revisando etapa;
  final void Function(String pessoaId) onAlternar;
  final VoidCallback onConfirmar;

  static const _titulos = {
    SituacaoNaFoto.presente: 'Reconhecidos',
    SituacaoNaFoto.conferir: 'Conferir',
    SituacaoNaFoto.ausente: 'Não encontrados nas fotos',
    SituacaoNaFoto.semAutorizacao: 'Sem reconhecimento autorizado (marque à mão)',
  };

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final resultado = etapa.resultado;
    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(vertical: 8),
            children: [
              for (final situacao in SituacaoNaFoto.values)
                if (resultado.de(situacao).isNotEmpty) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
                    child: Text('${_titulos[situacao]} (${resultado.de(situacao).length})', style: tema.textTheme.titleSmall),
                  ),
                  for (final aluno in resultado.de(situacao))
                    CheckboxListTile(
                      value: etapa.presentes.contains(aluno.pessoaId),
                      onChanged: (_) => onAlternar(aluno.pessoaId),
                      title: Text(aluno.nome),
                      subtitle: situacao == SituacaoNaFoto.conferir
                          ? Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Row(children: [
                                ImagemDoPersona(caminho: aluno.recorte, legenda: 'Na foto'),
                                const SizedBox(width: 12),
                                ImagemDoPersona(caminho: aluno.fotoCadastro, legenda: 'Cadastro'),
                              ]),
                            )
                          : null,
                    ),
                ],
            ],
          ),
        ),
        SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: onConfirmar,
                child: Text('Confirmar chamada: ${etapa.presentes.length} presente(s) de ${resultado.alunos.length}'),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
