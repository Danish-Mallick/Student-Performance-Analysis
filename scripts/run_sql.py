"""Reproduce PostgreSQL project queries locally using the SQLite standard library.

The published .sql files target PostgreSQL (ROUND(AVG()::NUMERIC, 2)).
SQLite does not support PostgreSQL's :: cast; this local runner only strips that
one dialect-specific cast. All grouping/ranking logic is executed by SQL.
"""
import csv
import re
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SQL=ROOT/'sql'
RESULTS=ROOT/'results'
QUERIES={
    '01_avg_exam_score_by_study_and_extracurricular.sql':'q1_study_and_extracurricular_sql.csv',
    '02_avg_exam_score_by_hours_studied_range.sql':'q2_study_ranges_sql.csv',
    '03_exam_ranking.sql':'q3_top30_rank_sql.csv',
    '04_attendance_study_interaction.sql':'q4_attendance_study_sql.csv',
    '05_tutoring_within_study_ranges.sql':'q5_tutoring_sql.csv',
    '06_sleep_hours.sql':'q6_sleep_sql.csv',
    '07_teacher_quality.sql':'q7_teacher_sql.csv',
    '08_data_quality.sql':'q8_validation_sql.csv',
}

def connection():
    db=sqlite3.connect(':memory:')
    db.executescript((SQL/'00_schema.sql').read_text(encoding='utf8'))
    with (ROOT/'data'/'StudentPerformanceFactors.csv').open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        cols=[k.lower() for k in reader.fieldnames]
        rows=[tuple(None if row[k]=='' else row[k] for k in reader.fieldnames) for row in reader]
    db.executemany('INSERT INTO student_performance ('+', '.join(cols)+') VALUES ('+', '.join('?' for _ in cols)+')',rows)
    db.commit()
    return db

def sqlite_sql(query_file):
    sql=(SQL/query_file).read_text(encoding='utf8')
    return re.sub(r'AVG\(exam_score\)::NUMERIC', 'AVG(exam_score)', sql,flags=re.I)

def main():
    RESULTS.mkdir(exist_ok=True)
    db=connection()
    for filename,out in QUERIES.items():
        c=db.execute(sqlite_sql(filename))
        rows=c.fetchall()
        with (RESULTS/out).open('w',encoding='utf8',newline='') as f:
            w=csv.writer(f); w.writerow([d[0] for d in c.description]);w.writerows(rows)
        print(f'{filename}: {len(rows)} rows -> {out}')
    assert db.execute('SELECT COUNT(*) FROM student_performance').fetchone()[0]==6607
    assert len(db.execute(sqlite_sql(next(iter(QUERIES)))).fetchall())==30
    assert len(db.execute(sqlite_sql(list(QUERIES)[1])).fetchall())==4
    rows=db.execute(sqlite_sql(list(QUERIES)[2])).fetchall()
    assert len(rows)==30 and all(rows[i][4]<=rows[i+1][4] for i in range(29))
    q8=db.execute(sqlite_sql('08_data_quality.sql')).fetchone()
    assert q8[:5]==(6607,78,90,67,1),f'Quality check failed: {q8}'
    print('PASS: original questions produce 30, 4, and 30 rows; quality checks passed.')
    db.close()
if __name__=='__main__':main()
