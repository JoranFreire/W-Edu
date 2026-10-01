/** Relatorios e documentos. */
export const reportsEndpoints = {
  analytics: {
    overview: '/analytics/overview',
    courses: '/analytics/courses',
    course: (id: string) => `/analytics/courses/${id}`,
    me: '/analytics/students/me',
    student: (id: string) => `/analytics/students/${id}`,
    class: (id: string) => `/analytics/classes/${id}`,
    reports: {
      completion: '/analytics/reports/completion',
      attendance: '/analytics/reports/attendance',
      engagement: '/analytics/reports/engagement',
      performance: '/analytics/reports/performance',
      roi: '/analytics/reports/roi',
    },
  },
  documents: {
    list: '/documents',
    detail: (id: string) => `/documents/${id}`,
    versions: (id: string) => `/documents/${id}/versions`,
    versionDownload: (documentId: string, versionId: string) => `/documents/${documentId}/versions/${versionId}/download`,
    download: (id: string) => `/documents/${id}/download`,
  },
};
