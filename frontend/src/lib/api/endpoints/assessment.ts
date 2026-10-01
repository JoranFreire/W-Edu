/** Diario de classe: avaliacoes, notas, chamada e resultados. */
export const assessmentEndpoints = {
  assessment: {
    schemes: '/assessment/grading-schemes',
    scheme: (id: string) => `/assessment/grading-schemes/${id}`,
    teachingOfferings: '/assessment/teaching/offerings',
    offering: (id: string) => `/assessment/offerings/${id}`,
    syncGroup: (id: string) => `/assessment/offerings/${id}/sync-group-enrollments`,
    items: (offeringId: string) => `/assessment/offerings/${offeringId}/items`,
    item: (id: string) => `/assessment/items/${id}`,
    grades: (itemId: string) => `/assessment/items/${itemId}/grades`,
    importQuiz: (itemId: string) => `/assessment/items/${itemId}/import-quiz`,
    gradebook: (offeringId: string) => `/assessment/offerings/${offeringId}/gradebook`,
    diary: (offeringId: string) => `/assessment/offerings/${offeringId}/diary`,
    diaryEntry: (id: string) => `/assessment/diary-entries/${id}`,
    diaryAttendance: (id: string) => `/assessment/diary-entries/${id}/attendance`,
    closePeriod: (offeringId: string, periodId: string) => `/assessment/offerings/${offeringId}/periods/${periodId}/close`,
    results: (offeringId: string) => `/assessment/offerings/${offeringId}/results`,
    computeResults: (offeringId: string) => `/assessment/offerings/${offeringId}/results/compute`,
    recovery: (offeringId: string) => `/assessment/offerings/${offeringId}/recovery`,
    finalize: (offeringId: string) => `/assessment/offerings/${offeringId}/finalize`,
    myReportCard: '/assessment/my/report-card',
  },
};
