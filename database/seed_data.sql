PRAGMA foreign_keys = ON;

BEGIN;

INSERT INTO knowledge_nodes
    (node_id, name, description, difficulty, chapter)
VALUES
    ('variable', '变量', '理解变量的定义、赋值与基本使用方式。', 1, 'Python 基础'),
    ('expression', '表达式', '理解运算符、表达式求值与基本数据运算。', 1, 'Python 基础'),
    ('condition', '条件语句', '使用条件判断控制程序执行分支。', 2, '流程控制'),
    ('loop', '循环', '使用循环结构重复执行代码。', 2, '流程控制'),
    ('function', '函数', '理解函数定义、调用和代码复用。', 2, '函数与递归'),
    ('parameter', '参数传递', '理解形参、实参以及参数传递过程。', 3, '函数与递归'),
    ('return_value', '返回值', '理解函数返回值以及调用结果的使用方式。', 3, '函数与递归'),
    ('call_stack', '调用栈', '理解函数调用过程中栈帧的创建、保存与返回。', 4, '函数与递归'),
    ('recursion', '递归思想', '理解递归问题分解、终止条件和递归调用。', 4, '函数与递归'),
    ('basic_recursion', '基础递归', '能够阅读并编写阶乘、汉诺塔等基础递归程序。', 4, '函数与递归'),
    ('dfs', 'DFS', '使用递归实现树或图的深度优先遍历。', 5, '递归进阶'),
    ('backtracking', '回溯', '理解选择、递归与撤销选择组成的搜索过程。', 5, '递归进阶');

INSERT INTO knowledge_edges
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
    (12, 'recursion', 'basic_recursion', 'prerequisite'),
    (13, 'basic_recursion', 'dfs', 'prerequisite'),
    (14, 'dfs', 'backtracking', 'prerequisite'),
    (15, 'loop', 'dfs', 'prerequisite');

INSERT INTO learning_goals
    (goal_id, target_node_id, title, description, recommended_level)
VALUES
    ('G001', 'recursion', '掌握递归', '理解递归思想并能编写基础递归程序。', 'intermediate');

INSERT INTO students
    (student_id, name, avatar, current_goal_id, created_at)
VALUES
    ('S001', 'Tom', '/assets/avatar/tom.png', 'G001', '2026-07-05 09:00:00'),
    ('S002', 'Alice', '/assets/avatar/alice.png', 'G001', '2026-07-05 09:05:00'),
    ('S003', 'Bob', '/assets/avatar/bob.png', 'G001', '2026-07-05 09:10:00');

INSERT INTO student_profiles
    (profile_id, student_id, learning_speed, learning_preference, confidence,
     mastery_json, profile_json, updated_at)
VALUES
    (
        1, 'S001', 'medium', 'example', 0.58,
        '{"function":1.0,"parameter":0.9,"return_value":0.55,"call_stack":0.2,"recursion":0.0}',
        '{"mastery":{"function":1.0,"parameter":0.9,"return_value":0.55,"call_stack":0.2,"recursion":0.0},"weak_points":["call_stack","return_value"],"recent_state":"confused"}',
        '2026-07-05 20:10:00'
    ),
    (
        2, 'S002', 'fast', 'fast', 0.91,
        '{"function":1.0,"parameter":1.0,"return_value":0.95,"call_stack":0.9,"recursion":0.75}',
        '{"mastery":{"function":1.0,"parameter":1.0,"return_value":0.95,"call_stack":0.9,"recursion":0.75},"weak_points":[],"recent_state":"ready_to_advance"}',
        '2026-07-05 20:12:00'
    ),
    (
        3, 'S003', 'slow', 'example', 0.43,
        '{"function":0.8,"parameter":0.6,"return_value":0.35,"call_stack":0.1,"recursion":0.0}',
        '{"mastery":{"function":0.8,"parameter":0.6,"return_value":0.35,"call_stack":0.1,"recursion":0.0},"weak_points":["call_stack","return_value","recursion"],"recent_state":"needs_example"}',
        '2026-07-05 20:15:00'
    );

-- 汉诺塔和递归程序是案例资源，不额外扩展为知识点，以保持文档规定的 12 个知识点。
INSERT INTO learning_paths
    (path_id, student_id, goal_id, path_type, path_name, nodes_json, is_current, status, reason, created_at)
