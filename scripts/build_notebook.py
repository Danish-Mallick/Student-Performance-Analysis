"""Build and execute a reviewer-friendly notebook with actual output tables/charts."""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
nb=nbf.v4.new_notebook()
nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}}
m=lambda s: nbf.v4.new_markdown_cell(s)
c=lambda s: nbf.v4.new_code_cell(s)
nb.cells=[
 m('''# Student performance | A reproducible analysis\n\n**Research question:** What relationships are visible between study habits, attendance, educational support, and exam performance?\n\nThis notebook reproduces the **three original SQL assignment questions** and extends them with more detailed group comparisons, sample sizes, and a simple held-out predictive illustration. The 6,607 observations form a **synthetic, observational dataset**, so these relationships do not establish causality.'''),
 c('''from pathlib import Path
import sys
ROOT = Path.cwd().resolve()
if not (ROOT / "data" / "StudentPerformanceFactors.csv").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
import pandas as pd
from IPython.display import display, Image
from scripts.analyze import load, summaries, model
from scripts.run_sql import connection, sqlite_sql
raw, prepared = load()
print(f"Records: {len(raw):,} | Original fields: {len(raw.columns)} | Average score: {raw.Exam_Score.mean():.2f}")
display(raw.head(4))'''),
 m('''## 1. Data quality before analysis\n\nWe keep the original exam scores intact so the original SQL answers remain reproducible. Three original categorical fields are partially missing and become **Unknown** in the Power BI export. **One score is 101**, which lies outside an expected 0–100 scale; the prepared dataset exposes this with a quality flag and sensitivity comparison.'''),
 c('''qa = pd.DataFrame({"missing_raw": raw.isna().sum()}).query("missing_raw > 0")
display(qa)
print("Source scores > 100:", int((raw.Exam_Score > 100).sum()))
print("Average with flagged row:", round(raw.Exam_Score.mean(),4))
print("Average excluding flagged row:", round(raw.loc[raw.Exam_Score <= 100,"Exam_Score"].mean(),4))'''),
 m('''## 2. Original DataCamp questions: run the actual SQL\n\nThe SQL files under `sql/` target **PostgreSQL**. Here we run the same logic locally with **SQLite**. The runner only removes PostgreSQL's dialect-specific `::NUMERIC` cast before evaluation. The ranking query never exposes exam scores in its final output.'''),
 c('''db = connection()
queries = [
    ("Q1: hours > 10 + extracurricular participation", "01_avg_exam_score_by_study_and_extracurricular.sql", 30),
    ("Q2: study-hour ranges", "02_avg_exam_score_by_hours_studied_range.sql", 4),
    ("Q3: dense exam ranking (top 30)", "03_exam_ranking.sql", 30),
]
for title, filename, expected_count in queries:
    output = pd.read_sql_query(sqlite_sql(filename), db)
    assert len(output) == expected_count
    print(f"\\n{title}: {len(output)} output rows")
    display(output.head(5))'''),
 m('''## 3. The main story: attendance and study hours\n\nShorter study groups are much smaller, so every visualization and table also shows **the number of records**. The next comparison combines both habits rather than considering them in isolation.'''),
 c('''results = summaries(raw, prepared)
display(results["group"].round(2))
display(results["att"].round(2))
display(results["case"].round(2))
display(Image(filename=str(ROOT/"charts"/"03_attendance_study_heatmap.png")))'''),
 m('''## 4. Check alternative explanations: tutoring and sleep\n\nThe tutoring comparison is **stratified by study hours**; it is still observational and is not a matched trial. Sleep-hour means are nearly flat in this particular dataset; avoid inventing a strong pattern where none appears.'''),
 c('''display(results["tutor"].round(2))
display(Image(filename=str(ROOT/"charts"/"04_tutoring.png")))
display(results["sleep"][["Sleep_Hours","students","avg_score"]].round(2))
display(Image(filename=str(ROOT/"charts"/"05_sleep.png")))'''),
 m('''## 5. Numerical associations\n\nPearson's *r* summarizes **linear association** only; it cannot measure causality or isolate overlapping mechanisms. Variable scales, confounders and the synthetic nature of the source limit any generalization.'''),
 c('''display(results["corr"].rename("Pearson r").to_frame().round(3))
display(Image(filename=str(ROOT/"charts"/"06_correlations.png")))'''),
 m('''## 6. Optional predictive demonstration (not for student-level decision-making)\n\nFor reproducibility, train/test records are selected with `random_state=42` and an **80/20 random split**. The simple ridge-regression comparison evaluates prediction in held-out rows of this synthetic dataset. Predictive fit is **not** evidence that an input causes an outcome; neither model should be used to assess actual students.'''),
 c('''holdout = model(raw)
display(pd.DataFrame(holdout).round(3))
print("Compare these values against results/optional_holdout_model.csv")'''),
 m('''## Conclusion and limitations\n\n- **Attendance and weekly study hours** show clear positive unadjusted associations with score in these records.\n- **Tutoring** differences remain visible inside study-hour bins, but many other attributes can differ between the groups.\n- **Sleep hours** show little linear correlation with exam scores in these records. This does **not** show that sleep is unimportant in real life.\n- Original coursework results deliberately retain the **single score of 101**; data quality is explicit, not silently altered.\n- **This synthetic dataset is not a representative causal experiment.** Treat recommendations as hypotheses for further investigation, not policy prescriptions.\n\nThe interactive companion is prepared in `powerbi/` with DAX measures, a theme and step-by-step build instructions.''')
]
out=ROOT/'notebooks'/'student_performance_analysis.ipynb'
try:
    executed=NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
    nbf.write(executed,out)
    print('Executed',out,'cells:',len(executed.cells))
except Exception:
    nbf.write(nb,out)
    raise
