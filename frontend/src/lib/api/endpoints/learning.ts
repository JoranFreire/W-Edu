/** Cursos, trilhas, aulas, progresso, atividades, quizzes, sessoes de voz e certificados. */
export const learningEndpoints = {
  courses: {
    list: '/courses',
    detail: (id: string) => `/courses/${id}`,
    lessons: (courseId: string) => `/lessons/course/${courseId}`,
    modules: (courseId: string) => `/courses/${courseId}/modules`,
    moduleDetail: (moduleId: string) => `/courses/modules/${moduleId}`,
    prerequisites: (courseId: string) => `/courses/${courseId}/prerequisites`,
  },
  learningPaths: {
    list: '/learning-paths',
    detail: (id: string) => `/learning-paths/${id}`,
    courses: (id: string) => `/learning-paths/${id}/courses`,
  },
  enrollments: {
    byStudent: (studentId: string) => `/enrollments/student/${studentId}`,
    create: '/enrollments',
  },
  progress: {
    me: '/progress/me',
    courses: '/progress/me/courses',
    update: (lessonId: string) => `/progress/${lessonId}`,
  },
  sessions: {
    me: '/sessions/me',
    history: '/sessions/me/history',
    create: '/sessions',
    voiceStart: '/sessions/voice/start',
    voice: (id: string) => `/sessions/${id}/voice`,
  },
  lessons: {
    videoStream: (id: string) => `/lessons/${id}/video/stream`,
    videoUpload: (id: string) => `/lessons/${id}/video`,
  },
  assignments: {
    mine: (lessonId: string) => `/assignments/lessons/${lessonId}/me`,
    submit: (lessonId: string) => `/assignments/lessons/${lessonId}/submit`,
    submissions: (lessonId: string) => `/assignments/lessons/${lessonId}/submissions`,
    review: (submissionId: string) => `/assignments/submissions/${submissionId}`,
    download: (submissionId: string) => `/assignments/submissions/${submissionId}/download`,
  },
  quizzes: {
    lesson: (lessonId: string) => `/quizzes/lesson/${lessonId}`,
    lessonOptional: (lessonId: string) => `/quizzes/lesson/${lessonId}/optional`,
    attempts: (lessonId: string) => `/quizzes/lesson/${lessonId}/attempts`,
    attemptsOptional: (lessonId: string) => `/quizzes/lesson/${lessonId}/attempts/optional`,
    attempt: (lessonId: string) => `/quizzes/lesson/${lessonId}/attempt`,
  },
  certificates: {
    rule: (courseId: string) => `/certificates/rules/${courseId}`,
    eligibility: (courseId: string, studentId: string) => `/certificates/courses/${courseId}/students/${studentId}/eligibility`,
    issue: (courseId: string, studentId: string) => `/certificates/courses/${courseId}/students/${studentId}/issue`,
    courseCertificates: (courseId: string) => `/certificates/courses/${courseId}/certificates`,
    revoke: (id: string) => `/certificates/${id}/revoke`,
    download: (id: string) => `/certificates/${id}/download`,
    validate: (code: string) => `/certificates/validate/${code}`,
    my: '/certificates/students/me',
    student: (studentId: string) => `/certificates/students/${studentId}`,
  },
};
