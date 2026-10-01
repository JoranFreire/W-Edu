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
    meetingVouchers: (meetingId: string) => `/social/meetings/${meetingId}/vouchers`,
    vouchers: '/social/vouchers',
    offeringVouchers: (offeringId: string) => `/social/offerings/${offeringId}/vouchers`,
    cancelVoucher: (voucherId: string) => `/social/vouchers/${voucherId}/cancel`,
    lookupVoucher: '/social/vouchers/lookup',
    redeemVoucher: '/social/vouchers/redeem',
    myVouchers: '/social/my/vouchers',
  },
  retention: {
    offering: (offeringId: string) => `/retention/offerings/${offeringId}`,
    evaluate: (offeringId: string) => `/retention/offerings/${offeringId}/evaluate`,
    readmit: (enrollmentId: string) => `/retention/enrollments/${enrollmentId}/readmit`,
  },
};
