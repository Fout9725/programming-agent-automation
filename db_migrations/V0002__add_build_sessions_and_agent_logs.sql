
CREATE TABLE IF NOT EXISTS build_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id INTEGER REFERENCES projects(id),
    user_query TEXT NOT NULL,
    project_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'started',
    current_step VARCHAR(100),
    spec JSONB,
    generated_files JSONB DEFAULT '{}'::jsonb,
    validation_issues JSONB DEFAULT '[]'::jsonb,
    fix_iterations INTEGER DEFAULT 0,
    error_message TEXT,
    app_url VARCHAR(500),
    github_url VARCHAR(500),
    ai_model_used VARCHAR(100),
    tokens_used INTEGER DEFAULT 0,
    cost_usd NUMERIC(10,4) DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_build_sessions_project_id ON build_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_build_sessions_status ON build_sessions(status);

CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES build_sessions(id),
    agent_role VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_logs_session_id ON agent_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_role ON agent_logs(agent_role);
