PRAGMA foreign_keys = ON;

BEGIN;

INSERT OR IGNORE INTO knowledge_nodes
    (node_id, name, description, difficulty, chapter)
VALUES
    ('variable', '变量', '理解变量的定义、赋值与基本使用方式。', 1, 'Python 基础'),
    ('expression', '表达式', '理解运算符、表达式求值与基本数据运算。', 1, 'Python 基础'),
    ('condition', '条件语句', '使用条件判断控制程序执行分支。', 2, '流程控制'),
    ('loop', '循环', '使用循环结构重复执行代码。', 2, '流程控制'),
    ('function', '函数', '理解函数定义、调用和代码复用。', 2, '函数与递归'),
    ('parameter', '参数传递', '理解位置参数、形参与实参的传递过程。', 3, '函数与递归'),
    ('return_value', '返回值', '理解函数返回值以及调用结果的使用方式。', 3, '函数与递归'),
    ('call_stack', '调用栈', '理解函数调用过程中栈帧的创建与返回。', 4, '函数与递归'),
    ('recursion', '递归', '理解递归定义、终止条件和递归调用过程。', 4, '函数与递归'),
    ('tree_recursion', '树形递归', '理解一次调用产生多个递归分支的执行过程。', 4, '递归进阶'),
    ('dfs', '深度优先搜索', '使用递归实现图或树的深度优先遍历。', 5, '递归进阶'),
    ('backtracking', '回溯', '理解选择、递归与撤销选择组成的搜索过程。', 5, '递归进阶');

INSERT OR IGNORE INTO knowledge_edges
    (edge_id, source_id, target_id, relation)
VALUES
    (1, 'variable', 'expression', 'prerequisite'),
    (2, 'expression', 'condition', 'prerequisite'),
    (3, 'condition', 'loop', 'prerequisite'),
    (4, 'variable', 'function', 'prerequisite'),
    (5, 'expression', 'function', 'prerequisite'),
    (6, 'function', 'parameter', 'prerequisite'),
    (7, 'parameter', 'return_value', 'prerequisite'),
    (8, 'function', 'return_value', 'prerequisite'),
    (9, 'function', 'call_stack', 'prerequisite'),
    (10, 'return_value', 'call_stack', 'prerequisite'),
    (11, 'call_stack', 'recursion', 'prerequisite'),
    (12, 'recursion', 'tree_recursion', 'prerequisite'),
    (13, 'tree_recursion', 'dfs', 'prerequisite'),
    (14, 'dfs', 'backtracking', 'prerequisite'),
    (15, 'recursion', 'backtracking', 'prerequisite');

INSERT OR IGNORE INTO learning_goals
    (goal_id, target_node_id, title, description, recommended_level)
VALUES
    (
        'G001',
        'recursion',
        '掌握递归',
        '理解递归思想、调用过程与终止条件，并能编写简单递归程序。',
        'intermediate'
    );

INSERT OR IGNORE INTO students
    (student_id, name, avatar, current_goal_id, created_at)
VALUES
    ('S001', 'Tom', '/assets/avatar/tom.png', 'G001', '2026-07-05 09:00:00'),
    ('S002', 'Alice', '/assets/avatar/alice.png', 'G001', '2026-07-05 09:05:00'),
    ('S003', 'Bob', '/assets/avatar/bob.png', 'G001', '2026-07-05 09:10:00');

INSERT OR IGNORE INTO student_profiles
    (
        profile_id,
        student_id,
        learning_speed,
        learning_preference,
        confidence,
        profile_json,
        updated_at
    )
VALUES
    (
        1,
        'S001',
        'medium',
        'basic',
        0.62,
        '{"mastery":{"function":0.75,"return_value":0.55,"call_stack":0.30,"recursion":0.10},"weak_points":["call_stack","return_value"],"recent_state":"confused"}',
        '2026-07-05 20:10:00'
    ),
    (
        2,
        'S002',
        'fast',
        'fast',
        0.86,
        '{"mastery":{"function":0.92,"return_value":0.88,"call_stack":0.82,"recursion":0.68},"weak_points":["tree_recursion"],"recent_state":"focused"}',
        '2026-07-05 20:12:00'
    ),
    (
        3,
        'S003',
        'slow',
        'example',
        0.57,
        '{"mastery":{"function":0.70,"return_value":0.60,"call_stack":0.48,"recursion":0.25},"weak_points":["recursion","call_stack"],"recent_state":"needs_example"}',
        '2026-07-05 20:15:00'
    );

