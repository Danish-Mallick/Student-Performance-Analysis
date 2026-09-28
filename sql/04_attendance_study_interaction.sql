-- BONUS: Are attendance and study hours associated with score differences together?
-- Four transparent comparison groups; not a causal estimate.
WITH groups AS (
    SELECT
        CASE WHEN hours_studied >= 16 THEN '16+ hours' ELSE '<16 hours' END AS study_group,
        CASE WHEN attendance >= 80 THEN '80%+' ELSE '<80%' END AS attendance_group,
        exam_score
    FROM student_performance
)
SELECT
    study_group, attendance_group, COUNT(*) AS students,
    ROUND(AVG(exam_score)::NUMERIC, 2) AS avg_exam_score
FROM groups
GROUP BY study_group, attendance_group
ORDER BY study_group, attendance_group;
