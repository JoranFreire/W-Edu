import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_error.dart';
import '../../../l10n/l10n.dart';
import '../auth_providers.dart';
import '../widgets/face_sign_in_button.dart';
import '../widgets/login_header.dart';
import '../widgets/password_field.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _form = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();

  // Estado só desta tela: fica em setState, não num provider.
  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    if (!_form.currentState!.validate()) return;
    final l10n = context.l10n;
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      await ref.read(authProvider.notifier).signIn(_email.text, _password.text);
      // Deu certo: o router percebe a sessão e sai desta tela sozinho.
    } catch (e) {
      if (mounted) setState(() => _error = apiErrorMessage(e, l10n, fallback: l10n.signInError));
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 400),
              child: Form(
                key: _form,
                child: AutofillGroup(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const LoginHeader(),
                      const SizedBox(height: 32),
                      _emailField(l10n),
                      const SizedBox(height: 16),
                      PasswordField(controller: _password, onSubmitted: _signIn),
                      if (_error != null) ...[const SizedBox(height: 16), Text(_error!, style: TextStyle(color: theme.colorScheme.error))],
                      const SizedBox(height: 24),
                      FilledButton(
                        onPressed: _submitting ? null : _signIn,
                        child: _submitting
                            ? const SizedBox.square(dimension: 20, child: CircularProgressIndicator(strokeWidth: 2))
                            : Text(l10n.signIn),
                      ),
                      const FaceSignInButton(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _emailField(AppLocalizations l10n) => TextFormField(
        controller: _email,
        decoration: InputDecoration(labelText: l10n.emailLabel),
        keyboardType: TextInputType.emailAddress,
        textInputAction: TextInputAction.next,
        autofillHints: const [AutofillHints.email],
        autocorrect: false,
        validator: (v) => (v ?? '').contains('@') ? null : l10n.emailRequired,
      );
}
