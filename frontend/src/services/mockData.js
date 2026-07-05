export const mockStudent = {
  student_id: 'S001',
  name: 'Tom',
  avatar: '',
  current_goal_id: 'G001',
  learning_speed: 'medium',
  learning_preference: 'basic',
  recent_state: '专注学习中',
}

export const mockGoals = [
  {
    goal_id: 'G001',
    title: '掌握递归',
    target_node_id: 'recursion',
    target_name: '递归',
    description: '理解递归思想、调用过程与终止条件，并能编写简单递归程序。',
    recommended_level: 'intermediate',
    difficulty: 4,
    duration: '3–4 小时',
    recommended: true,
  },
  {
    goal_id: 'G002',
    title: '巩固函数基础',
    target_node_id: 'function',
    target_name: '函数',
    description: '掌握函数定义、参数传递、返回值与作用域。',
    recommended_level: 'beginner',
    difficulty: 2,
    duration: '1–2 小时',
  },
  {
    goal_id: 'G003',
    title: '理解调用栈',
    target_node_id: 'call_stack',
    target_name: '调用栈',
    description: '理解栈帧、函数调用顺序和返回过程。',
    recommended_level: 'intermediate',
    difficulty: 3,
    duration: '2–3 小时',
  },
  {
    goal_id: 'G004',
    title: '递归应用入门',
    target_node_id: 'tree_recursion',
    target_name: '树形递归',
    description: '通过阶乘与斐波那契案例理解递归应用。',
    recommended_level: 'intermediate',
    difficulty: 4,
    duration: '4–5 小时',
  },
  {
    goal_id: 'G005',
    title: '深度优先搜索',
    target_node_id: 'dfs',
    target_name: 'DFS',
    description: '使用递归完成树和图的深度优先遍历。',
    recommended_level: 'advanced',
    difficulty: 5,
    duration: '5–6 小时',
  },
  {
    goal_id: 'G006',
    title: '回溯算法',
    target_node_id: 'backtracking',
    target_name: '回溯',
    description: '理解选择、递归与撤销选择组成的搜索过程。',
    recommended_level: 'advanced',
    difficulty: 5,
    duration: '6–8 小时',
  },
]

export const mockPaths = [
  {
    path_id: 'P001',
    path_type: 'basic',
    path_name: '基础补全路径',
    subtitle: '系统学习，循序渐进',
    reason: '调用栈和返回值掌握较弱，建议先补全前置知识。',
    duration: '8–10 小时',
    difficulty: '平缓',
    is_current: true,
    nodes: ['函数', '参数传递', '返回值', '调用栈', '递归'],
  },
  {
    path_id: 'P002',
    path_type: 'example',
    path_name: '案例驱动路径',
    subtitle: '通过案例理解，学以致用',
    reason: '通过阶乘、斐波那契等案例建立递归直觉。',
    duration: '6–8 小时',
    difficulty: '适中',
    is_current: false,
    nodes: ['函数回顾', '阶乘案例', '调用栈', '递归', '综合练习'],
  },
  {
    path_id: 'P003',
    path_type: 'fast',
    path_name: '快速提升路径',
    subtitle: '高效速成，直击重点',
    reason: '跳过已掌握内容，直接聚焦递归核心。',
    duration: '4–6 小时',
    difficulty: '较陡',
    is_current: false,
    nodes: ['函数', '调用栈', '递归', '递归应用'],
  },
]

export const mockCurrentPath = {
  path_id: 'P001',
  path_name: '基础补全路径',
  path_type: 'basic',
  goal_id: 'G001',
  current_node_id: 'call_stack',
  status: 'active',
  reason: '调用栈和返回值掌握较弱，建议先补全前置知识。',
  nodes: [
    { node_id: 'function', name: '函数', status: 'completed' },
    { node_id: 'parameter', name: '参数传递', status: 'completed' },
    { node_id: 'return_value', name: '返回值', status: 'completed' },
    { node_id: 'call_stack', name: '调用栈', status: 'learning' },
    { node_id: 'recursion', name: '递归', status: 'pending' },
  ],
}

export const mockResources = [
  {
    resource_id: 'R002',
    title: '调用栈可视化讲解',
    resource_type: 'text',
    url: '',
    content: '逐步展示函数调用时栈帧的入栈与出栈。',
    difficulty: 3,
  },
  {
    resource_id: 'R003',
    title: '调用栈跟踪练习',
    resource_type: 'exercise',
    url: '',
    content: '跟踪嵌套函数调用并写出返回顺序。',
    difficulty: 3,
  },
]

export const mockLearningCurrent = {
  current_node: {
    node_id: 'call_stack',
    name: '调用栈',
    description: '调用栈用于记录函数调用过程，并保存函数返回后继续执行的位置。',
  },
  path_progress: { completed: 3, total: 5, percent: 60 },
  resources: mockResources,
}

