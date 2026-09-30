'use client';

import Modal from '@/components/common/Modal';
import type { Subject } from '@/types/academic';
import SubjectLinkList from './SubjectLinkList';

export default function SubjectLinksModal({ subject, subjects, canRemove, onClose }: {
  subject: Subject;
  subjects: Subject[];
  canRemove: boolean;
  onClose: () => void;
}) {
  return (
    <Modal title={`${subject.code} · ${subject.name}`} description="Pré-requisitos e equivalências" size="xl" onClose={onClose}>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <SubjectLinkList kind="prerequisites" subject={subject} subjects={subjects} canRemove={canRemove} />
        <SubjectLinkList kind="equivalences" subject={subject} subjects={subjects} canRemove={canRemove} />
      </div>
    </Modal>
  );
}
