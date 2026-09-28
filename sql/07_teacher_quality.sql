-- BONUS: Preserve missing teacher-quality entries as Unknown, never silently drop.
SELECT
    COALESCE(teacher_quality,'Unknown') AS teacher_quality,
    COUNT(*) AS students,
    ROUND(AVG(exam_score)::NUMERIC, 2) AS avg_exam_score
FROM student_performance
GROUP BY COALESCE(teacher_quality,'Unknown')
ORDER BY teacher_quality;
