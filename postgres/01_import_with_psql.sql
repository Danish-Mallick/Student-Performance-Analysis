-- Execute from the repository root AFTER creating the table with sql/00_schema.sql.
-- Example: psql -d YOUR_DATABASE -f postgres/01_import_with_psql.sql
-- The CSV uses Title_Case headers but columns match by POSITION here.
\copy student_performance FROM 'data/StudentPerformanceFactors.csv' WITH (FORMAT csv, HEADER true, NULL '');
