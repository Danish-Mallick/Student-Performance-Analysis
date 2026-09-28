# Power BI Desktop: build the interactive report

**Goal:** reproduce the finished visuals as a filterable 4-page `.pbix` using the prepared 6,607-row dataset. The ZIP includes the complete model-ready CSV, all DAX definitions, theme, a concept mock-up and the static charts. **A real `.pbix` is not included**: it must be saved from your local Power BI Desktop after these steps.

## 1 | Load the source (about 4 clicks)

1. Unzip the repository, open **Power BI Desktop** and choose **Home > Get data > Text/CSV**.
2. Select `powerbi/student_performance_powerbi.csv`. Then choose **Transform data** to inspect types before loading.
3. In Power Query, rename the query to exactly **`Student Performance`**. Confirm `Student_ID`, `Hours_Studied`, `Attendance`, `Exam_Score`, `Study_Range_Order`, `Attendance_Band_Order`, `Tutoring_Sessions` are **Whole number**. (The provided file contains integers in these fields.) Leave categories as Text. Select **Close & Apply**.
4. To preserve natural ordering: select the `Study_Hours_Range` column, select **Column tools > Sort by column > Study_Range_Order**. Repeat for `Attendance_Band` sorted by `Attendance_Band_Order`.
5. Optional reproducible transformation: `01_power_query_optional.m` imports the same CSV with explicit types. Update `CsvPath` and use **Home > Transform data > Advanced Editor** to replace the query; not needed if steps 1–4 worked.

**Why one table?** This is one observation-level CSV with no real student keys or date dimension. A single-table model avoids artificial relationships. `Student_ID` is only the stable row number assigned during preparation, not an actual student identity.

## 2 | Apply the visual theme

Go to **View > Themes > Browse for themes**. Select `powerbi/power_bi_theme.json`. Use a 16:9 page and keep consistent left-aligned titles, slicers on a narrow left rail and small, readable chart labels.

## 3 | Add the measures

Create each expression from `dax_measures.dax` **separately**: select the `Student Performance` table in the Data pane, then **Modeling > New measure**. Do not paste the entire `.dax` file as one formula. Set `Avg Exam Score` and other score measures to **2 decimals**. Format `Avg Attendance %`, `Tutoring Share %`, `High Attendance Share %` as **Percentage, 1 decimal**. All measures respect active filters except where `REMOVEFILTERS` is explicitly used (see comments).

## 4 | Build these four report pages

### PAGE 1 — Executive overview (the landing page)

| Visual | Fields / setup | Purpose |
|---|---|---|
| Card: Students | `Student Count` | Sample size under filters |
| Card: Average score | `Avg Exam Score` | Current cohort's average |
| Card: Avg weekly study hours | `Avg Study Hours` | Context for filtered cohort |
| Card: Avg attendance | `Avg Attendance %` | Context for filtered cohort |
| Clustered column chart | X: `Study_Hours_Range`; Y: `Avg Exam Score`; Tooltip: `Student Count` | Performance across study bands |
| Column chart | X: `Attendance_Band`; Y: `Avg Exam Score`; Tooltip: `Student Count` | Attendance gradient |
| Small text panel | "Descriptive trends only. Data are synthetic; filters affect the mix of students." | Responsible reading |

Add slicers for `Extracurricular_Activities` and `Teacher_Quality` in a left rail. Set study and attendance chart Y axes to start at zero **for the overview**. Use the imported ordering columns.

### PAGE 2 — Attendance × study habits (the investigative page)

| Visual | Fields / setup | Purpose |
|---|---|---|
| Matrix heatmap | Rows: `Attendance_Band`; Columns: `Study_Hours_Range`; Values: `Avg Exam Score`; apply *background color conditional formatting* | Joint association |
| Matrix tooltip | Add `Student Count` in Values if tooltip support is limited; otherwise report tooltip page | Averages in small cells need counts |
| Clustered columns | X: `Study_Hours_Range`; Legend: `Extracurricular_Activities`; Y: `Avg Exam Score`; Tooltip: `Student Count` | Participation within study groups |
| Scatter plot (optional) | X: `Hours_Studied`; Y: `Exam_Score`; Details: `Student_ID` if your version exposes the Details well; alternatively use a line chart with mean score by `Hours_Studied` | Underlying spread instead of just averages |

