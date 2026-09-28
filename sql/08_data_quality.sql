-- Validation: synthetic source has 3 partially missing text fields and one score >100.
SELECT
    COUNT(*) AS records,
    SUM(CASE WHEN teacher_quality IS NULL THEN 1 ELSE 0 END) AS missing_teacher_quality,
    SUM(CASE WHEN parental_education_level IS NULL THEN 1 ELSE 0 END) AS missing_parental_education,
    SUM(CASE WHEN distance_from_home IS NULL THEN 1 ELSE 0 END) AS missing_distance_from_home,
    SUM(CASE WHEN exam_score > 100 THEN 1 ELSE 0 END) AS scores_over_100,
    MIN(hours_studied) AS min_study_hours,
    MAX(hours_studied) AS max_study_hours
FROM student_performance;
