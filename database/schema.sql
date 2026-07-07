PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE IF NOT EXISTS knowledge_nodes (
    node_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    chapter TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_goals (
    goal_id TEXT PRIMARY KEY,
    target_node_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    recommended_level TEXT NOT NULL,
    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes (node_id)
);

CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    avatar TEXT,
    current_goal_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_goal_id) REFERENCES learning_goals (goal_id)
);

CREATE TABLE IF NOT EXISTS student_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    learning_speed TEXT NOT NULL
        CHECK (learning_speed IN ('slow', 'medium', 'fast')),
    learning_preference TEXT NOT NULL
        CHECK (learning_preference IN ('basic', 'example', 'fast')),
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    mastery_json TEXT NOT NULL DEFAULT '{}',
    profile_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);

CREATE TABLE IF NOT EXISTS knowledge_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation TEXT NOT NULL DEFAULT 'prerequisite',
    FOREIGN KEY (source_id) REFERENCES knowledge_nodes (node_id),
    FOREIGN KEY (target_id) REFERENCES knowledge_nodes (node_id),
    UNIQUE (source_id, target_id, relation)
);

CREATE TABLE IF NOT EXISTS learning_paths (
    path_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    goal_id TEXT NOT NULL,
    path_type TEXT NOT NULL CHECK (path_type IN ('basic', 'example', 'fast')),
    path_name TEXT NOT NULL,
    nodes_json TEXT NOT NULL,
    is_current INTEGER NOT NULL DEFAULT 0 CHECK (is_current IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'active', 'completed', 'switched')),
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (goal_id) REFERENCES learning_goals (goal_id)
);

CREATE TABLE IF NOT EXISTS learning_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('learn', 'quiz', 'finish', 'pause')),
    result TEXT,
    score REAL,
    time_spent INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

CREATE TABLE IF NOT EXISTS dialogue_logs (
    dialogue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    extracted_signal_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

CREATE TABLE IF NOT EXISTS path_switch_logs (
    switch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    old_path_id TEXT NOT NULL,
    new_path_id TEXT NOT NULL,
    trigger_type TEXT NOT NULL
        CHECK (trigger_type IN ('dialogue', 'quiz', 'time', 'manual')),
    trigger_signal_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (old_path_id) REFERENCES learning_paths (path_id),
    FOREIGN KEY (new_path_id) REFERENCES learning_paths (path_id)
);

CREATE TABLE IF NOT EXISTS path_adjustment_suggestions (
    suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    current_path_id TEXT NOT NULL,
    suggested_path_type TEXT NOT NULL
        CHECK (suggested_path_type IN ('basic', 'example', 'fast')),
    suggested_nodes_json TEXT NOT NULL,
    trigger_type TEXT NOT NULL
        CHECK (trigger_type IN ('dialogue', 'quiz', 'time', 'manual')),
    trigger_signal_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    risk_level TEXT NOT NULL
        CHECK (risk_level IN ('low', 'medium', 'high')),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'rejected', 'overridden', 'applied')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (current_path_id) REFERENCES learning_paths (path_id)
);

CREATE TABLE IF NOT EXISTS learning_resources (
    resource_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    title TEXT NOT NULL,
    resource_type TEXT NOT NULL
        CHECK (resource_type IN ('video', 'text', 'exercise', 'code')),
    url TEXT,
    content TEXT,
    difficulty INTEGER NOT NULL,
    FOREIGN KEY (node_id) REFERENCES knowledge_nodes (node_id)
);

CREATE TABLE IF NOT EXISTS system_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_knowledge_edges_source_id
    ON knowledge_edges (source_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_edges_target_id
    ON knowledge_edges (target_id);
CREATE INDEX IF NOT EXISTS ix_learning_goals_target_node_id
    ON learning_goals (target_node_id);
CREATE INDEX IF NOT EXISTS ix_learning_paths_student_id
    ON learning_paths (student_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_learning_paths_current_student
    ON learning_paths (student_id)
    WHERE is_current = 1;
CREATE INDEX IF NOT EXISTS ix_learning_events_student_id
    ON learning_events (student_id);
CREATE INDEX IF NOT EXISTS ix_dialogue_logs_student_id
    ON dialogue_logs (student_id);
CREATE INDEX IF NOT EXISTS ix_path_switch_logs_student_id
    ON path_switch_logs (student_id);
CREATE INDEX IF NOT EXISTS ix_path_adjustment_suggestions_student_status
    ON path_adjustment_suggestions (student_id, status);
CREATE INDEX IF NOT EXISTS ix_learning_resources_node_id
    ON learning_resources (node_id);

COMMIT;
