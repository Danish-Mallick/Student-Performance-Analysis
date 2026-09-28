-- Q1: Study hours >10 AND participation in extracurricular activities.
-- Expected output: hours_studied, avg_exam_score; sorted by hours_studied DESC.
SELECT
    hours_studied,
    ROUND(CAST(AVG(exam_score) AS NUMERIC), 2) AS avg_exam_score
FROM student_performance
WHERE hours_studied > 10
  AND extracurricular_activities = 'Yes'
GROUP BY hours_studied
ORDER BY hours_studied DESC;