Include a footnote: **"No causal inference; the 1–5-hour group is relatively small (59 records overall)."** If the scatter uses 6,607 points, turn down marker size and test readability; the aggregate line is an easier first version.

### PAGE 3 — Tutoring, sleep and support

| Visual | Fields / setup | Purpose |
|---|---|---|
| Clustered column chart | X: `Study_Hours_Range`; Legend: `Tutoring_Group`; Y: `Avg Exam Score`; Tooltip: `Student Count` | Compare tutoring within study groups |
| Line + markers | X: `Sleep_Hours`; Y: `Avg Exam Score`; Tooltip: `Student Count` | Check near-flat sleep pattern |
| Bar chart | Y: `Teacher_Quality`; X: `Avg Exam Score`; Tooltip: `Student Count` | Include `Unknown`, not just known teachers |
| Card | `Observed Tutoring Score Gap` (label: **Observed gap**) | Responds to study and attendance slicers but not tutoring-group slicer |

For the sleep chart use clearly labeled scores, and **do not zoom the y-axis without a visible "zoomed axis" note**. Preserve category counts as tooltips and avoid treating the tutoring gap as a causal benefit.

### PAGE 4 — Data quality / methodology

| Visual | Fields / setup | Purpose |
|---|---|---|
| Card | `Score Quality Flags` | One source score is 101 (outside expected 0–100 range) |
| Table | `Score_Quality_Flag`, `Student Count`, `Avg Exam Score` | Visibility of flagged observations |
| Two cards | `Avg Exam Score`, `Avg Score (Within 0-100)` | Check sensitivity to the out-of-range score |
| Text box | Missing categorical values in the raw file: teacher quality **78**, parental education **90**, distance from home **67**. These are labeled `Unknown` in the Power BI extract. | Transparent cleaning |
| Text box | Dataset: Kaggle "Student Performance Factors" (Lai Nguyen); synthetic; observational; no causal claims. | Provenance / limitations |

### Report interaction checklist

- Sync `Extracurricular_Activities`, `Teacher_Quality` and optional `Score_Quality_Flag` slicers across pages as intended (**View > Sync slicers**).
- Click a category in a chart and verify the KPI cards change. If cross-highlighting makes the story confusing, use **Format > Edit interactions**.
- Sort the teacher bar based on average score only if you intentionally want this ordering; keep `Unknown` included.
- Use tooltips containing **Student Count** on every aggregated visual; a single-record subgroup should never look as reliable as a large one.
- Export to PDF as an optional reviewer-friendly copy. Save your final file to `powerbi/Student_Performance_Analysis.pbix`.
- Once your local `.pbix` is built, **commit it to GitHub** if you want other Power BI Desktop users to open the interactive report, subject to file-size limits.

## 5 | Reproducibility and QA

- Expected rows after load: **6,607**.
- Expected overall average: **67.23566** (display **67.24**).
- Source flags: **1 record with score 101**. Core coursework SQL and main dashboard **retain the row**, and an explicit quality flag allows sensitivity comparisons; do not silently alter the result.
- Expected study groups: **59**, **306**, **1,140**, **5,102** from shortest to longest weekly study ranges.
- The source has **no time variable**. Do not invent a time series, forecast timeline or year-over-year chart.

## If you want a truly clickable .pbix

Everything except the final Power BI Desktop file is already created in this repository. Work through pages 1–4 in order and save the `.pbix` locally. If you'd like to review it together later, share a screenshot or your `.pbix` file after saving.

**Microsoft reference documentation:**
- https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-calculations-options
- https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures
- https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-query-overview