VALUES
    ('P001', 'S001', 'G001', 'basic', '基础补全路径', '["function","parameter","return_value","call_stack","recursion","basic_recursion"]', 1, 'active', 'Tom 基础一般且调用栈理解较弱，推荐补全前置知识。', '2026-07-05 10:00:00'),
    ('P002', 'S001', 'G001', 'example', '案例驱动路径', '["function","recursion","basic_recursion","dfs"]', 0, 'planned', '通过汉诺塔等案例理解递归并过渡到 DFS。', '2026-07-05 10:00:00'),
    ('P003', 'S001', 'G001', 'fast', '快速提升路径', '["recursion","basic_recursion","dfs","backtracking"]', 0, 'planned', '直接学习递归思想、DFS 与回溯。', '2026-07-05 10:00:00'),
    ('P004', 'S002', 'G001', 'basic', '基础补全路径', '["function","parameter","return_value","call_stack","recursion","basic_recursion"]', 0, 'planned', '按完整前置知识顺序掌握递归。', '2026-07-05 10:05:00'),
    ('P005', 'S002', 'G001', 'example', '案例驱动路径', '["function","recursion","basic_recursion","dfs"]', 0, 'planned', '通过汉诺塔等案例巩固递归。', '2026-07-05 10:05:00'),
    ('P006', 'S002', 'G001', 'fast', '快速提升路径', '["recursion","basic_recursion","dfs","backtracking"]', 1, 'active', 'Alice 基础扎实且学习速度快，推荐跳过已掌握内容。', '2026-07-05 10:05:00'),
    ('P007', 'S003', 'G001', 'basic', '基础补全路径', '["function","parameter","return_value","call_stack","recursion","basic_recursion"]', 0, 'planned', '按完整前置知识顺序掌握递归。', '2026-07-05 10:10:00'),
    ('P008', 'S003', 'G001', 'example', '案例驱动路径', '["function","recursion","basic_recursion","dfs"]', 1, 'active', 'Bob 喜欢图示和案例，推荐通过汉诺塔案例学习。', '2026-07-05 10:10:00'),
    ('P009', 'S003', 'G001', 'fast', '快速提升路径', '["recursion","basic_recursion","dfs","backtracking"]', 0, 'planned', '直接聚焦递归核心及进阶应用。', '2026-07-05 10:10:00');

INSERT INTO learning_events
    (event_id, student_id, node_id, event_type, result, score, time_spent, created_at)
VALUES
    (1, 'S001', 'function', 'finish', 'completed', 1.00, 300, '2026-07-05 17:30:00'),
    (2, 'S001', 'parameter', 'finish', 'completed', 0.90, 360, '2026-07-05 18:00:00'),
    (3, 'S001', 'return_value', 'learn', NULL, 0.55, 420, '2026-07-05 18:30:00'),
    (4, 'S002', 'function', 'finish', 'completed', 1.00, 120, '2026-07-05 17:20:00'),
    (5, 'S002', 'parameter', 'finish', 'completed', 1.00, 140, '2026-07-05 17:35:00'),
    (6, 'S002', 'return_value', 'finish', 'completed', 0.95, 150, '2026-07-05 17:50:00'),
    (7, 'S002', 'call_stack', 'finish', 'completed', 0.90, 180, '2026-07-05 18:10:00'),
    (8, 'S002', 'recursion', 'learn', NULL, 0.75, 210, '2026-07-05 18:35:00'),
    (9, 'S003', 'function', 'finish', 'completed', 0.80, 480, '2026-07-05 17:40:00'),
    (10, 'S003', 'parameter', 'learn', NULL, 0.60, 540, '2026-07-05 18:25:00');

INSERT INTO path_switch_logs
    (switch_id, student_id, old_path_id, new_path_id, trigger_type, trigger_signal_json, reason, created_at)
VALUES
    (
        1, 'S001', 'P002', 'P001', 'dialogue',
        '{"knowledge_gap":"call_stack","confusion_level":0.82,"action":"insert_return_value_review"}',
        '检测到调用栈理解困难，由案例驱动路径切换为基础补全路径。',
        '2026-07-05 20:00:00'
    ),
    (
        2, 'S002', 'P004', 'P006', 'quiz',
        '{"mastery":"high","action":"skip_recursion_review"}',
        'Alice 掌握度较高，由基础补全路径切换为快速提升路径。',
        '2026-07-05 20:05:00'
    );

INSERT INTO learning_resources
    (resource_id, node_id, title, resource_type, url, content, difficulty)
