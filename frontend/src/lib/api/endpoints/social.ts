/** Programas sociais e frequencia/evasao. */
export const socialEndpoints = {
  social: {
    fundingSources: '/social/funding-sources',
    fundingSource: (id: string) => `/social/funding-sources/${id}`,
    fundingReport: (id: string) => `/social/funding-sources/${id}/report`,
    fundingReportCsv: (id: string) => `/social/funding-sources/${id}/report.csv`,
    items: '/social/benefit-items',
    item: (id: string) => `/social/benefit-items/${id}`,
    stock: (itemId: string) => `/social/benefit-items/${itemId}/stock`,
    meetingDeliveries: (meetingId: string) => `/social/meetings/${meetingId}/deliveries`,
    deliveries: '/social/deliveries',
    offeringDeliveries: (offeringId: string) => `/social/offerings/${offeringId}/deliveries`,
    myBenefits: '/social/my/benefits',
  },
  retention: {
    offering: (offeringId: string) => `/retention/offerings/${offeringId}`,
    evaluate: (offeringId: string) => `/retention/offerings/${offeringId}/evaluate`,
    readmit: (enrollmentId: string) => `/retention/enrollments/${enrollmentId}/readmit`,
  },
};
