/** Editais e processos seletivos. */
export const admissionsEndpoints = {
  admissions: {
    publicCalls: '/admissions/public/calls',
    publicCall: (id: string) => `/admissions/public/calls/${id}`,
    publicResult: (id: string) => `/admissions/public/calls/${id}/result`,
    apply: (callId: string) => `/admissions/calls/${callId}/apply`,
    mine: '/admissions/my/applications',
    myDocuments: (id: string) => `/admissions/my/applications/${id}/documents`,
    myAction: (id: string, action: 'withdraw' | 'confirm' | 'decline') => `/admissions/my/applications/${id}/${action}`,
    calls: '/admissions/calls',
    call: (id: string) => `/admissions/calls/${id}`,
    callStatus: (id: string) => `/admissions/calls/${id}/status`,
    callApplications: (id: string) => `/admissions/calls/${id}/applications`,
    review: (applicationId: string) => `/admissions/applications/${applicationId}/review`,
    documentReview: (documentId: string) => `/admissions/documents/${documentId}/review`,
    documentDownload: (documentId: string) => `/admissions/documents/${documentId}/download`,
    select: (id: string) => `/admissions/calls/${id}/select`,
    deadlines: (id: string) => `/admissions/calls/${id}/process-deadlines`,
  },
};
