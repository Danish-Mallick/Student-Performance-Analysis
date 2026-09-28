# Publishing checklist (GitHub)

## Suggested repository metadata

- **Repository name:** `student-performance-sql-python-powerbi`
- **Description:** `End-to-end student exam performance analysis using PostgreSQL, Python, and a Power BI dashboard. Includes validated SQL, EDA, and reproducible reporting.`
- **Topics:** `sql`, `postgresql`, `python`, `pandas`, `power-bi`, `data-analysis`, `data-visualization`, `education-analytics`, `portfolio-project`

## Before publication

1. **Review the analysis.** Open the 5-page PDF and notebook; confirm every sentence matches your own understanding. Portfolio projects are more useful when you can clearly explain the choices at interview.
2. **Confirm original data license** at the Kaggle source linked in `DATA_SOURCE_NOTE.md` before making both original and derived row-level CSV files public. If required, remove the raw dataset and the model-ready derived dataset and replace them with download-and-regenerate instructions.
3. **Finish the native Power BI report** by following `powerbi/POWER_BI_BUILD_GUIDE.md`. Save your actual `.pbix` in `powerbi/`. Replace `dashboard_design_mockup.png` with a **separately named real screenshot**; keep the mock-up clearly labeled until then. Update the README to link to the actual `.pbix` once it exists.
4. **Run tests again** after any edits: `python -m unittest discover -s tests -v`.

## Publish using Git

After unzipping the project, open a terminal **inside the extracted project folder**. Create an empty GitHub repository with the suggested name, *without* initializing another README, then run:

```bash
git init
git add .
git commit -m "Add student performance SQL, Python and Power BI portfolio"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_URL` with the URL of the empty repository you created. If you prefer not to use Git commands, you can use GitHub Desktop and publish the local folder.

## GitHub first impressions

- The repository README already has a visual hero, main research question, findings, actual chart images and fast navigation to the notebook, SQL, PDF and Power BI instructions.
- **Pin** the completed repository on your GitHub profile.
- In your CV, describe actual work rather than "proving what really drives performance": e.g., *Analyzed 6,607 synthetic student records with PostgreSQL and pandas, validated eight SQL queries, developed grouped analytical visuals and prepared an interactive Power BI dashboard with filter-aware DAX measures.* Change "prepared" to "built" **only after your actual PBIX is finished**.
- Retain the caveat that associations in synthetic data are descriptive, not causal.
