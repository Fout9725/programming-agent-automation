-- Таблица проектов
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) NOT NULL,
    technologies JSONB DEFAULT '[]'::jsonb,
    github_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица версий изменений (для отката)
CREATE TABLE IF NOT EXISTS project_versions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    version_number INTEGER NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    change_description TEXT,
    files_changed JSONB DEFAULT '[]'::jsonb,
    diff_content TEXT,
    ai_model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица файлов проекта
CREATE TABLE IF NOT EXISTS project_files (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    file_path VARCHAR(500) NOT NULL,
    content TEXT,
    file_type VARCHAR(50),
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, file_path)
);

-- Таблица анализа кода
CREATE TABLE IF NOT EXISTS code_analysis (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    quality_score INTEGER,
    performance_score INTEGER,
    security_score INTEGER,
    readability_score INTEGER,
    issues_found JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_project_versions_project_id ON project_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_project_files_project_id ON project_files(project_id);
CREATE INDEX IF NOT EXISTS idx_code_analysis_project_id ON code_analysis(project_id);
