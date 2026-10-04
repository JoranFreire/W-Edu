import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wedu_mobile/features/agenda/data/agenda_item.dart';
import 'package:wedu_mobile/features/auth/data/institution.dart';
import 'package:wedu_mobile/features/auth/data/user.dart';
import 'package:wedu_mobile/features/benefits/data/benefit.dart';
import 'package:wedu_mobile/features/dependents/data/dependent.dart';
import 'package:wedu_mobile/features/dependents/widgets/dependent_card.dart';
import 'package:wedu_mobile/features/materials/data/material_request.dart';
import 'package:wedu_mobile/features/materials/widgets/material_request_card.dart';
import 'package:wedu_mobile/features/notices/data/notice.dart';
import 'package:wedu_mobile/features/report_card/data/report_card.dart';
import 'package:wedu_mobile/l10n/l10n.dart';

import '../helpers/fakes.dart';

void main() {
  final pt = lookupAppLocalizations(const Locale('pt'));
  final en = lookupAppLocalizations(const Locale('en'));

  test('instituição usa o nome exibido e a cor da marca', () {
    final institution = Institution.fromJson(institutionJson());
    expect(institution.name, 'Colégio Alfa');
    expect(institution.primaryColor, const Color(0xFF059669));
  });

  test('usuário com vários papéis', () {
    final user = User.fromJson(
      userJson(role: 'instructor', roles: ['instructor', 'student', 'guardian']),
      Institution.fromJson(institutionJson()),
    );
    expect(user.isStudent, isTrue);
    expect(user.isGuardian, isTrue);
    expect(user.firstName, 'Ana');
  });

  test('aviso lido e não lido', () {
    expect(Notice.fromJson(noticeJson('a1')).isRead, isFalse);
    expect(Notice.fromJson(noticeJson('a1')).markedAsRead().isRead, isTrue);
  });

  test('item da agenda lê a data como dia local', () {
    final item = AgendaItem.fromJson(agendaJson('i1', day: '2026-10-03'));
    expect(item.date, DateTime(2026, 10, 3));
    expect(item.kind, AgendaItemKind.test);
    expect(AgendaItemKind.of('unknown'), AgendaItemKind.notice);
  });

  test('disciplina do boletim', () {
    final subject = ReportCardSubject.fromJson(reportCardJson());
    expect(subject.result, SubjectResult.approved);
    expect(subject.periods.single.absences, 2);
    expect(subject.attendanceRate, 0.92);
  });

  test('dependente e o parentesco no idioma da tela', () {
    final dependent = Dependent.fromJson(dependentJson());
    expect(dependent.studentId, 's-1');
    expect(relationshipLabel(dependent.relationship, pt), 'Mãe');
    expect(relationshipLabel(dependent.relationship, en), 'Mother');
  });

  test('benefícios: para retirar primeiro e validade vale também offline', () {
    final list = Benefit.list([
      benefitJson('1', status: 'redeemed'),
      benefitJson('2', validUntil: '2020-01-01'),
      benefitJson('3', validUntil: '2099-12-31', item: 'Kit'),
    ]);
    expect(list.map((b) => b.id), ['3', '1', '2']);
    expect(list.first.isReadyForPickup, isTrue);
    expect(list.first.qrPayload, 'wedu-beneficio:COD3');
    expect(list.first.kind, BenefitKind.snack);
    expect(BenefitKind.of('uniform'), BenefitKind.uniform);
    expect(BenefitKind.of(null), BenefitKind.other);
    expect(list.last.status(), BenefitStatus.expired);
    expect(list[1].status(), BenefitStatus.redeemed);
  });

  test('requisições: aprovadas com QR primeiro; linha mostra o que vale agora', () {
    final list = MaterialRequest.list([materialRequestJson('1', status: 'pending'), materialRequestJson('2', code: 'ABC')]);
    expect(list.map((r) => r.id), ['2', '1']);
    expect(list.first.isReadyForPickup, isTrue);
    expect(lineSummary(list.first.lines.single, pt), 'Papel A4: 2 resma');
    expect(list.last.status, MaterialRequestStatus.pending);
  });

  test('permissões vêm do acesso', () {
    final user = User.fromJson(userJson(role: 'instructor'), Institution.fromJson(institutionJson()), permissions: ['warehouse.request']);
    expect(user.canRequestMaterials, isTrue);
  });
}
