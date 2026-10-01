/** Responsaveis e vida escolar (ocorrencias e agenda). */
export const familyEndpoints = {
  guardians: {
    links: (studentId: string) => `/guardians/students/${studentId}/links`,
    link: (linkId: string) => `/guardians/links/${linkId}`,
    dependents: '/guardians/me/dependents',
    reportCard: (studentId: string) => `/guardians/me/dependents/${studentId}/report-card`,
    notices: (studentId: string) => `/guardians/me/dependents/${studentId}/notices`,
    charges: (studentId: string) => `/guardians/me/dependents/${studentId}/charges`,
    occurrences: (studentId: string) => `/guardians/me/dependents/${studentId}/occurrences`,
    acknowledge: (studentId: string, occurrenceId: string) => `/guardians/me/dependents/${studentId}/occurrences/${occurrenceId}/acknowledge`,
    agenda: (studentId: string) => `/guardians/me/dependents/${studentId}/agenda`,
  },
  school: {
    occurrences: '/school/occurrences',
    occurrence: (occurrenceId: string) => `/school/occurrences/${occurrenceId}`,
    studentOccurrences: (studentId: string) => `/school/students/${studentId}/occurrences`,
    groupAgenda: (groupId: string) => `/school/class-groups/${groupId}/agenda`,
    agendaItem: (itemId: string) => `/school/agenda/${itemId}`,
    myAgenda: '/school/my/agenda',
  },
};
