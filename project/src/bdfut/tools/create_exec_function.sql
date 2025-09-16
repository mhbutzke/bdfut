-- Primeiro execute esta função no Supabase SQL Editor
CREATE OR REPLACE FUNCTION exec_sql(sql text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    EXECUTE sql;
    RETURN 'SQL executed successfully';
END;
$$;
