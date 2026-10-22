import 'package:flutter/material.dart';

import '../../../l10n/l10n.dart';

/// Campo de senha com o botão de mostrar/ocultar (estado só do campo).
class PasswordField extends StatefulWidget {
  const PasswordField({super.key, required this.controller, required this.onSubmitted});

  final TextEditingController controller;
  final VoidCallback onSubmitted;

  @override
  State<PasswordField> createState() => _PasswordFieldState();
}

class _PasswordFieldState extends State<PasswordField> {
  bool _visible = false;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return TextFormField(
      controller: widget.controller,
      obscureText: !_visible,
      decoration: InputDecoration(
        labelText: l10n.passwordLabel,
        suffixIcon: IconButton(
          tooltip: _visible ? l10n.hidePassword : l10n.showPassword,
          icon: Icon(_visible ? Icons.visibility_off : Icons.visibility),
          onPressed: () => setState(() => _visible = !_visible),
        ),
      ),
      textInputAction: TextInputAction.done,
      autofillHints: const [AutofillHints.password],
      onFieldSubmitted: (_) => widget.onSubmitted(),
      validator: (v) => (v ?? '').isEmpty ? l10n.passwordRequired : null,
    );
  }
}
