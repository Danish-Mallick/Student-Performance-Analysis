-- BONUS: Compare tutoring groups within study-hour strata.
-- Study-hour stratification does NOT control for all other differences.
WITH groups AS (
    SELECT
        CASE
            WHEN hours_studied BETWEEN 1 AND 5 THEN '1-5 hours'
            WHEN hours_studied BETWEEN 6 AND 10 THEN '6-10 hours'
            WHEN hours_studied BETWEEN 11 AND 15 THEN '11-15 hours'
            ELSE '16+ hours'
        END AS hours_studied_range,
        CASE WHEN tutoring_sessions > 0 THEN '1+ sessions' ELSE 'No tutoring' END AS tutoring_group,
        exam_score
    FROM student_performance
    WHERE hours_studied >= 1
)
SELECT
    hours_studied_range, tutoring_group,
    COUNT(*) AS students,
    ROUND(AVG(exam_score)::NUMERIC, 2) AS avg_exam_score
FROM groups
GROUP BY hours_studied_range, tutoring_group
ORDER BY
    CASE hours_studied_range
      WHEN '1-5 hours' THEN 1 WHEN '6-10 hours' THEN 2
      WHEN '11-15 hours' THEN 3 ELSE 4 END,
    tutoring_group;
