CREATE TABLE IF NOT EXISTS lucas_ci_smoke (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL
);

INSERT INTO lucas_ci_smoke (id, label)
VALUES (1, 'migration-ok')
ON CONFLICT (id) DO UPDATE SET label = EXCLUDED.label;