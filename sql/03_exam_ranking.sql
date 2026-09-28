-- Q3: Ties share the same rank, with no gaps. Exam scores remain hidden.
-- Extra sort columns make selection at the 30-row limit reproducible across ties.
SELECT
    attendance,
    hours_studied,
    sleep_hours,
    tutoring_sessions,
    DENSE_RANK() OVER (ORDER BY exam_score DESC) AS exam_rank
FROM student_performance
ORDER BY exam_rank ASC,
         attendance DESC,
         hours_studied DESC,
         sleep_hours DESC,
         tutoring_sessions DESC
LIMIT 30;
