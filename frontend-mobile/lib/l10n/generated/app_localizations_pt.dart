// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Portuguese (`pt`).
class AppLocalizationsPt extends AppLocalizations {
  AppLocalizationsPt([String locale = 'pt']) : super(locale);

  @override
  String get agendaTitle => 'Agenda escolar';

  @override
  String get agendaEmpty => 'Nada na agenda por enquanto.';

  @override
  String get agendaKindHomework => 'Tarefa';

  @override
  String get agendaKindTest => 'Prova';

  @override
  String get agendaKindEvent => 'Evento';

  @override
  String get agendaKindNotice => 'Aviso';

  @override
  String get attendanceTitle => 'Chamada facial';

  @override
  String get attendanceNoClasses => 'Nenhuma turma para você.';

  @override
  String get attendanceChooseMeeting => 'Escolha o encontro';

  @override
  String get attendanceNoMeetings => 'Nenhum encontro aberto nesta turma.';

  @override
  String get attendanceOpening => 'Abrindo a chamada…';

  @override
  String get attendanceAnalyzing => 'Analisando as fotos…';

  @override
  String get attendanceSaving => 'Gravando a chamada…';

  @override
  String get attendanceOffline =>
      'Sem internet agora. Você pode fotografar a sala: as fotos ficam guardadas (cifradas) no aparelho e a chamada é analisada quando a rede voltar.';

  @override
  String get attendancePhotographLater => 'Fotografar e enviar depois';

  @override
  String attendancePhotosSaved(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count fotos guardadas', one: '1 foto guardada');
    return '$_temp0. Quando a internet voltar, abra a Chamada facial para enviar e revisar.';
  }

  @override
  String attendanceConfirmed(int present, int total) {
    return 'Chamada registrada: $present presente(s) de $total.';
  }

  @override
  String get attendanceBackToMeetings => 'Voltar aos encontros';

  @override
  String get attendanceNotTeaching => 'Você não ministra esta turma.';

  @override
  String get attendanceOpenFailed => 'Não foi possível abrir a chamada.';

  @override
  String get attendanceCameraUnavailable => 'Não foi possível abrir a câmera.';

  @override
  String get attendanceNotPending => 'Esta chamada não está mais guardada no aparelho.';

  @override
  String get attendanceStillOffline => 'Ainda sem internet: as fotos continuam guardadas para enviar depois.';

  @override
  String get attendanceStillProcessing => 'As fotos ainda estão sendo analisadas. Tente de novo em instantes.';

  @override
  String get attendanceAnalysisFailed => 'Não foi possível analisar as fotos.';

  @override
  String get attendancePhotoFailed => 'Não foi possível enviar a foto.';

  @override
  String get attendanceConfirmFailed => 'Não foi possível gravar a chamada.';

  @override
  String get angleLeft => 'Lado esquerdo';

  @override
  String get angleCenter => 'Centro';

  @override
  String get angleRight => 'Lado direito';

  @override
  String get attendanceOfflineHint => 'Sem internet: as fotos ficam guardadas (cifradas) e a chamada é analisada quando a rede voltar.';

  @override
  String attendanceWithConsent(int count) {
    return '$count aluno(s) com reconhecimento autorizado';
  }

  @override
  String attendanceWithoutConsent(int count) {
    return ' · $count sem (você marca na revisão)';
  }

  @override
  String attendanceAnalyze(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count fotos', one: '1 foto');
    return 'Analisar $_temp0';
  }

  @override
  String attendanceStore(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count fotos', one: '1 foto');
    return 'Guardar $_temp0';
  }

  @override
  String get outcomePresent => 'Reconhecidos';

  @override
  String get outcomeUncertain => 'Conferir';

  @override
  String get outcomeAbsent => 'Não encontrados nas fotos';

  @override
  String get outcomeWithoutConsent => 'Sem reconhecimento autorizado (marque à mão)';

  @override
  String outcomeSection(String title, int count) {
    return '$title ($count)';
  }

  @override
  String get inThePhoto => 'Na foto';