INSERT OR IGNORE INTO learning_paths
    (
        path_id,
        student_id,
        goal_id,
        path_type,
        path_name,
        nodes_json,
        is_current,
        status,
        reason,
        created_at
    )
VALUES
    (
        'P001', 'S001', 'G001', 'basic', '基础补全路径',
        '["variable","expression","function","parameter","return_value","call_stack","recursion"]',
        1, 'active', 'Tom 的调用栈和返回值掌握较弱，适合先补全前置知识。',
        '2026-07-05 10:00:00'
    ),
    (
        'P002', 'S001', 'G001', 'example', '案例驱动路径',
        '["function","parameter","return_value","call_stack","recursion","tree_recursion"]',
        0, 'switched', '通过阶乘与斐波那契案例理解递归。',
        '2026-07-05 10:00:00'
    ),
    (
        'P003', 'S001', 'G001', 'fast', '快速提升路径',
        '["function","call_stack","recursion"]',
        0, 'planned', '跳过已掌握内容，直接学习递归核心。',
        '2026-07-05 10:00:00'
    ),
    (
        'P004', 'S002', 'G001', 'basic', '基础补全路径',
        '["variable","expression","function","parameter","return_value","call_stack","recursion"]',
        0, 'planned', '按完整前置知识顺序学习递归。',
        '2026-07-05 10:05:00'
    ),
    (
        'P005', 'S002', 'G001', 'example', '案例驱动路径',
        '["function","return_value","call_stack","recursion","tree_recursion"]',
        0, 'planned', '通过典型程序案例巩固递归。',
        '2026-07-05 10:05:00'
    ),
    (
        'P006', 'S002', 'G001', 'fast', '快速提升路径',
        '["function","call_stack","recursion"]',
        1, 'active', 'Alice 基础较好且学习速度快，适合快速提升路径。',
        '2026-07-05 10:05:00'
    ),
    (
        'P007', 'S003', 'G001', 'basic', '基础补全路径',
        '["variable","expression","function","parameter","return_value","call_stack","recursion"]',
        0, 'switched', '按完整前置知识顺序学习递归。',
        '2026-07-05 10:10:00'
    ),
    (
        'P008', 'S003', 'G001', 'example', '案例驱动路径',
        '["function","parameter","return_value","call_stack","recursion","tree_recursion"]',
        1, 'active', 'Bob 偏好通过案例学习，适合案例驱动路径。',
        '2026-07-05 10:10:00'
    ),
    (
        'P009', 'S003', 'G001', 'fast', '快速提升路径',
        '["function","call_stack","recursion"]',
        0, 'planned', '直接聚焦递归所需的核心知识。',
        '2026-07-05 10:10:00'
    );

INSERT OR IGNORE INTO learning_events
    (event_id, student_id, node_id, event_type, result, score, time_spent, created_at)
VALUES
    (1, 'S001', 'function', 'learn', 'completed', 0.80, 240, '2026-07-05 18:00:00'),
    (2, 'S001', 'return_value', 'quiz', 'wrong', 0.40, 180, '2026-07-05 18:20:00'),
    (3, 'S001', 'call_stack', 'quiz', 'wrong', 0.30, 220, '2026-07-05 18:40:00'),
    (4, 'S002', 'function', 'finish', 'completed', 1.00, 120, '2026-07-05 18:05:00'),
    (5, 'S002', 'call_stack', 'quiz', 'correct', 0.90, 100, '2026-07-05 18:25:00'),
    (6, 'S002', 'recursion', 'learn', 'completed', 0.85, 160, '2026-07-05 18:45:00'),
    (7, 'S003', 'function', 'quiz', 'correct', 0.70, 260, '2026-07-05 18:10:00'),
    (8, 'S003', 'call_stack', 'learn', 'completed', 0.60, 300, '2026-07-05 18:30:00'),
    (9, 'S003', 'recursion', 'pause', NULL, NULL, 180, '2026-07-05 18:50:00');

