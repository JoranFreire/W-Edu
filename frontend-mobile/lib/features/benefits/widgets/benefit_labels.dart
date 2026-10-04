import '../../../l10n/l10n.dart';
import '../data/benefit.dart';

extension BenefitStatusText on BenefitStatus {
  String label(AppLocalizations l10n) => switch (this) {
    BenefitStatus.released => l10n.benefitStatusReleased,
    BenefitStatus.redeemed => l10n.benefitStatusRedeemed,
    BenefitStatus.cancelled => l10n.benefitStatusCancelled,
    BenefitStatus.expired => l10n.benefitStatusExpired,
  };
}

extension BenefitKindText on BenefitKind {
  String label(AppLocalizations l10n) => switch (this) {
    BenefitKind.snack => l10n.benefitKindSnack,
    BenefitKind.material => l10n.benefitKindMaterial,
    BenefitKind.uniform => l10n.benefitKindUniform,
    BenefitKind.transport => l10n.benefitKindTransport,
    BenefitKind.stipend => l10n.benefitKindStipend,
    BenefitKind.other => l10n.benefitKindOther,
  };
}
