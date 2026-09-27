-- Candidate Technical Profiling Schema
CREATE TABLE IF NOT EXISTS candidates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    university TEXT NOT NULL,
    degree TEXT NOT NULL,
    gpa REAL,
    grad_year INTEGER,
    target_role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT NOT NULL,
    category TEXT NOT NULL, -- 'Language', 'AI/ML', 'Cloud/Infra', 'Algorithms', 'Databases'
    skill_name TEXT NOT NULL,
    proficiency_level TEXT NOT NULL, -- 'Expert', 'Proficient', 'Working'
    verified INTEGER DEFAULT 1, -- 1 = verified ground truth, 0 = unverified claim
    proof_details TEXT,
    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT NOT NULL,
    title TEXT NOT NULL,
    primary_stack TEXT NOT NULL,
    metrics_summary TEXT NOT NULL,
    is_production INTEGER DEFAULT 0,
    repo_url TEXT,
    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT NOT NULL,
    domain TEXT NOT NULL, -- 'DSA', 'System Design', 'AI Engineering'
    metric_label TEXT NOT NULL, -- e.g. 'LeetCode Knight', 'Codeforces Specialist'
    score_percentile REAL,
    problems_solved INTEGER,
    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT NOT NULL,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    duration TEXT NOT NULL,
    highlights TEXT,
    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
);