export const mockGraphNodes = [
  { id: 'variable', name: '变量', difficulty: 1, status: 'completed' },
  { id: 'expression', name: '表达式', difficulty: 1, status: 'completed' },
  { id: 'condition', name: '条件语句', difficulty: 2, status: 'not_in_path' },
  { id: 'loop', name: '循环', difficulty: 2, status: 'not_in_path' },
  { id: 'function', name: '函数', difficulty: 2, status: 'completed' },
  { id: 'parameter', name: '参数传递', difficulty: 3, status: 'completed' },
  { id: 'return_value', name: '返回值', difficulty: 3, status: 'completed' },
  { id: 'call_stack', name: '调用栈', difficulty: 4, status: 'learning' },
  { id: 'recursion', name: '递归', difficulty: 4, status: 'pending' },
  { id: 'tree_recursion', name: '树形递归', difficulty: 4, status: 'not_in_path' },
  { id: 'dfs', name: 'DFS', difficulty: 5, status: 'not_in_path' },
  { id: 'backtracking', name: '回溯', difficulty: 5, status: 'not_in_path' },
]

export const mockGraphEdges = [
  ['variable', 'expression'],
  ['expression', 'condition'],
  ['condition', 'loop'],
  ['variable', 'function'],
  ['expression', 'function'],
  ['function', 'parameter'],
  ['parameter', 'return_value'],
  ['function', 'return_value'],
  ['function', 'call_stack'],
  ['return_value', 'call_stack'],
  ['call_stack', 'recursion'],
  ['recursion', 'tree_recursion'],
  ['tree_recursion', 'dfs'],
  ['dfs', 'backtracking'],
  ['recursion', 'backtracking'],
].map(([source, target]) => ({ source, target, relation: 'prerequisite' }))

export const mockMastery = [
  { node_id: 'function', name: '函数', mastery: 0.82 },
  { node_id: 'parameter', name: '参数传递', mastery: 0.74 },
  { node_id: 'return_value', name: '返回值', mastery: 0.55 },
  { node_id: 'call_stack', name: '调用栈', mastery: 0.3 },
  { node_id: 'recursion', name: '递归', mastery: 0.18 },
]

export const mockLearningEvents = [
  { event_id: 1, created_at: '2026-07-05 18:00', node_name: '函数', event_type: 'learn', result: 'completed', score: 0.8, time_spent: 240 },
  { event_id: 2, created_at: '2026-07-05 18:20', node_name: '返回值', event_type: 'quiz', result: 'wrong', score: 0.4, time_spent: 180 },
  { event_id: 3, created_at: '2026-07-05 18:40', node_name: '调用栈', event_type: 'quiz', result: 'wrong', score: 0.3, time_spent: 220 },
  { event_id: 4, created_at: '2026-07-05 19:05', node_name: '调用栈', event_type: 'learn', result: 'completed', score: 0.7, time_spent: 300 },
]

export const mockDialogues = [
  {
    dialogue_id: 1,
    node_id: 'call_stack',
    user_message: '为什么函数返回后还能继续执行？',
    ai_response: '调用栈会保存每次函数调用前的执行位置，函数返回时会恢复该位置。',
    extracted_signal: { knowledge_gap: 'call_stack', confusion_level: 0.8, learning_preference: 'basic', suggested_action: 'insert_prerequisite' },
    created_at: '2026-07-05 19:00',
  },
  {
    dialogue_id: 2,
    node_id: 'return_value',
    user_message: 'return 和 print 有什么区别？',
    ai_response: 'return 把结果交还给调用者，print 只负责把内容显示出来。',
    extracted_signal: { knowledge_gap: 'return_value', confusion_level: 0.6, learning_preference: 'example', suggested_action: 'review_node' },
    created_at: '2026-07-05 19:10',
  },
]

export const mockSwitchLogs = [
  {
    switch_id: 1,
    old_path_name: '案例驱动路径',
    new_path_name: '基础补全路径',
    trigger_type: 'dialogue',
    reason: '对话信号显示对调用栈存在明显困惑，建议补全前置知识。',
    created_at: '2026-07-05 20:00',
  },
]

export const mockProfile = {
  student_id: 'S001',
  learning_speed: 'medium',
  learning_preference: 'basic',
  confidence: 0.62,
  current_goal: '掌握递归',
  current_path: '基础补全路径',
  weak_points: ['调用栈', '返回值'],
  recent_state: 'confused',
}

export const mockStudents = [
  { student_id: 'S001', name: 'Tom', learning_speed: 'medium', learning_preference: 'basic' },
  { student_id: 'S002', name: 'Alice', learning_speed: 'fast', learning_preference: 'fast' },
  { student_id: 'S003', name: 'Bob', learning_speed: 'slow', learning_preference: 'example' },
]
