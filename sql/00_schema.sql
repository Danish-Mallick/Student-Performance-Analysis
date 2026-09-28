-- PostgreSQL-compatible, SQLite-compatible table definition.
-- The column order matches the supplied CSV exactly; psql COPY uses the CSV's position.
CREATE TABLE IF NOT EXISTS student_performance (
    hours_studied                INTEGER,
    attendance                   NUMERIC(5,2),
    parental_involvement         VARCHAR(10),
    access_to_resources         VARCHAR(10),
    extracurricular_activities  VARCHAR(3),
    sleep_hours                  NUMERIC(4,2),
    previous_scores              NUMERIC(5,2),
    motivation_level             VARCHAR(10),
    internet_access              VARCHAR(3),
    tutoring_sessions            INTEGER,
    family_income                VARCHAR(10),
    teacher_quality              VARCHAR(10),
    school_type                  VARCHAR(10),
    peer_influence               VARCHAR(10),
    physical_activity            INTEGER,
    learning_disabilities        VARCHAR(3),
    parental_education_level     VARCHAR(20),
    distance_from_home           VARCHAR(10),
    gender                       VARCHAR(10),
    exam_score                   NUMERIC(6,2)
);
