/** Almoxarifado. */
export const warehouseEndpoints = {
  warehouse: {
    items: '/warehouse/items',
    item: (id: string) => `/warehouse/items/${id}`,
    entries: (id: string) => `/warehouse/items/${id}/entries`,
    history: (id: string) => `/warehouse/items/${id}/history`,
    lookup: '/warehouse/requests/lookup',
    pickup: '/warehouse/requests/pickup',
    requests: '/warehouse/requests',
    myRequests: '/warehouse/my/requests',
    cancel: (id: string) => `/warehouse/my/requests/${id}/cancel`,
    action: (id: string, action: 'approve' | 'reject' | 'deliver' | 'returns') => `/warehouse/requests/${id}/${action}`,
    lowStock: '/warehouse/reports/low-stock',
    overdue: '/warehouse/reports/overdue',
    consumption: '/warehouse/reports/consumption',
  },
};
