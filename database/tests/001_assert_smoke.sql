DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM lucas_ci_smoke
        WHERE id = 1 AND label = 'migration-ok'
    ) THEN
        RAISE EXCEPTION 'Lucas SQL smoke test failed';
    END IF;
END
$$;