  @override
  String attendanceConfirm(int present, int total) {
    return 'Confirmar chamada: $present presente(s) de $total';
  }

  @override
  String get pendingDiscardTitle => 'Descartar esta chamada?';

  @override
  String pendingDiscardBody(String title) {
    return 'As fotos de $title serão apagadas do aparelho, sem enviar.';
  }

  @override
  String get discard => 'Descartar';

  @override
  String pendingStored(int count) {
    return 'Chamadas guardadas no aparelho ($count)';
  }

  @override
  String get sendNow => 'Enviar agora';

  @override
  String pendingSummary(int count, String date, String state) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count fotos', one: '1 foto');
    return '$_temp0 · $date · $state';
  }

  @override
  String get pendingReady => 'pronta para revisar';

  @override
  String get pendingWaiting => 'aguardando internet';

  @override
  String get enrollmentPhoto => 'Cadastro';

  @override
  String get signInWithAnotherAccount => 'Entrar com outra conta';

  @override
  String get loginSubtitle => 'Entre com a conta da sua instituição';

  @override
  String get emailLabel => 'E-mail';

  @override
  String get emailRequired => 'Informe o e-mail.';

  @override
  String get passwordLabel => 'Senha';

  @override
  String get passwordRequired => 'Informe a senha.';

  @override
  String get showPassword => 'Mostrar senha';

  @override
  String get hidePassword => 'Esconder senha';

  @override
  String get signIn => 'Entrar';

  @override
  String get signInError => 'Não foi possível entrar.';

  @override
  String faceSignInAs(String name) {
    return 'Entrar com o rosto como $name';
  }

  @override
  String notYouUseAnotherAccount(String name) {
    return 'Não é $name? Usar outra conta';
  }

  @override
  String get faceLoginTitle => 'Entrar com o rosto';

  @override
  String faceLoginHello(String name) {
    return 'Olá, $name';
  }

  @override
  String get faceLoginIntro => 'Vamos conferir que é você.\nVocê vai olhar para a câmera e virar o rosto para os dois lados.';

  @override
  String get faceChecking => 'Conferindo…';

  @override
  String get signInWithPassword => 'Entrar com a senha';

  @override
  String get faceLoginUnavailable => 'Entrar com o rosto não está disponível. Use a senha.';

  @override
  String get faceLoginCameraUnavailable => 'Não foi possível abrir a câmera. Confira a permissão ou use a senha.';

  @override
  String get faceLoginRefused => 'Não foi possível entrar com o rosto. Use a senha.';

  @override
  String get benefitsTitle => 'Benefícios';

  @override
  String get benefitsEmpty => 'Nenhum benefício liberado.';

  @override
  String get benefitStatusReleased => 'Liberado';

  @override
  String get benefitStatusRedeemed => 'Retirado';

  @override
  String get benefitStatusCancelled => 'Cancelado';

  @override
  String get benefitStatusExpired => 'Vencido';

  @override
  String get benefitKindSnack => 'Lanche';

  @override
  String get benefitKindMaterial => 'Material';

  @override
  String get benefitKindUniform => 'Uniforme';

  @override
  String get benefitKindTransport => 'Transporte';

  @override
  String get benefitKindStipend => 'Auxílio financeiro';

  @override
  String get benefitKindOther => 'Outro';

  @override
  String benefitRedeemedOn(String date) {
    return 'Retirado em $date';
  }

  @override
  String benefitPickUpBy(String date) {
    return 'Retire até $date';
  }

  @override
  String benefitReleasedOn(String date) {
    return 'Liberado em $date';
  }

  @override
  String get showQr => 'Mostrar QR';

  @override
  String get benefitNoExpiry => 'Sem data de validade';

  @override
  String benefitValidUntil(String date) {
    return 'Válido até $date';
  }

  @override
  String benefitQrFooter(String validity) {
    return '$validity\nMostre este QR na retirada.';
  }

  @override
  String get purposeLogin => 'Entrar no app com o rosto';

  @override
  String get purposeLoginHint => 'Usar o rosto em vez da senha ao abrir o app.';

  @override
  String get purposeAccess => 'Catraca';

  @override
  String get purposeAccessHint => 'Passar pela catraca da instituição com o rosto (o responsável recebe um aviso).';

  @override
  String get purposeAttendance => 'Presença em aula';

  @override
  String get purposeAttendanceHint => 'O professor registra a chamada com uma foto da sala. Só para maiores de 18 anos.';

  @override
  String get personaAdultOnly =>
      'A presença por reconhecimento facial é só para maiores de 18 anos. Se a data de nascimento estiver errada, fale com a secretaria.';

  @override
  String get personaGuardianConsents =>
      'Até os 16 anos, quem autoriza é o responsável. Se a data de nascimento estiver errada, fale com a secretaria.';

  @override
  String get personaSubjectDecidesAlone => 'A partir de 16 anos, o próprio aluno autoriza pelo app.';

  @override
  String get personaSubjectIsAdult => 'O aluno é maior de idade: ele mesmo autoriza pelo app.';

  @override
  String get personaGuardianPurposeNotAllowed => 'O responsável autoriza só o login e a catraca.';

  @override
  String get personaTermsOutdated => 'O termo foi atualizado. Leia a nova versão e autorize de novo.';

  @override
  String get personaInstitutionRequired => 'Entre de novo no app e tente outra vez.';

  @override
  String get personaNoActiveConsent => 'Autorize pelo menos um uso do rosto antes de cadastrá-lo.';

  @override
  String get personaChallengeInvalid => 'O tempo da conferência acabou. Tente de novo.';

  @override
  String get personaFaceNotChecked => 'Não deu para conferir o rosto (luz, enquadramento ou movimentos). Tente de novo.';

  @override
  String get biometricsTitle => 'Reconhecimento facial';

  @override
  String get biometricsIntro =>
      'Cada uso é autorizado separadamente e pode ser revogado quando quiser. A senha (e a portaria, na catraca) continua valendo sempre.';

  @override
  String get enrollmentTitle => 'Cadastrar o rosto';

  @override
  String get enrollmentIntro =>
      'Em um lugar bem iluminado, olhe para a câmera e vire o rosto para os dois lados quando pedir. As fotos vão só para a conferência e não ficam no aparelho.';

  @override
  String get enrollmentDone => 'Rosto cadastrado.';

  @override
  String get finish => 'Concluir';

  @override
  String get enrollmentUnavailable => 'O reconhecimento facial não está disponível.';

  @override
  String get enrollmentCameraUnavailable => 'Não foi possível abrir a câmera. Confira a permissão do app.';

  @override
  String get enrollmentError => 'Não foi possível cadastrar o rosto.';

  @override
  String get faceEnrolled => 'Seu rosto está cadastrado.';

  @override
  String get faceEnrollmentMissing => 'Falta cadastrar o rosto para usar o que foi autorizado.';

  @override
  String get faceEnrollmentNeedsConsent => 'Autorize pelo menos um uso abaixo para cadastrar o rosto.';

  @override
  String get reenrollFace => 'Refazer o cadastro do rosto';

  @override
  String get enrollMyFace => 'Cadastrar meu rosto';

  @override
  String get consentAdultsOnly => 'Só para maiores de 18 anos.';

  @override
  String get consentGuardianDecides => 'Até os 16 anos, quem autoriza é o seu responsável, pelo app dele.';

  @override
  String consentGranted(String purpose) {
    return '$purpose: autorizado.';
  }

  @override
  String consentRevoked(String purpose) {
    return '$purpose: revogado.';
  }

  @override
  String get dependentDecidesAlone => 'A partir de 16 anos, o próprio aluno autoriza o uso do rosto pelo app.';

  @override
  String dependentFaceEnrolled(String name) {
    return 'O rosto de $name está cadastrado.';
  }

  @override
  String dependentEnrollAfterConsent(String name) {
    return 'Depois de autorizar, $name cadastra o próprio rosto no app (Perfil → Reconhecimento facial).';
  }

  @override
  String termsOnBehalfOf(String name) {
    return 'Autorização em nome de $name';
  }

  @override
  String termsVersion(String version) {
    return 'Termo versão $version';
  }

  @override
  String get termsAgree => 'Li e concordo';

  @override
  String get notNow => 'Agora não';

  @override
  String revokeTitle(String purpose) {
    return 'Revogar: $purpose?';
  }

  @override
  String get revokeBody => 'O rosto deixa de ser usado para isso agora. Se nenhum uso continuar autorizado, o cadastro do rosto é apagado.';

  @override
  String get revoke => 'Revogar';

  @override
  String get dependentsTitle => 'Meus dependentes';

  @override
  String get dependentsEmpty => 'Nenhum aluno vinculado à sua conta. Procure a secretaria.';

  @override
  String get dependentFallbackName => 'Dependente';

  @override
  String get dependentTabFace => 'Rosto';

  @override
  String get dependentTabBenefits => 'Benefícios';

  @override
  String get financialBadge => 'Financeiro';

  @override
  String get relationshipMother => 'Mãe';

  @override
  String get relationshipFather => 'Pai';

  @override
  String get relationshipLegalGuardian => 'Responsável legal';

  @override
  String get relationshipGrandparent => 'Avó/avô';

  @override
  String get relationshipOther => 'Responsável';

  @override
  String get tabHome => 'Início';

  @override
  String get tabNotices => 'Avisos';

  @override
  String get tabAgenda => 'Agenda';

  @override
  String get tabReportCard => 'Boletim';

  @override
  String get tabDependents => 'Dependentes';

  @override
  String get tabProfile => 'Perfil';

  @override
  String homeGreeting(String name) {
    return 'Olá, $name!';
  }

  @override
  String get homeAllRead => 'Tudo lido';

  @override
  String homeUnread(int count) {
    return '$count sem ler';
  }

  @override
  String get homeTapToSee => 'Toque para ver';

  @override
  String get homeNextOnAgenda => 'Próximo na agenda';

  @override
  String get homeNothingAhead => 'Nada pela frente';

  @override
  String homeNextItem(String title, String date) {
    return '$title · $date';
  }

  @override
  String get homeFaceAttendance => 'Chamada facial';

  @override
  String get homeAttendanceHint => 'Fotografe a sala e revise';

  @override
  String homeAttendancePending(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count chamadas guardadas no aparelho',
      one: '1 chamada guardada no aparelho',
    );
    return '$_temp0';
  }

  @override
  String get homeNothingToPickUp => 'Nada para retirar';

  @override
  String homeToPickUp(int count) {
    return '$count para retirar';
  }

  @override
  String get homeNoDependents => 'Nenhum vinculado';

  @override
  String get materialsTitle => 'Requisições de material';

  @override
  String get materialsEmpty => 'Nenhuma requisição. Peça materiais pelo site.';

  @override
  String get materialStatusPending => 'Aguardando aprovação';

  @override
  String get materialStatusApproved => 'Aprovada: retirar';

  @override
  String get materialStatusRejected => 'Recusada';

  @override
  String get materialStatusDelivered => 'Retirada';

  @override
  String get materialStatusClosed => 'Concluída';

  @override
  String get materialStatusCancelled => 'Cancelada';

  @override
  String get materialReturnOverdue => 'Devolução atrasada';

  @override
  String materialNeededOn(String date) {
    return 'Para $date';
  }

  @override
  String materialReturnBy(String date) {
    return 'devolver até $date';
  }

  @override
  String materialLine(String material, int quantity, String unit) {
    return '$material: $quantity $unit';
  }

  @override
  String materialLineToReturn(String line, int count) {
    return '$line · devolver $count';
  }

  @override
  String get pickupQr => 'QR de retirada';

  @override
  String get materialQrFooter => 'Mostre este QR no almoxarifado. Só você recebe este código.';

  @override
  String get noticesTitle => 'Avisos';

  @override
  String get markAllAsRead => 'Marcar todos como lidos';

  @override
  String get noNotices => 'Nenhum aviso por enquanto.';

  @override
  String get profileTitle => 'Perfil';

  @override
  String get profileEmail => 'E-mail';

  @override
  String profileRole(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: 'Papéis', one: 'Papel');
    return '$_temp0';
  }

  @override
  String get profileInstitution => 'Instituição';

  @override
  String get profileFaceRecognition => 'Reconhecimento facial';

  @override
  String get profileFaceRecognitionHint => 'Entrar com o rosto, catraca e presença: autorizações e cadastro do rosto';

  @override
  String get signOut => 'Sair';

  @override
  String get signOutTitle => 'Sair da conta?';

  @override
  String get signOutBody => 'Você vai precisar entrar de novo com e-mail e senha.';

  @override
  String signOutPendingAttendance(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: 'Há $count chamadas com fotos ainda não enviadas: elas serão apagadas do aparelho.',
      one: 'Há 1 chamada com fotos ainda não enviadas: ela será apagada do aparelho.',
    );
    return '$_temp0';
  }

  @override
  String get roleStudent => 'Aluno';

  @override
  String get roleInstructor => 'Instrutor';

  @override
  String get roleCoordinator => 'Coordenação';

  @override
  String get roleSecretary => 'Secretaria';

  @override
  String get roleGuardian => 'Responsável';

  @override
  String get roleCompanyManager => 'Gestão empresa';

  @override
  String get roleInstitutionAdmin => 'Admin da instituição';

  @override
  String get roleAdmin => 'Admin';

  @override
  String get roleSuperAdmin => 'Admin da plataforma';

  @override
  String get reportCardTitle => 'Boletim';

  @override
  String get reportCardEmpty => 'Ainda não há notas publicadas.';

  @override
  String get reportCardNoPeriods => 'Nenhuma etapa fechada ainda.';

  @override
  String reportCardAbsences(int count) {
    String _temp0 = intl.Intl.pluralLogic(count, locale: localeName, other: '$count faltas', one: '1 falta');
    return '$_temp0';
  }

  @override
  String reportCardFinalGrade(String grade) {
    return 'Média final: $grade';
  }

  @override
  String reportCardRecovery(String grade) {
    return 'Recuperação: $grade';
  }

  @override
  String reportCardAttendance(String rate) {
    return 'Frequência: $rate';
  }

  @override
  String reportCardPassingGrade(String grade) {
    return 'Média para aprovar: $grade';
  }

  @override
  String get subjectInProgress => 'Cursando';

  @override
  String get subjectRecovery => 'Em recuperação';

  @override
  String get subjectApproved => 'Aprovado';

  @override
  String get subjectFailed => 'Reprovado';

  @override
  String get subjectFailedAttendance => 'Reprovado por falta';

  @override
  String get appTitle => 'W-Edu';

  @override
  String get errorGeneric => 'Não foi possível concluir.';

  @override
  String get errorNoConnection => 'Sem conexão com o servidor. Verifique a internet.';

  @override
  String get errorTimeout => 'O servidor demorou a responder.';

  @override
  String get tryAgain => 'Tentar de novo';

  @override
  String get back => 'Voltar';

  @override
  String get cancel => 'Cancelar';

  @override
  String get keep => 'Manter';

  @override
  String get close => 'Fechar';

  @override
  String get errorLoad => 'Não foi possível carregar.';

  @override
  String get errorRefresh => 'Não foi possível atualizar.';

  @override
  String get faceStepCenter => 'Olhe para a câmera';

  @override
  String get faceStepTurnLeft => 'Vire o rosto para a esquerda';

  @override
  String get faceStepTurnRight => 'Vire o rosto para a direita';

  @override
  String faceStepProgress(int current, int total) {
    return 'Passo $current de $total';
  }

  @override
  String qrSemanticLabel(String title) {
    return 'QR de $title';
  }

  @override
  String get openingCamera => 'Abrindo a câmera…';

  @override
  String get start => 'Começar';
}
