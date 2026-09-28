"""Reproducible integrity tests for the original question outputs and BI extract."""
import sys
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.run_sql import connection, sqlite_sql

class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=connection()
        cls.source=pd.read_csv(ROOT/'data'/'StudentPerformanceFactors.csv')
        cls.pbi=pd.read_csv(ROOT/'powerbi'/'student_performance_powerbi.csv')

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_original_q1_exact_shape_and_filter(self):
        cursor=self.db.execute(sqlite_sql('01_avg_exam_score_by_study_and_extracurricular.sql'))
        data=cursor.fetchall()
        self.assertEqual([d[0] for d in cursor.description],['hours_studied','avg_exam_score'])
        self.assertEqual(len(data),30)
        self.assertTrue(all(data[i][0]>data[i+1][0] for i in range(29)))
        self.assertTrue(all(t[0]>10 for t in data))
        subset=self.source.query('Hours_Studied > 10 and Extracurricular_Activities == "Yes"')
        self.assertEqual(subset.Hours_Studied.nunique(),30)
        for hours, avg in data:
            expected=subset.loc[subset.Hours_Studied==hours,'Exam_Score'].mean()
            self.assertAlmostEqual(avg,expected,places=2)

    def test_original_q2_4_groups_and_totals(self):
        c=self.db.execute(sqlite_sql('02_avg_exam_score_by_hours_studied_range.sql'))
        data=c.fetchall()
        self.assertEqual([d[0] for d in c.description],['hours_studied_range','avg_exam_score'])
        self.assertEqual(len(data),4)
        self.assertEqual([n for n,_ in data],['16+ hours','11-15 hours','6-10 hours','1-5 hours'])
        self.assertAlmostEqual(data[0][1],67.92,places=2)
        b=pd.read_csv(ROOT/'results'/'study_range_summary.csv')
        self.assertEqual(int(b.students.sum()),6607)

    def test_original_q3_dense_rank(self):
        c=self.db.execute(sqlite_sql('03_exam_ranking.sql'))
        data=c.fetchall()
        self.assertEqual([d[0] for d in c.description],['attendance','hours_studied','sleep_hours','tutoring_sessions','exam_rank'])
        self.assertEqual(len(data),30)
        ranks=[row[-1] for row in data]
        self.assertEqual(sorted(set(ranks)),list(range(1,max(ranks)+1)))
        self.assertEqual(ranks,sorted(ranks))
        full=self.db.execute('SELECT exam_score, DENSE_RANK() OVER (ORDER BY exam_score DESC) AS r FROM student_performance').fetchall()
        mapping={}
        for score,rank in full:
            self.assertEqual(mapping.setdefault(score,rank),rank)

    def test_bi_grain_flags_missing(self):
        self.assertEqual(self.source.shape,(6607,20))
        self.assertEqual(self.pbi.shape,(6607,27))
        self.assertEqual(len(self.pbi.Student_ID.unique()),6607)
        self.assertEqual(int(self.pbi.Score_Quality_Flag.eq('Above 100').sum()),1)
        self.assertEqual(int(self.pbi.Teacher_Quality.eq('Unknown').sum()),78)
        self.assertEqual(int(self.pbi.Parental_Education_Level.eq('Unknown').sum()),90)
        self.assertEqual(int(self.pbi.Distance_from_Home.eq('Unknown').sum()),67)
        self.assertTrue(self.pbi.isna().sum().eq(0).all())
        self.assertAlmostEqual(self.pbi.Exam_Score.mean(),self.source.Exam_Score.mean(),places=6)

    def test_summary_matrices_complete(self):
        data=pd.read_csv(ROOT/'results'/'attendance_x_study_matrix.csv')
        self.assertEqual(len(data),16)
        self.assertEqual(int(data.students.sum()),6607)
        self.assertEqual(int(pd.read_csv(ROOT/'results'/'tutoring_by_study_range.csv').students.sum()),6607)
        self.assertEqual(int(pd.read_csv(ROOT/'results'/'sleep_summary.csv').students.sum()),6607)

if __name__=='__main__':unittest.main()
