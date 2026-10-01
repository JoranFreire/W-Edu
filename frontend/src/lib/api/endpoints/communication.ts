/** Comunicacao: avisos, forum e chat. */
export const communicationEndpoints = {
  notifications: {
    templates: '/notifications/templates',
    template: (key: string, channel: string) => `/notifications/templates/${key}/${channel}`,
    events: '/notifications/events',
    processDue: '/notifications/events/process-due',
    eventRetry: (id: string) => `/notifications/events/${id}/retry`,
    inbox: '/notifications/me',
    inboxSummary: '/notifications/me/summary',
    inboxReadAll: '/notifications/me/read-all',
    inboxRead: (id: string) => `/notifications/me/${id}/read`,
  },
  forum: {
    courseThreads: (courseId: string) => `/forum/courses/${courseId}/threads`,
    thread: (threadId: string) => `/forum/threads/${threadId}`,
    posts: (threadId: string) => `/forum/threads/${threadId}/posts`,
  },
  chat: {
    conversations: '/chat/conversations',
    conversation: (id: string) => `/chat/conversations/${id}`,
    messages: (id: string) => `/chat/conversations/${id}/messages`,
  },
};