INSERT OR IGNORE INTO dialogue_logs
    (
        dialogue_id,
        student_id,
        node_id,
        user_message,
        ai_response,
        extracted_signal_json,
        created_at
    )
VALUES
    (
        1,
        'S001',
        'call_stack',
        '为什么函数返回后还能继续执行？',
        '调用栈会保存每次函数调用前的执行位置，函数返回时会恢复该位置。',
        '{"knowledge_gap":"call_stack","confusion_level":0.8,"learning_preference":"basic","suggested_action":"insert_prerequisite"}',
        '2026-07-05 19:00:00'
    ),
    (
        2,
        'S001',
        'return_value',
        'return 和 print 有什么区别？',
        'return 把结果交还给调用者，print 只负责把内容显示出来。',
        '{"knowledge_gap":"return_value","confusion_level":0.6,"learning_preference":"example","suggested_action":"review_node"}',
        '2026-07-05 19:10:00'
    ),
    (
        3,
        'S002',
        'recursion',
        '我可以直接练习递归题吗？',
        '可以，你的前置知识较完整，可以从基础递归练习开始。',
        '{"knowledge_gap":null,"confusion_level":0.2,"learning_preference":"fast","suggested_action":"continue"}',
        '2026-07-05 19:15:00'
    ),
    (
        4,
        'S003',
        'recursion',
        '能用生活中的例子解释递归吗？',
        '可以把递归理解为打开一个盒子后发现里面还有同样结构的小盒子。',
        '{"knowledge_gap":"recursion","confusion_level":0.7,"learning_preference":"example","suggested_action":"show_example"}',
        '2026-07-05 19:20:00'
    );

INSERT OR IGNORE INTO path_switch_logs
    (
        switch_id,
        student_id,
        old_path_id,
        new_path_id,
        trigger_type,
        trigger_signal_json,
        reason,
        created_at
    )
VALUES
    (
        1,
        'S001',
        'P002',
        'P001',
        'dialogue',
        '{"knowledge_gap":"call_stack","confusion_level":0.8}',
        '对话记录显示 Tom 对调用栈存在明显困惑，切换到基础补全路径。',
        '2026-07-05 20:00:00'
    ),
    (
        2,
        'S003',
        'P007',
        'P008',
        'manual',
        '{"learning_preference":"example"}',
        'Bob 主动选择通过案例方式学习。',
        '2026-07-05 20:05:00'
    );

INSERT OR IGNORE INTO learning_resources
    (resource_id, node_id, title, resource_type, url, content, difficulty)
VALUES
    ('R001', 'return_value', '返回值基础讲解', 'text', '', '通过示例区分函数返回值与输出。', 2),
    ('R002', 'call_stack', '调用栈可视化讲解', 'text', '', '逐步展示函数调用时栈帧的入栈与出栈。', 3),
    ('R003', 'call_stack', '调用栈练习', 'exercise', '', '跟踪嵌套函数调用并写出返回顺序。', 3),
    ('R004', 'recursion', '递归基础讲解', 'text', '', '介绍递归定义、终止条件和规模缩减。', 3),
    ('R005', 'recursion', '阶乘递归示例', 'code', '', '使用 Python 编写并跟踪阶乘递归程序。', 3),
    ('R006', 'tree_recursion', '斐波那契调用树', 'text', '', '使用调用树观察重复递归分支。', 4),
    ('R007', 'dfs', '递归实现 DFS', 'code', '', '使用递归完成树的深度优先遍历。', 4),
    ('R008', 'backtracking', '回溯入门练习', 'exercise', '', '通过排列问题理解选择与撤销选择。', 5);

INSERT OR IGNORE INTO system_settings (setting_key, setting_value)
VALUES
    ('theme', 'light'),
    ('llm_provider', 'openai'),
    ('model_name', 'gpt-4.1-mini'),
    ('current_student_id', 'S001');

COMMIT;
