import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_pt.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale) : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[Locale('en'), Locale('pt')];

  /// No description provided for @agendaTitle.
  ///
  /// In pt, this message translates to:
  /// **'Agenda escolar'**
  String get agendaTitle;

  /// No description provided for @agendaEmpty.
  ///
  /// In pt, this message translates to:
  /// **'Nada na agenda por enquanto.'**
  String get agendaEmpty;

  /// No description provided for @agendaKindHomework.
  ///
  /// In pt, this message translates to:
  /// **'Tarefa'**
  String get agendaKindHomework;

  /// No description provided for @agendaKindTest.
  ///
  /// In pt, this message translates to:
  /// **'Prova'**
  String get agendaKindTest;

  /// No description provided for @agendaKindEvent.
  ///
  /// In pt, this message translates to:
  /// **'Evento'**
  String get agendaKindEvent;

  /// No description provided for @agendaKindNotice.
  ///
  /// In pt, this message translates to:
  /// **'Aviso'**
  String get agendaKindNotice;

  /// No description provided for @attendanceTitle.
  ///
  /// In pt, this message translates to:
  /// **'Chamada facial'**
  String get attendanceTitle;

  /// No description provided for @attendanceNoClasses.
  ///
  /// In pt, this message translates to:
  /// **'Nenhuma turma para você.'**
  String get attendanceNoClasses;

  /// No description provided for @attendanceChooseMeeting.
  ///
  /// In pt, this message translates to:
  /// **'Escolha o encontro'**
  String get attendanceChooseMeeting;

  /// No description provided for @attendanceNoMeetings.
  ///
  /// In pt, this message translates to:
  /// **'Nenhum encontro aberto nesta turma.'**
  String get attendanceNoMeetings;

  /// No description provided for @attendanceOpening.
  ///
  /// In pt, this message translates to:
  /// **'Abrindo a chamada…'**
  String get attendanceOpening;

  /// No description provided for @attendanceAnalyzing.
  ///
  /// In pt, this message translates to:
  /// **'Analisando as fotos…'**
  String get attendanceAnalyzing;

  /// No description provided for @attendanceSaving.
  ///
  /// In pt, this message translates to:
  /// **'Gravando a chamada…'**
  String get attendanceSaving;

  /// No description provided for @attendanceOffline.
  ///
  /// In pt, this message translates to:
  /// **'Sem internet agora. Você pode fotografar a sala: as fotos ficam guardadas (cifradas) no aparelho e a chamada é analisada quando a rede voltar.'**
  String get attendanceOffline;

  /// No description provided for @attendancePhotographLater.
  ///
  /// In pt, this message translates to:
  /// **'Fotografar e enviar depois'**
  String get attendancePhotographLater;

  /// No description provided for @attendancePhotosSaved.
  ///
  /// In pt, this message translates to:
  /// **'{count, plural, =1{1 foto guardada} other{{count} fotos guardadas}}. Quando a internet voltar, abra a Chamada facial para enviar e revisar.'**
  String attendancePhotosSaved(int count);

  /// No description provided for @attendanceConfirmed.
  ///
  /// In pt, this message translates to:
  /// **'Chamada registrada: {present} presente(s) de {total}.'**
  String attendanceConfirmed(int present, int total);

  /// No description provided for @attendanceBackToMeetings.
  ///
  /// In pt, this message translates to:
  /// **'Voltar aos encontros'**
  String get attendanceBackToMeetings;

  /// No description provided for @attendanceNotTeaching.
  ///
  /// In pt, this message translates to:
  /// **'Você não ministra esta turma.'**
  String get attendanceNotTeaching;

  /// No description provided for @attendanceOpenFailed.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível abrir a chamada.'**
  String get attendanceOpenFailed;

  /// No description provided for @attendanceCameraUnavailable.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível abrir a câmera.'**
  String get attendanceCameraUnavailable;

  /// No description provided for @attendanceNotPending.
  ///
  /// In pt, this message translates to:
  /// **'Esta chamada não está mais guardada no aparelho.'**
  String get attendanceNotPending;

  /// No description provided for @attendanceStillOffline.
  ///
  /// In pt, this message translates to:
  /// **'Ainda sem internet: as fotos continuam guardadas para enviar depois.'**
  String get attendanceStillOffline;

  /// No description provided for @attendanceStillProcessing.
  ///
  /// In pt, this message translates to:
  /// **'As fotos ainda estão sendo analisadas. Tente de novo em instantes.'**
  String get attendanceStillProcessing;

  /// No description provided for @attendanceAnalysisFailed.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível analisar as fotos.'**
  String get attendanceAnalysisFailed;

  /// No description provided for @attendancePhotoFailed.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível enviar a foto.'**
  String get attendancePhotoFailed;

  /// No description provided for @attendanceConfirmFailed.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível gravar a chamada.'**
  String get attendanceConfirmFailed;

  /// No description provided for @angleLeft.
  ///
  /// In pt, this message translates to:
  /// **'Lado esquerdo'**
  String get angleLeft;

  /// No description provided for @angleCenter.
  ///
  /// In pt, this message translates to:
  /// **'Centro'**
  String get angleCenter;

  /// No description provided for @angleRight.
  ///
  /// In pt, this message translates to:
  /// **'Lado direito'**
  String get angleRight;

  /// No description provided for @attendanceOfflineHint.
  ///
  /// In pt, this message translates to:
  /// **'Sem internet: as fotos ficam guardadas (cifradas) e a chamada é analisada quando a rede voltar.'**
  String get attendanceOfflineHint;

  /// No description provided for @attendanceWithConsent.
  ///
  /// In pt, this message translates to:
  /// **'{count} aluno(s) com reconhecimento autorizado'**
  String attendanceWithConsent(int count);

  /// No description provided for @attendanceWithoutConsent.
  ///
  /// In pt, this message translates to:
  /// **' · {count} sem (você marca na revisão)'**
  String attendanceWithoutConsent(int count);

  /// No description provided for @attendanceAnalyze.
  ///
  /// In pt, this message translates to:
  /// **'Analisar {count, plural, =1{1 foto} other{{count} fotos}}'**
  String attendanceAnalyze(int count);

  /// No description provided for @attendanceStore.
  ///
  /// In pt, this message translates to:
  /// **'Guardar {count, plural, =1{1 foto} other{{count} fotos}}'**
  String attendanceStore(int count);

  /// No description provided for @outcomePresent.
  ///
  /// In pt, this message translates to:
  /// **'Reconhecidos'**
  String get outcomePresent;

  /// No description provided for @outcomeUncertain.
  ///
  /// In pt, this message translates to:
  /// **'Conferir'**
  String get outcomeUncertain;

  /// No description provided for @outcomeAbsent.
  ///
  /// In pt, this message translates to:
  /// **'Não encontrados nas fotos'**
  String get outcomeAbsent;

  /// No description provided for @outcomeWithoutConsent.
  ///
  /// In pt, this message translates to:
  /// **'Sem reconhecimento autorizado (marque à mão)'**
  String get outcomeWithoutConsent;

  /// No description provided for @outcomeSection.
  ///
  /// In pt, this message translates to:
  /// **'{title} ({count})'**
  String outcomeSection(String title, int count);

  /// No description provided for @inThePhoto.
  ///
  /// In pt, this message translates to:
  /// **'Na foto'**
  String get inThePhoto;

  /// No description provided for @attendanceConfirm.
  ///
  /// In pt, this message translates to:
  /// **'Confirmar chamada: {present} presente(s) de {total}'**
  String attendanceConfirm(int present, int total);

  /// No description provided for @pendingDiscardTitle.
  ///
  /// In pt, this message translates to:
  /// **'Descartar esta chamada?'**
  String get pendingDiscardTitle;

  /// No description provided for @pendingDiscardBody.
  ///
  /// In pt, this message translates to:
  /// **'As fotos de {title} serão apagadas do aparelho, sem enviar.'**
  String pendingDiscardBody(String title);

  /// No description provided for @discard.
  ///
  /// In pt, this message translates to:
  /// **'Descartar'**
  String get discard;

  /// No description provided for @pendingStored.
  ///
  /// In pt, this message translates to:
  /// **'Chamadas guardadas no aparelho ({count})'**
  String pendingStored(int count);

  /// No description provided for @sendNow.
  ///
  /// In pt, this message translates to:
  /// **'Enviar agora'**
  String get sendNow;

  /// No description provided for @pendingSummary.
  ///
  /// In pt, this message translates to:
  /// **'{count, plural, =1{1 foto} other{{count} fotos}} · {date} · {state}'**
  String pendingSummary(int count, String date, String state);

  /// No description provided for @pendingReady.
  ///
  /// In pt, this message translates to:
  /// **'pronta para revisar'**
  String get pendingReady;

  /// No description provided for @pendingWaiting.
  ///
  /// In pt, this message translates to:
  /// **'aguardando internet'**
  String get pendingWaiting;

  /// No description provided for @enrollmentPhoto.
  ///
  /// In pt, this message translates to:
  /// **'Cadastro'**
  String get enrollmentPhoto;

  /// No description provided for @signInWithAnotherAccount.
  ///
  /// In pt, this message translates to:
  /// **'Entrar com outra conta'**
  String get signInWithAnotherAccount;

  /// No description provided for @loginSubtitle.
  ///
  /// In pt, this message translates to:
  /// **'Entre com a conta da sua instituição'**
  String get loginSubtitle;

  /// No description provided for @emailLabel.
  ///
  /// In pt, this message translates to:
  /// **'E-mail'**
  String get emailLabel;

  /// No description provided for @emailRequired.
  ///
  /// In pt, this message translates to:
  /// **'Informe o e-mail.'**
  String get emailRequired;

  /// No description provided for @passwordLabel.
  ///
  /// In pt, this message translates to:
  /// **'Senha'**
  String get passwordLabel;

  /// No description provided for @passwordRequired.
  ///
  /// In pt, this message translates to:
  /// **'Informe a senha.'**
  String get passwordRequired;

  /// No description provided for @showPassword.
  ///
  /// In pt, this message translates to:
  /// **'Mostrar senha'**
  String get showPassword;

  /// No description provided for @hidePassword.
  ///
  /// In pt, this message translates to:
  /// **'Esconder senha'**
  String get hidePassword;

  /// No description provided for @signIn.
  ///
  /// In pt, this message translates to:
  /// **'Entrar'**
  String get signIn;

  /// No description provided for @signInError.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível entrar.'**
  String get signInError;

  /// No description provided for @faceSignInAs.
  ///
  /// In pt, this message translates to:
  /// **'Entrar com o rosto como {name}'**
  String faceSignInAs(String name);

  /// No description provided for @notYouUseAnotherAccount.
  ///
  /// In pt, this message translates to:
  /// **'Não é {name}? Usar outra conta'**
  String notYouUseAnotherAccount(String name);

  /// No description provided for @faceLoginTitle.
  ///
  /// In pt, this message translates to:
  /// **'Entrar com o rosto'**
  String get faceLoginTitle;

  /// No description provided for @faceLoginHello.
  ///
  /// In pt, this message translates to:
  /// **'Olá, {name}'**
  String faceLoginHello(String name);

  /// No description provided for @faceLoginIntro.
  ///
  /// In pt, this message translates to:
  /// **'Vamos conferir que é você.\nVocê vai olhar para a câmera e virar o rosto para os dois lados.'**
  String get faceLoginIntro;

  /// No description provided for @faceChecking.
  ///
  /// In pt, this message translates to:
  /// **'Conferindo…'**
  String get faceChecking;

  /// No description provided for @signInWithPassword.
  ///
  /// In pt, this message translates to:
  /// **'Entrar com a senha'**
  String get signInWithPassword;

  /// No description provided for @faceLoginUnavailable.
  ///
  /// In pt, this message translates to:
  /// **'Entrar com o rosto não está disponível. Use a senha.'**
  String get faceLoginUnavailable;

  /// No description provided for @faceLoginCameraUnavailable.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível abrir a câmera. Confira a permissão ou use a senha.'**
  String get faceLoginCameraUnavailable;

  /// No description provided for @faceLoginRefused.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível entrar com o rosto. Use a senha.'**
  String get faceLoginRefused;

  /// No description provided for @benefitsTitle.
  ///
  /// In pt, this message translates to:
  /// **'Benefícios'**
  String get benefitsTitle;

  /// No description provided for @benefitsEmpty.
  ///
  /// In pt, this message translates to:
  /// **'Nenhum benefício liberado.'**
  String get benefitsEmpty;

  /// No description provided for @benefitStatusReleased.
  ///
  /// In pt, this message translates to:
  /// **'Liberado'**
  String get benefitStatusReleased;

  /// No description provided for @benefitStatusRedeemed.
  ///
  /// In pt, this message translates to:
  /// **'Retirado'**
  String get benefitStatusRedeemed;

  /// No description provided for @benefitStatusCancelled.
  ///
  /// In pt, this message translates to:
  /// **'Cancelado'**
  String get benefitStatusCancelled;

  /// No description provided for @benefitStatusExpired.
  ///
  /// In pt, this message translates to:
  /// **'Vencido'**
  String get benefitStatusExpired;

  /// No description provided for @benefitKindSnack.
  ///
  /// In pt, this message translates to:
  /// **'Lanche'**
  String get benefitKindSnack;

  /// No description provided for @benefitKindMaterial.
  ///
  /// In pt, this message translates to:
  /// **'Material'**
  String get benefitKindMaterial;

  /// No description provided for @benefitKindUniform.
  ///
  /// In pt, this message translates to:
  /// **'Uniforme'**
  String get benefitKindUniform;

  /// No description provided for @benefitKindTransport.
  ///
  /// In pt, this message translates to:
  /// **'Transporte'**
  String get benefitKindTransport;

  /// No description provided for @benefitKindStipend.
  ///
  /// In pt, this message translates to:
  /// **'Auxílio financeiro'**
  String get benefitKindStipend;

  /// No description provided for @benefitKindOther.
  ///
  /// In pt, this message translates to:
  /// **'Outro'**
  String get benefitKindOther;

  /// No description provided for @benefitRedeemedOn.
  ///
  /// In pt, this message translates to:
  /// **'Retirado em {date}'**
  String benefitRedeemedOn(String date);

  /// No description provided for @benefitPickUpBy.
  ///
  /// In pt, this message translates to:
  /// **'Retire até {date}'**
  String benefitPickUpBy(String date);

  /// No description provided for @benefitReleasedOn.
  ///
  /// In pt, this message translates to:
  /// **'Liberado em {date}'**
  String benefitReleasedOn(String date);

  /// No description provided for @showQr.
  ///
  /// In pt, this message translates to:
  /// **'Mostrar QR'**
  String get showQr;

  /// No description provided for @benefitNoExpiry.
  ///
  /// In pt, this message translates to:
  /// **'Sem data de validade'**
  String get benefitNoExpiry;

  /// No description provided for @benefitValidUntil.
  ///
  /// In pt, this message translates to:
  /// **'Válido até {date}'**
  String benefitValidUntil(String date);

  /// No description provided for @benefitQrFooter.
  ///
  /// In pt, this message translates to:
  /// **'{validity}\nMostre este QR na retirada.'**
  String benefitQrFooter(String validity);

  /// No description provided for @purposeLogin.
  ///
  /// In pt, this message translates to:
  /// **'Entrar no app com o rosto'**
  String get purposeLogin;

  /// No description provided for @purposeLoginHint.
  ///
  /// In pt, this message translates to:
  /// **'Usar o rosto em vez da senha ao abrir o app.'**
  String get purposeLoginHint;

  /// No description provided for @purposeAccess.
  ///
  /// In pt, this message translates to:
  /// **'Catraca'**
  String get purposeAccess;

  /// No description provided for @purposeAccessHint.
  ///
  /// In pt, this message translates to:
  /// **'Passar pela catraca da instituição com o rosto (o responsável recebe um aviso).'**
  String get purposeAccessHint;

  /// No description provided for @purposeAttendance.
  ///
  /// In pt, this message translates to:
  /// **'Presença em aula'**
  String get purposeAttendance;

  /// No description provided for @purposeAttendanceHint.
  ///
  /// In pt, this message translates to:
  /// **'O professor registra a chamada com uma foto da sala. Só para maiores de 18 anos.'**
  String get purposeAttendanceHint;

  /// No description provided for @personaAdultOnly.
  ///
  /// In pt, this message translates to:
  /// **'A presença por reconhecimento facial é só para maiores de 18 anos. Se a data de nascimento estiver errada, fale com a secretaria.'**
  String get personaAdultOnly;

  /// No description provided for @personaGuardianConsents.
  ///
  /// In pt, this message translates to:
  /// **'Até os 16 anos, quem autoriza é o responsável. Se a data de nascimento estiver errada, fale com a secretaria.'**
  String get personaGuardianConsents;

  /// No description provided for @personaSubjectDecidesAlone.
  ///
  /// In pt, this message translates to:
  /// **'A partir de 16 anos, o próprio aluno autoriza pelo app.'**
  String get personaSubjectDecidesAlone;

  /// No description provided for @personaSubjectIsAdult.
  ///
  /// In pt, this message translates to:
  /// **'O aluno é maior de idade: ele mesmo autoriza pelo app.'**
  String get personaSubjectIsAdult;

  /// No description provided for @personaGuardianPurposeNotAllowed.
  ///
  /// In pt, this message translates to:
  /// **'O responsável autoriza só o login e a catraca.'**
  String get personaGuardianPurposeNotAllowed;

  /// No description provided for @personaTermsOutdated.
  ///
  /// In pt, this message translates to:
  /// **'O termo foi atualizado. Leia a nova versão e autorize de novo.'**
  String get personaTermsOutdated;

  /// No description provided for @personaInstitutionRequired.
  ///
  /// In pt, this message translates to:
  /// **'Entre de novo no app e tente outra vez.'**
  String get personaInstitutionRequired;

  /// No description provided for @personaNoActiveConsent.
  ///
  /// In pt, this message translates to:
  /// **'Autorize pelo menos um uso do rosto antes de cadastrá-lo.'**
  String get personaNoActiveConsent;

  /// No description provided for @personaChallengeInvalid.
  ///
  /// In pt, this message translates to:
  /// **'O tempo da conferência acabou. Tente de novo.'**
  String get personaChallengeInvalid;

  /// No description provided for @personaFaceNotChecked.
  ///
  /// In pt, this message translates to:
  /// **'Não deu para conferir o rosto (luz, enquadramento ou movimentos). Tente de novo.'**
  String get personaFaceNotChecked;

  /// No description provided for @biometricsTitle.
  ///
  /// In pt, this message translates to:
  /// **'Reconhecimento facial'**
  String get biometricsTitle;

  /// No description provided for @biometricsIntro.
  ///
  /// In pt, this message translates to:
  /// **'Cada uso é autorizado separadamente e pode ser revogado quando quiser. A senha (e a portaria, na catraca) continua valendo sempre.'**
  String get biometricsIntro;

  /// No description provided for @enrollmentTitle.
  ///
  /// In pt, this message translates to:
  /// **'Cadastrar o rosto'**
  String get enrollmentTitle;

  /// No description provided for @enrollmentIntro.
  ///
  /// In pt, this message translates to:
  /// **'Em um lugar bem iluminado, olhe para a câmera e vire o rosto para os dois lados quando pedir. As fotos vão só para a conferência e não ficam no aparelho.'**
  String get enrollmentIntro;

  /// No description provided for @enrollmentDone.
  ///
  /// In pt, this message translates to:
  /// **'Rosto cadastrado.'**
  String get enrollmentDone;

  /// No description provided for @finish.
  ///
  /// In pt, this message translates to:
  /// **'Concluir'**
  String get finish;

  /// No description provided for @enrollmentUnavailable.
  ///
  /// In pt, this message translates to:
  /// **'O reconhecimento facial não está disponível.'**
  String get enrollmentUnavailable;

  /// No description provided for @enrollmentCameraUnavailable.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível abrir a câmera. Confira a permissão do app.'**
  String get enrollmentCameraUnavailable;

  /// No description provided for @enrollmentError.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível cadastrar o rosto.'**
  String get enrollmentError;

  /// No description provided for @faceEnrolled.
  ///
  /// In pt, this message translates to:
  /// **'Seu rosto está cadastrado.'**
  String get faceEnrolled;

  /// No description provided for @faceEnrollmentMissing.
  ///
  /// In pt, this message translates to:
  /// **'Falta cadastrar o rosto para usar o que foi autorizado.'**
  String get faceEnrollmentMissing;

  /// No description provided for @faceEnrollmentNeedsConsent.
  ///
  /// In pt, this message translates to:
  /// **'Autorize pelo menos um uso abaixo para cadastrar o rosto.'**
  String get faceEnrollmentNeedsConsent;

  /// No description provided for @reenrollFace.
  ///
  /// In pt, this message translates to:
  /// **'Refazer o cadastro do rosto'**
  String get reenrollFace;

  /// No description provided for @enrollMyFace.
  ///
  /// In pt, this message translates to:
  /// **'Cadastrar meu rosto'**
  String get enrollMyFace;

  /// No description provided for @consentAdultsOnly.
  ///
  /// In pt, this message translates to:
  /// **'Só para maiores de 18 anos.'**
  String get consentAdultsOnly;

  /// No description provided for @consentGuardianDecides.
  ///
  /// In pt, this message translates to:
  /// **'Até os 16 anos, quem autoriza é o seu responsável, pelo app dele.'**
  String get consentGuardianDecides;

  /// No description provided for @consentGranted.
  ///
  /// In pt, this message translates to:
  /// **'{purpose}: autorizado.'**
  String consentGranted(String purpose);

  /// No description provided for @consentRevoked.
  ///
  /// In pt, this message translates to:
  /// **'{purpose}: revogado.'**
  String consentRevoked(String purpose);

  /// No description provided for @dependentDecidesAlone.
  ///
  /// In pt, this message translates to:
  /// **'A partir de 16 anos, o próprio aluno autoriza o uso do rosto pelo app.'**
  String get dependentDecidesAlone;

  /// No description provided for @dependentFaceEnrolled.
  ///
  /// In pt, this message translates to:
  /// **'O rosto de {name} está cadastrado.'**
  String dependentFaceEnrolled(String name);

  /// No description provided for @dependentEnrollAfterConsent.
  ///
  /// In pt, this message translates to:
  /// **'Depois de autorizar, {name} cadastra o próprio rosto no app (Perfil → Reconhecimento facial).'**
  String dependentEnrollAfterConsent(String name);

  /// No description provided for @termsOnBehalfOf.
  ///
  /// In pt, this message translates to:
  /// **'Autorização em nome de {name}'**
  String termsOnBehalfOf(String name);

  /// No description provided for @termsVersion.
  ///
  /// In pt, this message translates to:
  /// **'Termo versão {version}'**
  String termsVersion(String version);

  /// No description provided for @termsAgree.
  ///
  /// In pt, this message translates to:
  /// **'Li e concordo'**
  String get termsAgree;

  /// No description provided for @notNow.
  ///
  /// In pt, this message translates to:
  /// **'Agora não'**
  String get notNow;

  /// No description provided for @revokeTitle.
  ///
  /// In pt, this message translates to:
  /// **'Revogar: {purpose}?'**
  String revokeTitle(String purpose);

  /// No description provided for @revokeBody.
  ///
  /// In pt, this message translates to:
  /// **'O rosto deixa de ser usado para isso agora. Se nenhum uso continuar autorizado, o cadastro do rosto é apagado.'**
  String get revokeBody;

  /// No description provided for @revoke.
  ///
  /// In pt, this message translates to:
  /// **'Revogar'**
  String get revoke;

  /// No description provided for @dependentsTitle.
  ///
  /// In pt, this message translates to:
  /// **'Meus dependentes'**
  String get dependentsTitle;

  /// No description provided for @dependentsEmpty.
  ///
  /// In pt, this message translates to:
  /// **'Nenhum aluno vinculado à sua conta. Procure a secretaria.'**
  String get dependentsEmpty;

  /// No description provided for @dependentFallbackName.
  ///
  /// In pt, this message translates to:
  /// **'Dependente'**
  String get dependentFallbackName;

  /// No description provided for @dependentTabFace.
  ///
  /// In pt, this message translates to:
  /// **'Rosto'**
  String get dependentTabFace;

  /// No description provided for @dependentTabBenefits.
  ///
  /// In pt, this message translates to:
  /// **'Benefícios'**
  String get dependentTabBenefits;

  /// No description provided for @financialBadge.
  ///
  /// In pt, this message translates to:
  /// **'Financeiro'**
  String get financialBadge;

  /// No description provided for @relationshipMother.
  ///
  /// In pt, this message translates to:
  /// **'Mãe'**
  String get relationshipMother;

  /// No description provided for @relationshipFather.
  ///
  /// In pt, this message translates to:
  /// **'Pai'**
  String get relationshipFather;

  /// No description provided for @relationshipLegalGuardian.
  ///
  /// In pt, this message translates to:
  /// **'Responsável legal'**
  String get relationshipLegalGuardian;

  /// No description provided for @relationshipGrandparent.
  ///
  /// In pt, this message translates to:
  /// **'Avó/avô'**
  String get relationshipGrandparent;

  /// No description provided for @relationshipOther.
  ///
  /// In pt, this message translates to:
  /// **'Responsável'**
  String get relationshipOther;

  /// No description provided for @tabHome.
  ///
  /// In pt, this message translates to:
  /// **'Início'**
  String get tabHome;

  /// No description provided for @tabNotices.
  ///
  /// In pt, this message translates to:
  /// **'Avisos'**
  String get tabNotices;

  /// No description provided for @tabAgenda.
  ///
  /// In pt, this message translates to:
  /// **'Agenda'**
  String get tabAgenda;

  /// No description provided for @tabReportCard.
  ///
  /// In pt, this message translates to:
  /// **'Boletim'**
  String get tabReportCard;

  /// No description provided for @tabDependents.
  ///
  /// In pt, this message translates to:
  /// **'Dependentes'**
  String get tabDependents;

  /// No description provided for @tabProfile.
  ///
  /// In pt, this message translates to:
  /// **'Perfil'**
  String get tabProfile;

  /// No description provided for @homeGreeting.
  ///
  /// In pt, this message translates to:
  /// **'Olá, {name}!'**
  String homeGreeting(String name);

  /// No description provided for @homeAllRead.
  ///
  /// In pt, this message translates to:
  /// **'Tudo lido'**
  String get homeAllRead;

  /// No description provided for @homeUnread.
  ///
  /// In pt, this message translates to:
  /// **'{count} sem ler'**
  String homeUnread(int count);

  /// No description provided for @homeTapToSee.
  ///
  /// In pt, this message translates to:
  /// **'Toque para ver'**
  String get homeTapToSee;

  /// No description provided for @homeNextOnAgenda.
  ///
  /// In pt, this message translates to:
  /// **'Próximo na agenda'**
  String get homeNextOnAgenda;

  /// No description provided for @homeNothingAhead.
  ///
  /// In pt, this message translates to:
  /// **'Nada pela frente'**
  String get homeNothingAhead;

  /// No description provided for @homeNextItem.
  ///
  /// In pt, this message translates to:
  /// **'{title} · {date}'**
  String homeNextItem(String title, String date);

  /// No description provided for @homeFaceAttendance.
  ///
  /// In pt, this message translates to:
  /// **'Chamada facial'**
  String get homeFaceAttendance;

  /// No description provided for @homeAttendanceHint.
  ///
  /// In pt, this message translates to:
  /// **'Fotografe a sala e revise'**
  String get homeAttendanceHint;

  /// No description provided for @homeAttendancePending.
  ///
  /// In pt, this message translates to:
  /// **'{count, plural, =1{1 chamada guardada no aparelho} other{{count} chamadas guardadas no aparelho}}'**
  String homeAttendancePending(int count);

  /// No description provided for @homeNothingToPickUp.
  ///
  /// In pt, this message translates to:
  /// **'Nada para retirar'**
  String get homeNothingToPickUp;

  /// No description provided for @homeToPickUp.
  ///
  /// In pt, this message translates to:
  /// **'{count} para retirar'**
  String homeToPickUp(int count);

  /// No description provided for @homeNoDependents.
  ///
  /// In pt, this message translates to:
  /// **'Nenhum vinculado'**
  String get homeNoDependents;

  /// No description provided for @materialsTitle.
  ///
  /// In pt, this message translates to:
  /// **'Requisições de material'**
  String get materialsTitle;

  /// No description provided for @materialsEmpty.
  ///
  /// In pt, this message translates to:
  /// **'Nenhuma requisição. Peça materiais pelo site.'**
  String get materialsEmpty;

  /// No description provided for @materialStatusPending.
  ///
  /// In pt, this message translates to:
  /// **'Aguardando aprovação'**
  String get materialStatusPending;

  /// No description provided for @materialStatusApproved.
  ///
  /// In pt, this message translates to:
  /// **'Aprovada: retirar'**
  String get materialStatusApproved;

  /// No description provided for @materialStatusRejected.
  ///
  /// In pt, this message translates to:
  /// **'Recusada'**
  String get materialStatusRejected;

  /// No description provided for @materialStatusDelivered.
  ///
  /// In pt, this message translates to:
  /// **'Retirada'**
  String get materialStatusDelivered;

  /// No description provided for @materialStatusClosed.
  ///
  /// In pt, this message translates to:
  /// **'Concluída'**
  String get materialStatusClosed;

  /// No description provided for @materialStatusCancelled.
  ///
  /// In pt, this message translates to:
  /// **'Cancelada'**
  String get materialStatusCancelled;

  /// No description provided for @materialReturnOverdue.
  ///
  /// In pt, this message translates to:
  /// **'Devolução atrasada'**
  String get materialReturnOverdue;

  /// No description provided for @materialNeededOn.
  ///
  /// In pt, this message translates to:
  /// **'Para {date}'**
  String materialNeededOn(String date);

  /// No description provided for @materialReturnBy.
  ///
  /// In pt, this message translates to:
  /// **'devolver até {date}'**
  String materialReturnBy(String date);

  /// No description provided for @materialLine.
  ///
  /// In pt, this message translates to:
  /// **'{material}: {quantity} {unit}'**
  String materialLine(String material, int quantity, String unit);

  /// No description provided for @materialLineToReturn.
  ///
  /// In pt, this message translates to:
  /// **'{line} · devolver {count}'**
  String materialLineToReturn(String line, int count);

  /// No description provided for @pickupQr.
  ///
  /// In pt, this message translates to:
  /// **'QR de retirada'**
  String get pickupQr;

  /// No description provided for @materialQrFooter.
  ///
  /// In pt, this message translates to:
  /// **'Mostre este QR no almoxarifado. Só você recebe este código.'**
  String get materialQrFooter;

  /// No description provided for @noticesTitle.
  ///
  /// In pt, this message translates to:
  /// **'Avisos'**
  String get noticesTitle;

  /// No description provided for @markAllAsRead.
  ///
  /// In pt, this message translates to:
  /// **'Marcar todos como lidos'**
  String get markAllAsRead;

  /// No description provided for @noNotices.
  ///
  /// In pt, this message translates to:
  /// **'Nenhum aviso por enquanto.'**
  String get noNotices;

  /// No description provided for @profileTitle.
  ///
  /// In pt, this message translates to:
  /// **'Perfil'**
  String get profileTitle;

  /// No description provided for @profileEmail.
  ///
  /// In pt, this message translates to:
  /// **'E-mail'**
  String get profileEmail;

  /// No description provided for @profileRole.
  ///
  /// In pt, this message translates to:
  /// **'{count, plural, =1{Papel} other{Papéis}}'**
  String profileRole(int count);

  /// No description provided for @profileInstitution.
  ///
  /// In pt, this message translates to:
  /// **'Instituição'**
  String get profileInstitution;

  /// No description provided for @profileFaceRecognition.
  ///
  /// In pt, this message translates to:
  /// **'Reconhecimento facial'**
  String get profileFaceRecognition;

  /// No description provided for @profileFaceRecognitionHint.
  ///
  /// In pt, this message translates to:
  /// **'Entrar com o rosto, catraca e presença: autorizações e cadastro do rosto'**
  String get profileFaceRecognitionHint;

  /// No description provided for @signOut.
  ///
  /// In pt, this message translates to:
  /// **'Sair'**
  String get signOut;

  /// No description provided for @signOutTitle.
  ///
  /// In pt, this message translates to:
  /// **'Sair da conta?'**
  String get signOutTitle;

  /// No description provided for @signOutBody.
  ///
  /// In pt, this message translates to:
  /// **'Você vai precisar entrar de novo com e-mail e senha.'**
  String get signOutBody;

  /// No description provided for @signOutPendingAttendance.
  ///
  /// In pt, this message translates to:
  /// **'{count, plural, =1{Há 1 chamada com fotos ainda não enviadas: ela será apagada do aparelho.} other{Há {count} chamadas com fotos ainda não enviadas: elas serão apagadas do aparelho.}}'**
  String signOutPendingAttendance(int count);

  /// No description provided for @roleStudent.
  ///
  /// In pt, this message translates to:
  /// **'Aluno'**
  String get roleStudent;

  /// No description provided for @roleInstructor.
  ///
  /// In pt, this message translates to:
  /// **'Instrutor'**
  String get roleInstructor;

  /// No description provided for @roleCoordinator.
  ///
  /// In pt, this message translates to:
  /// **'Coordenação'**
  String get roleCoordinator;

  /// No description provided for @roleSecretary.
  ///
  /// In pt, this message translates to:
  /// **'Secretaria'**
  String get roleSecretary;

  /// No description provided for @roleGuardian.
  ///
  /// In pt, this message translates to:
  /// **'Responsável'**
  String get roleGuardian;

  /// No description provided for @roleCompanyManager.
  ///
  /// In pt, this message translates to:
  /// **'Gestão empresa'**
  String get roleCompanyManager;

  /// No description provided for @roleInstitutionAdmin.
  ///
  /// In pt, this message translates to:
  /// **'Admin da instituição'**
  String get roleInstitutionAdmin;

  /// No description provided for @roleAdmin.
  ///
  /// In pt, this message translates to:
  /// **'Admin'**
  String get roleAdmin;

  /// No description provided for @roleSuperAdmin.
  ///
  /// In pt, this message translates to:
  /// **'Admin da plataforma'**
  String get roleSuperAdmin;

  /// No description provided for @reportCardTitle.
  ///
  /// In pt, this message translates to:
  /// **'Boletim'**
  String get reportCardTitle;

  /// No description provided for @reportCardEmpty.
  ///
  /// In pt, this message translates to:
  /// **'Ainda não há notas publicadas.'**
  String get reportCardEmpty;

  /// No description provided for @reportCardNoPeriods.
  ///
  /// In pt, this message translates to:
  /// **'Nenhuma etapa fechada ainda.'**
  String get reportCardNoPeriods;

  /// No description provided for @reportCardAbsences.
  ///
  /// In pt, this message translates to:
  /// **'{count, plural, =1{1 falta} other{{count} faltas}}'**
  String reportCardAbsences(int count);

  /// No description provided for @reportCardFinalGrade.
  ///
  /// In pt, this message translates to:
  /// **'Média final: {grade}'**
  String reportCardFinalGrade(String grade);

  /// No description provided for @reportCardRecovery.
  ///
  /// In pt, this message translates to:
  /// **'Recuperação: {grade}'**
  String reportCardRecovery(String grade);

  /// No description provided for @reportCardAttendance.
  ///
  /// In pt, this message translates to:
  /// **'Frequência: {rate}'**
  String reportCardAttendance(String rate);

  /// No description provided for @reportCardPassingGrade.
  ///
  /// In pt, this message translates to:
  /// **'Média para aprovar: {grade}'**
  String reportCardPassingGrade(String grade);

  /// No description provided for @subjectInProgress.
  ///
  /// In pt, this message translates to:
  /// **'Cursando'**
  String get subjectInProgress;

  /// No description provided for @subjectRecovery.
  ///
  /// In pt, this message translates to:
  /// **'Em recuperação'**
  String get subjectRecovery;

  /// No description provided for @subjectApproved.
  ///
  /// In pt, this message translates to:
  /// **'Aprovado'**
  String get subjectApproved;

  /// No description provided for @subjectFailed.
  ///
  /// In pt, this message translates to:
  /// **'Reprovado'**
  String get subjectFailed;

  /// No description provided for @subjectFailedAttendance.
  ///
  /// In pt, this message translates to:
  /// **'Reprovado por falta'**
  String get subjectFailedAttendance;

  /// No description provided for @appTitle.
  ///
  /// In pt, this message translates to:
  /// **'W-Edu'**
  String get appTitle;

  /// No description provided for @errorGeneric.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível concluir.'**
  String get errorGeneric;

  /// No description provided for @errorNoConnection.
  ///
  /// In pt, this message translates to:
  /// **'Sem conexão com o servidor. Verifique a internet.'**
  String get errorNoConnection;

  /// No description provided for @errorTimeout.
  ///
  /// In pt, this message translates to:
  /// **'O servidor demorou a responder.'**
  String get errorTimeout;

  /// No description provided for @tryAgain.
  ///
  /// In pt, this message translates to:
  /// **'Tentar de novo'**
  String get tryAgain;

  /// No description provided for @back.
  ///
  /// In pt, this message translates to:
  /// **'Voltar'**
  String get back;

  /// No description provided for @cancel.
  ///
  /// In pt, this message translates to:
  /// **'Cancelar'**
  String get cancel;

  /// No description provided for @keep.
  ///
  /// In pt, this message translates to:
  /// **'Manter'**
  String get keep;

  /// No description provided for @close.
  ///
  /// In pt, this message translates to:
  /// **'Fechar'**
  String get close;

  /// No description provided for @errorLoad.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível carregar.'**
  String get errorLoad;

  /// No description provided for @errorRefresh.
  ///
  /// In pt, this message translates to:
  /// **'Não foi possível atualizar.'**
  String get errorRefresh;

  /// No description provided for @faceStepCenter.
  ///
  /// In pt, this message translates to:
  /// **'Olhe para a câmera'**
  String get faceStepCenter;

  /// No description provided for @faceStepTurnLeft.
  ///
  /// In pt, this message translates to:
  /// **'Vire o rosto para a esquerda'**
  String get faceStepTurnLeft;

  /// No description provided for @faceStepTurnRight.
  ///
  /// In pt, this message translates to:
  /// **'Vire o rosto para a direita'**
  String get faceStepTurnRight;

  /// No description provided for @faceStepProgress.
  ///
  /// In pt, this message translates to:
  /// **'Passo {current} de {total}'**
  String faceStepProgress(int current, int total);

  /// No description provided for @qrSemanticLabel.
  ///
  /// In pt, this message translates to:
  /// **'QR de {title}'**
  String qrSemanticLabel(String title);

  /// No description provided for @openingCamera.
  ///
  /// In pt, this message translates to:
  /// **'Abrindo a câmera…'**
  String get openingCamera;

  /// No description provided for @start.
  ///
  /// In pt, this message translates to:
  /// **'Começar'**
  String get start;
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>['en', 'pt'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'pt':
      return AppLocalizationsPt();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
