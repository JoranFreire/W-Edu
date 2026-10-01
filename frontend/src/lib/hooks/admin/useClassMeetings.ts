'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import type {
  AttendanceRecord,
  AttendanceStatus,
  MeetingAttendanceReportRow,
  MeetingAttendanceSummary,
  MeetingType,
  ScheduledMeeting,
} from '@/types/schedule';

export interface MeetingDraft {
  class_offering_id: string;
  title: string;
  room_id: string | null;
  starts_at: string;
  ends_at: string;
  type: MeetingType;
}

type ByMeeting<T> = Record<string, T>;

/** Encontros das turmas e o que acontece neles: presenca, resumo e avaliacao pratica. */
export function useClassMeetings() {
  const [meetings, setMeetings] = useState<ByMeeting<ScheduledMeeting[]>>({});
  const [attendance, setAttendance] = useState<ByMeeting<AttendanceRecord[]>>({});
  const [attendanceReports, setAttendanceReports] = useState<ByMeeting<MeetingAttendanceReportRow[]>>({});
  const [summaries, setSummaries] = useState<ByMeeting<MeetingAttendanceSummary>>({});

  const createMeeting = async (draft: MeetingDraft) => {
    const { data } = await api.post<ScheduledMeeting>(endpoints.schedule.meetings, draft);
    setMeetings((prev) => ({ ...prev, [draft.class_offering_id]: [...(prev[draft.class_offering_id] ?? []), data] }));
    return data;
  };

  const loadMeetings = async (classId: string) => {
    const { data } = await api.get<ScheduledMeeting[]>(endpoints.schedule.classMeetings(classId));
    setMeetings((prev) => ({ ...prev, [classId]: data }));
  };

  const loadAttendance = async (meetingId: string) => {
    try {
      const { data } = await api.get<AttendanceRecord[]>(endpoints.schedule.attendance(meetingId));
      setAttendance((prev) => ({ ...prev, [meetingId]: data }));
    } catch { toast.error('Erro ao carregar presença.'); }
  };

  const loadAttendanceReport = async (meetingId: string) => {
    try {
      const { data } = await api.get<MeetingAttendanceReportRow[]>(endpoints.schedule.attendanceReport(meetingId));
      setAttendanceReports((prev) => ({ ...prev, [meetingId]: data }));
    } catch { toast.error('Erro ao carregar relatório de presença.'); }
  };

  const loadSummary = async (meetingId: string) => {
    try {
      const { data } = await api.get<MeetingAttendanceSummary>(endpoints.schedule.meetingSummary(meetingId));
      setSummaries((prev) => ({ ...prev, [meetingId]: data }));
    } catch { toast.error('Erro ao carregar resumo.'); }
  };

  const markAttendance = async (meeting: ScheduledMeeting, studentId: string, status: AttendanceStatus) => {
    try {
      await api.post<AttendanceRecord>(endpoints.schedule.attendance(meeting.id), { student_id: studentId, status, method: 'manual' });
      await Promise.all([loadAttendanceReport(meeting.id), loadAttendance(meeting.id), loadSummary(meeting.id)]);
      toast.success('Presença atualizada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao atualizar presença.'));
    }
  };

  const savePracticalAssessment = async (meeting: ScheduledMeeting, studentId: string, score: number, feedback: string | null) => {
    try {
      await api.post(endpoints.schedule.practicalAssessments(meeting.id), { student_id: studentId, score, status: 'reviewed', feedback });
      await loadAttendanceReport(meeting.id);
      toast.success('Avaliação prática salva.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao salvar avaliação prática.'));
    }
  };

  const closeMeeting = async (meeting: ScheduledMeeting) => {
    try {
      const { data } = await api.post<ScheduledMeeting>(endpoints.schedule.closeMeeting(meeting.id));
      setMeetings((prev) => ({
        ...prev,
        [meeting.class_offering_id]: (prev[meeting.class_offering_id] ?? []).map((m) => (m.id === meeting.id ? data : m)),
      }));
      toast.success('Encontro encerrado.');
    } catch { toast.error('Erro ao encerrar encontro.'); }
  };

  return {
    meetings, attendance, attendanceReports, summaries,
    createMeeting, loadMeetings, loadAttendance, loadAttendanceReport, loadSummary,
    markAttendance, savePracticalAssessment, closeMeeting,
  };
}
