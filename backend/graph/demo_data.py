DEMO_DATASET = "copath_recursion_demo"

KNOWLEDGE_NODES = [
    {"id": "variable", "name": "变量", "english_name": "Variable", "description": "理解变量的定义、赋值与基本使用方式。", "difficulty": 1, "chapter": "Python基础", "type": "foundation"},
    {"id": "expression", "name": "表达式", "english_name": "Expression", "description": "理解运算符、表达式求值与基本数据运算。", "difficulty": 1, "chapter": "Python基础", "type": "foundation"},
    {"id": "condition", "name": "条件语句", "english_name": "Conditional Statement", "description": "使用条件判断控制程序执行分支。", "difficulty": 2, "chapter": "控制结构", "type": "foundation"},
    {"id": "loop", "name": "循环", "english_name": "Loop", "description": "使用循环结构重复执行代码。", "difficulty": 2, "chapter": "控制结构", "type": "foundation"},
    {"id": "function", "name": "函数", "english_name": "Function", "description": "理解函数定义、调用和代码复用。", "difficulty": 3, "chapter": "函数基础", "type": "core"},
    {"id": "parameter", "name": "参数传递", "english_name": "Parameter Passing", "description": "理解形参、实参与参数传递过程。", "difficulty": 3, "chapter": "函数基础", "type": "core"},
    {"id": "return_value", "name": "返回值", "english_name": "Return Value", "description": "理解函数返回值以及调用结果的使用方式。", "difficulty": 3, "chapter": "函数基础", "type": "remedial"},
    {"id": "call_stack", "name": "调用栈", "english_name": "Call Stack", "description": "调用栈用于记录函数调用过程。", "difficulty": 4, "chapter": "函数与递归", "type": "remedial"},
    {"id": "recursion_thinking", "name": "递归思想", "english_name": "Recursive Thinking", "description": "理解问题分解、递归调用与规模缩减。", "difficulty": 4, "chapter": "递归", "type": "core"},
    {"id": "base_case", "name": "递归出口", "english_name": "Base Case", "description": "理解递归终止条件以及缺少出口的风险。", "difficulty": 4, "chapter": "递归", "type": "core"},
    {"id": "basic_recursion", "name": "基础递归", "english_name": "Basic Recursion", "description": "能够阅读并编写基础递归程序。", "difficulty": 5, "chapter": "递归", "type": "target"},
    {"id": "hanoi", "name": "汉诺塔案例", "english_name": "Tower of Hanoi", "description": "通过汉诺塔案例观察递归分解与回溯过程。", "difficulty": 4, "chapter": "递归案例", "type": "example"},
    {"id": "tree_recursion", "name": "树形递归", "english_name": "Tree Recursion", "description": "理解一次调用产生多个递归分支的执行过程。", "difficulty": 5, "chapter": "递归进阶", "type": "advanced"},
    {"id": "dfs", "name": "DFS", "english_name": "Depth-First Search", "description": "使用递归实现树或图的深度优先遍历。", "difficulty": 5, "chapter": "搜索算法", "type": "advanced"},
    {"id": "backtracking", "name": "回溯", "english_name": "Backtracking", "description": "理解选择、递归与撤销选择组成的搜索过程。", "difficulty": 6, "chapter": "搜索算法", "type": "advanced"},
]

PREREQUISITE_RELATIONSHIPS = [
    ("variable", "expression"),
    ("expression", "condition"),
    ("condition", "loop"),
    ("loop", "function"),
    ("function", "parameter"),
    ("function", "return_value"),
    ("parameter", "call_stack"),
    ("return_value", "call_stack"),
    ("call_stack", "recursion_thinking"),
    ("recursion_thinking", "base_case"),
    ("base_case", "basic_recursion"),
    ("basic_recursion", "tree_recursion"),
    ("basic_recursion", "dfs"),
    ("tree_recursion", "backtracking"),
    ("dfs", "backtracking"),
]

EXAMPLE_SUPPORT_RELATIONSHIPS = [
    ("hanoi", "recursion_thinking"),
    ("hanoi", "basic_recursion"),
]

LEARNING_GOAL = {
    "id": "goal_recursion",
    "title": "掌握递归",
    "description": "理解递归思想、递归出口，并能编写基础递归程序。",
    "target_node_id": "basic_recursion",
}

LEARNING_RESOURCES = [
    {"id": f"graph_resource_{node['id']}", "node_id": node["id"], "title": f"{node['name']}学习资料", "resource_type": "text", "content": node["description"], "url": "", "difficulty": node["difficulty"]}
    for node in KNOWLEDGE_NODES
]

CANDIDATE_PATHS = [
    {"path_type": "basic", "path_name": "基础补全路径", "nodes": ["function", "parameter", "return_value", "call_stack", "recursion_thinking", "base_case", "basic_recursion"]},
    {"path_type": "example", "path_name": "案例驱动路径", "nodes": ["hanoi", "recursion_thinking", "base_case", "basic_recursion", "dfs"]},
    {"path_type": "fast", "path_name": "快速提升路径", "nodes": ["recursion_thinking", "base_case", "basic_recursion", "dfs", "backtracking"]},
]