VALUES
    ('R001', 'variable', '变量基础讲解', 'text', '', '讲解变量定义、赋值与命名规则。', 1),
    ('R002', 'variable', '购物金额变量案例', 'code', '', '用商品价格与数量演示变量使用。', 1),
    ('R003', 'variable', '变量赋值练习', 'exercise', '', '完成变量创建和交换练习。', 1),
    ('R004', 'expression', '表达式工作原理', 'text', '', '讲解运算符优先级与表达式求值。', 1),
    ('R005', 'expression', '温度转换表达式案例', 'code', '', '通过温度转换理解表达式。', 1),
    ('R006', 'expression', '表达式求值练习', 'exercise', '', '判断多个表达式的计算结果。', 1),
    ('R007', 'condition', '条件语句讲解', 'text', '', '讲解 if、elif 和 else。', 2),
    ('R008', 'condition', '成绩等级判断案例', 'code', '', '使用条件语句判断成绩等级。', 2),
    ('R009', 'condition', '条件分支练习', 'exercise', '', '补全多分支判断程序。', 2),
    ('R010', 'loop', '循环结构讲解', 'text', '', '讲解 for 与 while 循环。', 2),
    ('R011', 'loop', '列表遍历案例', 'code', '', '遍历列表并统计元素。', 2),
    ('R012', 'loop', '循环控制练习', 'exercise', '', '练习 break、continue 与循环计数。', 2),
    ('R013', 'function', '函数基础讲解', 'text', '', '讲解函数定义、调用与作用域。', 2),
    ('R014', 'function', '问候函数案例', 'code', '', '编写可复用的问候函数。', 2),
    ('R015', 'function', '函数定义练习', 'exercise', '', '完成多个简单函数。', 2),
    ('R016', 'parameter', '参数传递讲解', 'text', '', '讲解形参、实参与位置参数。', 3),
    ('R017', 'parameter', '面积计算参数案例', 'code', '', '通过面积函数观察参数传递。', 3),
    ('R018', 'parameter', '参数匹配练习', 'exercise', '', '判断函数调用中的参数绑定。', 3),
    ('R019', 'return_value', '返回值工作原理', 'text', '', '区分 return 与 print。', 3),
    ('R020', 'return_value', '最大值函数案例', 'code', '', '通过最大值函数使用返回结果。', 3),
    ('R021', 'return_value', '返回值复习练习', 'exercise', '', '跟踪函数返回结果并修正程序。', 3),
    ('R022', 'call_stack', '调用栈工作原理', 'text', '', '讲解栈帧、返回位置与后进先出。', 4),
    ('R023', 'call_stack', '函数调用过程可视化', 'code', '', '可视化嵌套函数的入栈与出栈。', 4),
    ('R024', 'call_stack', '判断递归执行顺序', 'exercise', '', '根据调用栈判断递归输出顺序。', 4),
    ('R025', 'recursion', '递归思想讲解', 'text', '', '讲解问题分解、终止条件与递归调用。', 4),
    ('R026', 'recursion', '俄罗斯套娃递归案例', 'code', '', '通过层层嵌套理解递归思想。', 4),
    ('R027', 'recursion', '识别递归结构练习', 'exercise', '', '找出递归程序的终止条件和递归步骤。', 4),
    ('R028', 'basic_recursion', '基础递归程序讲解', 'text', '', '讲解阶乘和基础递归模板。', 4),
    ('R029', 'basic_recursion', '汉诺塔递归案例', 'code', '', '通过汉诺塔理解递归程序的调用过程。', 4),
    ('R030', 'basic_recursion', '递归程序编写练习', 'exercise', '', '编写阶乘与数列递归程序。', 4),
    ('R031', 'dfs', 'DFS 原理讲解', 'text', '', '讲解深度优先搜索与递归遍历。', 5),
    ('R032', 'dfs', '迷宫搜索案例', 'code', '', '使用 DFS 搜索迷宫路径。', 5),
    ('R033', 'dfs', '树遍历练习', 'exercise', '', '完成二叉树深度优先遍历。', 5),
    ('R034', 'backtracking', '回溯算法讲解', 'text', '', '讲解选择、递归和撤销选择。', 5),
    ('R035', 'backtracking', '全排列案例', 'code', '', '使用回溯生成全排列。', 5),
    ('R036', 'backtracking', '组合搜索练习', 'exercise', '', '完成组合问题的回溯程序。', 5);

INSERT INTO system_settings (setting_key, setting_value)
VALUES
    ('theme', 'light'),
    ('llm_provider', 'openai'),
    ('model_name', 'gpt-4.1-mini'),
    ('current_student_id', 'S001'),
    ('course_name', 'Python 程序设计'),
    ('learning_topic', '递归（Recursion）');

COMMIT;
