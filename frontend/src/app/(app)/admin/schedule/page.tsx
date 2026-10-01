'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { AcademicCapIcon, BuildingOffice2Icon, MapPinIcon, UserIcon } from '@heroicons/react/24/outline';
import CheckinQrModal from '@/components/admin/CheckinQrModal';
import ClassOfferingForm from '@/components/admin/ClassOfferingForm';
import ClassOfferingsList from '@/components/admin/ClassOfferingsList';
import LocationForm from '@/components/admin/LocationForm';
import RoomForm from '@/components/admin/RoomForm';
import InstructorAgendaPanel from '@/components/admin/schedule/InstructorAgendaPanel';
import LocationsList from '@/components/admin/schedule/LocationsList';
import MeetingFormModal, { type MeetingSlot } from '@/components/admin/schedule/MeetingFormModal';
import RoomsList from '@/components/admin/schedule/RoomsList';
import OfferingTimeSlotsModal from '@/components/registration/OfferingTimeSlotsModal';
import Modal from '@/components/common/Modal';
import SectionHeader from '@/components/common/SectionHeader';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import Spinner from '@/components/common/Spinner';
import { toDateTimeLocal } from '@/lib/dates';
import { useCheckinToken } from '@/lib/hooks/admin/useCheckinToken';
import { useClassMeetings } from '@/lib/hooks/admin/useClassMeetings';
import { useScheduleSetup } from '@/lib/hooks/admin/useScheduleSetup';
import type { ClassOffering, InstructorAgendaSuggestion } from '@/types/schedule';

type SetupTab = 'classes' | 'instructors' | 'rooms' | 'locations';
type CreateModal = 'class' | 'room' | 'location' | null;

export default function AdminSchedulePage() {
  const setup = useScheduleSetup();
  const meetings = useClassMeetings();
  const checkin = useCheckinToken();
  const [activeTab, setActiveTab] = useState<SetupTab>('classes');
  const [createModal, setCreateModal] = useState<CreateModal>(null);
  const [meetingClass, setMeetingClass] = useState<ClassOffering | null>(null);
  const [pendingSlot, setPendingSlot] = useState<MeetingSlot | null>(null);
  const [slotsClass, setSlotsClass] = useState<ClassOffering | null>(null);

  const closeCreateModal = () => setCreateModal(null);
  const afterCreate = () => {
    setCreateModal(null);
    setup.reload();
  };

  const pickSuggestion = (suggestion: InstructorAgendaSuggestion) => {
    setPendingSlot({ starts_at: toDateTimeLocal(suggestion.starts_at), ends_at: toDateTimeLocal(suggestion.ends_at) });
    setActiveTab('classes');
    toast.success('Horário selecionado. Escolha uma turma e crie o encontro.');
  };

  const closeMeetingModal = () => {
    setMeetingClass(null);
    setPendingSlot(null);
  };

  if (setup.loading && setup.classes.length === 0) return <Spinner />;

  const tabs: TabItem<SetupTab>[] = [
    { id: 'classes', label: 'Turmas', icon: AcademicCapIcon, badge: setup.classes.length },
    { id: 'instructors', label: 'Instrutores', icon: UserIcon, badge: setup.instructors.length },
    { id: 'rooms', label: 'Salas', icon: BuildingOffice2Icon, badge: setup.rooms.length },
    { id: 'locations', label: 'Unidades', icon: MapPinIcon, badge: setup.locations.length },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Agenda e Turmas</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Unidades, salas, ofertas de turma e encontros presenciais ou lives.</p>
      </div>
      <div className="space-y-5">
        <TabNav tabs={tabs} active={activeTab} onChange={setActiveTab} ariaLabel="Configurações da agenda" idPrefix="schedule-setup" />

        <div id={`schedule-setup-${activeTab}`} role="tabpanel" className="space-y-4">
          {activeTab === 'classes' && (
            <>
              <SectionHeader
                title="Turmas cadastradas"
                description="Gerencie ofertas, encontros e presenças em um só lugar."
                actionLabel="Adicionar turma"
                onAction={() => setCreateModal('class')}
              />
              <ClassOfferingsList
                classes={setup.classes} courses={setup.courses} rooms={setup.rooms}
                meetings={meetings.meetings} attendance={meetings.attendance}
                attendanceReports={meetings.attendanceReports} summaries={meetings.summaries}
                showHeader={false}
                onCreateMeeting={setMeetingClass} onLoadMeetings={meetings.loadMeetings} onGenerateCheckin={checkin.generate}
                onLoadAttendance={meetings.loadAttendance} onLoadAttendanceReport={meetings.loadAttendanceReport}
                onMarkAttendance={meetings.markAttendance} onSavePracticalAssessment={meetings.savePracticalAssessment}
                onLoadSummary={meetings.loadSummary} onCloseMeeting={meetings.closeMeeting} onEditSlots={setSlotsClass}
              />
            </>
          )}
          {activeTab === 'instructors' && (
            <InstructorAgendaPanel instructors={setup.instructors} onPickSuggestion={pickSuggestion} />
          )}
          {activeTab === 'rooms' && (
            <>
              <SectionHeader
                title="Salas cadastradas"
                description="Organize espaços físicos, capacidade e vínculo com unidades."
                actionLabel="Adicionar sala"
                onAction={() => setCreateModal('room')}
              />
              <RoomsList rooms={setup.rooms} locations={setup.locations} />
            </>
          )}
          {activeTab === 'locations' && (
            <>
              <SectionHeader
                title="Unidades cadastradas"
                description="Mantenha os polos e unidades disponíveis para aulas presenciais."
                actionLabel="Adicionar unidade"
                onAction={() => setCreateModal('location')}
              />
              <LocationsList locations={setup.locations} rooms={setup.rooms} />
            </>
          )}
        </div>
      </div>

      {createModal === 'class' && (
        <Modal title="Adicionar turma" description="Defina curso, período, capacidade e sala." size="xl" onClose={closeCreateModal}>
          <ClassOfferingForm courses={setup.courses} rooms={setup.rooms} instructors={setup.instructors} variant="plain" onCancel={closeCreateModal} onCreated={afterCreate} />
        </Modal>
      )}
      {createModal === 'room' && (
        <Modal title="Adicionar sala" description="Vincule a sala a uma unidade e defina sua capacidade." onClose={closeCreateModal}>
          <RoomForm locations={setup.locations} variant="plain" onCancel={closeCreateModal} onCreated={afterCreate} />
        </Modal>
      )}
      {createModal === 'location' && (
        <Modal title="Adicionar unidade" description="Crie uma unidade para organizar salas e encontros presenciais." onClose={closeCreateModal}>
          <LocationForm variant="plain" onCancel={closeCreateModal} onCreated={afterCreate} />
        </Modal>
      )}
      {meetingClass && (
        <MeetingFormModal
          classOffering={meetingClass}
          rooms={setup.rooms}
          slot={pendingSlot}
          onSubmit={meetings.createMeeting}
          onClose={closeMeetingModal}
        />
      )}
      {slotsClass && (
        <OfferingTimeSlotsModal offeringId={slotsClass.id} offeringName={slotsClass.name} onClose={() => setSlotsClass(null)} />
      )}
      {checkin.token && (
        <CheckinQrModal token={checkin.token} meeting={checkin.meeting} checkinUrl={checkin.url} onCopy={checkin.copyUrl} onClose={checkin.clear} />
      )}
    </div>
  );
}
