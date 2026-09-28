-- BONUS: Descriptive sleep-hour breakdown with counts.
SELECT
    sleep_hours, COUNT(*) AS students,
    ROUND(AVG(exam_score)::NUMERIC, 2) AS avg_exam_score
FROM student_performance
GROUP BY sleep_hours
ORDER BY sleep_hours;
