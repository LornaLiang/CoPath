import api from './api'

export const studentApi = {
  getCurrent: () => api.get('/students/current'),
  list: () => api.get('/students'),
}

export const goalApi = {
  list: () => api.get('/goals'),
  select: (studentId, goalId) => api.post('/goals/select', { student_id: studentId, goal_id: goalId }),
}

export const pathApi = {
  getCurrent: (studentId) => api.get('/paths/current', { params: { student_id: studentId } }),
  listCandidates: (studentId, goalId) => api.get('/paths/candidates', { params: { student_id: studentId, goal_id: goalId } }),
  switch: (studentId, newPathId, reason) => api.post('/paths/switch', { student_id: studentId, new_path_id: newPathId, reason }),
  listSwitchLogs: (studentId) => api.get('/paths/switch-logs', { params: { student_id: studentId } }),
  generate: (studentId, goalId) => api.post('/path/generate', { student_id: studentId, goal_id: goalId }),
  updateDynamic: (studentId, goalId) => api.post('/path/update', { student_id: studentId, goal_id: goalId }),
  getPlan: (studentId) => api.get(`/path/${encodeURIComponent(studentId)}`),
  getPendingAdjustment: (studentId) => api.get(`/path/pending-adjustment/${encodeURIComponent(studentId)}`),
  suggestAdjustment: (studentId, goalId, triggerType = 'manual', triggerSignal = null) => api.post('/path/suggest-adjustment', { student_id: studentId, goal_id: goalId, trigger_type: triggerType, trigger_signal: triggerSignal }),
  confirmAdjustment: (studentId, suggestionId) => api.post('/path/confirm-adjustment', { student_id: studentId, suggestion_id: suggestionId }),
  rejectAdjustment: (studentId, suggestionId) => api.post('/path/reject-adjustment', { student_id: studentId, suggestion_id: suggestionId }),
  evaluateSwitch: (studentId, newPathId, force = false) => api.post('/path/evaluate-switch', { student_id: studentId, new_path_id: newPathId, force }),
}

export const learningApi = {
  getCurrent: (studentId) => api.get('/learning/current', { params: { student_id: studentId } }),
  saveEvent: (event) => api.post('/learning/event', event),
  submitFeedback: (feedback) => api.post('/learning/feedback', feedback),
  listEvents: (studentId) => api.get('/learning/events', { params: { student_id: studentId } }),
  getSummary: (studentId) => api.get('/learning/summary', { params: { student_id: studentId } }),
}

export const dialogueApi = {
  list: (studentId) => api.get('/dialogues', { params: { student_id: studentId } }),
  chat: (studentId, nodeId, message) => api.post('/chat', { student_id: studentId, node_id: nodeId, message }),
}

export const graphApi = {
  get: (studentId) => api.get('/graph', { params: { student_id: studentId } }),
  getNode: (nodeId) => api.get(`/graph/node/${encodeURIComponent(nodeId)}`),
}

export const profileApi = {
  get: (studentId) => api.get(`/profile/${encodeURIComponent(studentId)}`),
  getMastery: (studentId) => api.get('/profile/mastery', { params: { student_id: studentId } }),
  updateFromAI: (studentId, aiSignal) => api.post('/profile/update', { student_id: studentId, ai_signal: aiSignal }),
  recordEvent: (studentId, nodeId, result) => api.post('/profile/event', { student_id: studentId, node_id: nodeId, result }),
}

export const resourceApi = {
  getCurrent: (studentId) => api.get('/resources/current', { params: { student_id: studentId } }),
}

export const settingsApi = {
  get: () => api.get('/settings'),
  switchStudent: (studentId) => api.post('/settings/student', { student_id: studentId }),
  resetDemo: () => api.post('/settings/reset-demo'),
  health: () => api.get('/health'),
}
