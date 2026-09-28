"""Create attractive static recruiter-facing HTML/PDF and a clearly labeled PBI wireframe."""
from pathlib import Path
import json, html
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT=Path(__file__).resolve().parents[1]
CH=ROOT/'charts'; REPORT=ROOT/'report'; BI=ROOT/'powerbi';REPORT.mkdir(exist_ok=True)
M=json.loads((ROOT/'results'/'project_metrics.json').read_text())
NAVY='#12263A';BLUE='#2176AE';TEAL='#129E91';GRAY='#566574';LIGHT='#F4F7FA'

# A helpful visual wireframe, intentionally NOT a screenshot of real Power BI.
width,height=1600,900
can=Image.new('RGB',(width,height),'#F1F6F8')
d=ImageDraw.Draw(can)
reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f=lambda size,b=False:ImageFont.truetype(bold if b else reg,size)
d.rectangle((0,0,width,116),fill=NAVY)
d.text((45,30),'STUDENT PERFORMANCE  /  Executive overview',font=f(30,True),fill='white')
d.text((46,78),'POWER BI PAGE 1  •  VISUAL DESIGN CONCEPT (not a real .pbix)',font=f(14),fill='#B8E9E4')
# Slicer rail
x0=40;railw=290
d.rounded_rectangle((x0,140,x0+railw,842),radius=16,fill='white',outline='#D9E5EB',width=2)
d.text((x0+20,165),'FILTERS',font=f(20,True),fill=NAVY)
for i,(cap,lines) in enumerate([('Extracurricular',['All','Yes','No']),('Teacher quality',['All','High','Medium','Low','Unknown']),('Score flag',['All','Within 0-100','Above 100'])]):
    y=220+i*194
    d.text((x0+18,y),cap,font=f(16,True),fill=NAVY)
    d.rounded_rectangle((x0+17,y+39,x0+railw-17,y+78),8,fill='#F4F7FA',outline='#CFDDE4')
    d.text((x0+29,y+49),'All  v',font=f(14),fill=GRAY)
    d.text((x0+19,y+90),'Slicer (interactive in Power BI)',font=f(10),fill='#70818E')
# KPI tiles
left=365;gap=17;usable=width-left-46;tile=(usable-gap*3)//4
cards=[('STUDENTS',f'{M["record_count"]:,}'),('AVERAGE SCORE',f'{M["average_score"]:.2f}'),('STUDY HOURS / WEEK',f'{M["avg_study_hours"]:.1f}'),('AVG ATTENDANCE',f'{M["average_attendance"]:.1f}%')]
for i,(cap,val) in enumerate(cards):
    x=left+i*(tile+gap)
    d.rounded_rectangle((x,141,x+tile,298),radius=15,fill='white',outline='#D9E5EB',width=2)
    d.text((x+18,159),cap,font=f(13,True),fill=GRAY)
    d.text((x+18,206),val,font=f(39,True),fill=TEAL if i>1 else BLUE)
# paste charts preserving look
for (box,img) in [((left,324,955,733),'01_study_hours.png'),((970,324,1556,733),'02_attendance.png')]:
    x1,y1,x2,y2=box
    d.rounded_rectangle((x1,y1,x2,y2),radius=14,fill='white',outline='#D9E5EB',width=2)
    chart=Image.open(CH/img).convert('RGB')
    chart.thumbnail((x2-x1-24,y2-y1-25),Image.Resampling.LANCZOS)
    can.paste(chart,(int(x1+(x2-x1-chart.width)/2),int(y1+(y2-y1-chart.height)/2)))
d.rounded_rectangle((left,754,1556,836),radius=12,fill='#E6F3F2')
d.text((left+22,775),'READ THIS FIRST',font=f(17,True),fill=NAVY)
d.text((left+212,778),'Relationships in a synthetic dataset are descriptive, not causal.',font=f(15),fill=GRAY)
can.save(BI/'dashboard_design_mockup.png',quality=95)

charts=[
 ('01_study_hours.png','Study habits','Scores are higher on average in longer-study groups, but sample sizes are uneven.'),
 ('02_attendance.png','Attendance','The 90–100% attendance band averages 70.14 versus 64.21 in the 60–69% band.'),
 ('03_attendance_study_heatmap.png','Combined view','Each cell shows its sample size: inspect attendance and study hours together.'),
 ('04_tutoring.png','Tutoring','The within-study-hour comparisons remain descriptive, not a tutoring treatment effect.'),
 ('05_sleep.png','Sleep','Nearly flat observed differences; the vertical axis is zoomed and labeled.'),
 ('06_correlations.png','Correlations','Attendance and study hours have larger observed numeric correlations with the exam score.')
]
sections='\n'.join(f'''<section><div class="sectiontop"><span>0{i}</span><h2>{html.escape(title)}</h2></div>
<img loading="lazy" src="../charts/{img}" alt="{html.escape(title)} chart"><p>{html.escape(note)}</p></section>'''
for i,(img,title,note) in enumerate(charts,1))
html_doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student performance | Portfolio analysis</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#eef4f7;color:{NAVY};font-family:Arial,Helvetica,sans-serif;line-height:1.55}}.shell{{max-width:1120px;margin:auto;padding:26px}}
.hero{{background:{NAVY};padding:54px 58px;border-radius:21px;color:#fff}}.hero small{{color:#96E3D8;letter-spacing:.11em;font-weight:bold}}h1{{font-size:47px;line-height:1.07;max-width:790px;margin:16px 0}}.lead{{font-size:19px;color:#cde0e7;max-width:800px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:25px 0}}.kpis div{{background:white;border:1px solid #d7e6ed;border-radius:16px;padding:24px 19px}}.kpis b{{display:block;font-size:34px;color:{BLUE}}}.kpis small{{color:#586b77}}section{{background:white;border:1px solid #dbe6eb;border-radius:18px;margin:20px 0;padding:25px 36px}}section img{{width:100%;max-width:100%;display:block;max-height:480px;object-fit:contain}}section p{{color:#475e70}}.sectiontop{{display:flex;align-items:center;gap:15px}}.sectiontop span{{font-size:16px;color:{TEAL};font-weight:900}}.sectiontop h2{{font-size:26px}}.notice{{background:#e5f4f0;border-left:6px solid {TEAL};padding:20px 25px;border-radius:10px;margin:20px 0}}footer{{text-align:center;color:#566574;padding:25px}}a{{color:{BLUE}}}@media(max-width:800px){{.hero{{padding:30px}}h1{{font-size:34px}}.kpis{{grid-template-columns:repeat(2,1fr)}}section{{padding:14px}}}}</style>
</head><body><div class="shell"><header class="hero"><small>PORTFOLIO CASE STUDY / SQL · PYTHON · POWER BI</small>
<h1>What patterns appear in student exam performance?</h1><p class="lead">A readable, reproducible exploration of 6,607 synthetic student records, with SQL queries, Python analysis and a Power BI-ready dataset.</p></header>
<div class="kpis"><div><b>6,607</b><small>student records</small></div><div><b>67.24</b><small>average exam score</small></div><div><b>+0.58</b><small>attendance correlation</small></div><div><b>+0.45</b><small>study-hours correlation</small></div></div>
<div class="notice"><strong>Executive summary.</strong> Attendance and study hours are positively associated with scores in these records. A tutoring difference is visible within study-hour groups; sleep-hour means are nearly flat. None of these observational patterns prove cause and effect.</div>
{sections}
<section><h2>Data quality and limitations</h2><p>The raw dataset contains 78 missing teacher-quality values, 90 missing parental-education values, 67 missing distance values and a single exam score of 101. Missing text values become "Unknown" in the Power BI export; the out-of-range score is retained and flagged for transparent sensitivity checks. Because these data are synthetic, the results should not be generalized to actual schools.</p>
<p>The <code>notebooks/student_performance_analysis.ipynb</code> file contains executable analysis. The <code>powerbi/</code> folder contains the data, theme, DAX and step-by-step report instructions; a native PBIX needs to be saved from Power BI Desktop.</p></section>
<footer>Student Performance | Descriptive education analytics | Dataset source: Kaggle - Lai Nguyen</footer></div></body></html>'''
(REPORT/'portfolio_overview.html').write_text(html_doc,encoding='utf8')

# A portable summary report: 5 carefully composed A4 pages.
PDF=REPORT/'student_performance_executive_report.pdf'
c=Canvas(str(PDF),pagesize=A4,pageCompression=1)
W,H=A4
styles={
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=10.4,leading=15,textColor=HexColor(NAVY)),
 'caption':ParagraphStyle('cap',fontName='Helvetica',fontSize=9.1,leading=12.8,textColor=HexColor(GRAY)),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=10,leading=14,textColor=HexColor(GRAY)),
}
def P(s,x,y,maxw=486,style='body'):
    p=Paragraph(s,styles[style]);_,h=p.wrap(maxw,1000);p.drawOn(c,x,y-h);return y-h

def header(page,title,tag='ANALYTICAL REPORT'):
    c.setFillColor(HexColor(NAVY));c.rect(0,H-89,W,89,stroke=0,fill=1)
    c.setFillColor(HexColor('#8FE3D8'));c.setFont('Helvetica-Bold',9);c.drawString(47,H-33,tag)
    c.setFillColor(HexColor('#FFFFFF'));c.setFont('Helvetica-Bold',22);c.drawString(47,H-62,title)
    c.setStrokeColor(HexColor('#D8E6EC'));c.line(48,55,W-48,55)
    c.setFillColor(HexColor(GRAY));c.setFont('Helvetica',8.7)
    c.drawString(48,39,'Student Performance | SQL + Python + Power BI | Synthetic data')
    c.drawRightString(W-48,39,str(page))

def image_block(filename,y,maxw=500,maxh=237):
    im=Image.open(CH/filename)
    w,h=im.size;scale=min(maxw/w,maxh/h);dw=w*scale;dh=h*scale
    c.drawImage(ImageReader(im),(W-dw)/2,y-dh,dw,dh,mask='auto')
    return y-dh

header(1,'What patterns shape exam scores?','EXECUTIVE BRIEF')
y=H-109
y=P('A descriptive portfolio case study of <b>6,607 synthetic student records</b> using PostgreSQL, Python and a Power BI-ready model. It examines study habits, attendance, tutoring and sleep without making causal claims.',48,y)
y-=20
y=image_block('00_hero.png',y,maxw=500,maxh=260)-12
y=P('<b>Three observations from these records</b>',48,y)
for line in [
    '<b>Attendance:</b> the mean exam score rises from 64.21 (60-69% attendance) to 70.14 (90-100% attendance).',
    '<b>Study time:</b> students in the 16+ weekly-hour band average 67.92; those in the 1-5-hour band average 62.63, although the latter contains only 59 records.',
    '<b>Sleep:</b> the observed linear correlation with score is approximately -0.02; this synthetic sample offers little evidence of an unadjusted linear pattern.'
]:
    y-=13;y=P('&bull; '+line,60,y,470)
y-=24
c.setFillColor(HexColor('#E8F6F3'));c.roundRect(49,y-55,W-98,59,9,stroke=0,fill=1)
P('<b>Interpretation:</b> relationships do not establish cause and effect. The source is synthetic, not a representative school sample.',62,y-11,455)
c.showPage()

header(2,'Study habits and attendance')
y=H-109
y=P('The broad study-hour and attendance bands display gradual average-score differences. Each chart labels group sizes, because a precise average based on 59 observations is less stable than one based on thousands.',48,y,'486' if False else 486)
y-=7;y=image_block('01_study_hours.png',y,maxw=475,maxh=245)
y-=8;y=P('<b>Study-hour gap:</b> 67.92 - 62.63 = approximately <b>5.30 points</b> between extreme groups; this unadjusted contrast is not a recommended study-hour target.',50,y,487,style='caption')
y-=18;y=image_block('02_attendance.png',y,maxw=475,maxh=243)
y-=5;P('<b>Attendance gap:</b> the 90-100% band averages approximately <b>5.93 points</b> above the 60-69% band. Other factors may differ across groups.',50,y,487,style='caption')
c.showPage()

header(3,'Explore combined patterns')
y=H-109
y=P('A more useful analytical question is whether the observed patterns persist when comparing more similar study-hour groups. These charts expose the joint attendance-by-study matrix and tutoring differences within study-hour strata.',48,y)
y-=11;y=image_block('03_attendance_study_heatmap.png',y,maxw=475,maxh=260)
y-=9;y=P('<b>Read the sample sizes:</b> counts are printed in every cell; compare within rows and columns rather than claiming a particular habit compensates for another.',50,y,485,style='caption')
y-=16;y=image_block('04_tutoring.png',y,maxw=475,maxh=239)
y-=8;P('<b>Tutoring comparison:</b> study-hour stratification helps contextualize the raw difference, but does not control for attendance, prior scores, resources or selection into tutoring.',50,y,485,style='caption')
c.showPage()

header(4,'Wellbeing and correlations')
y=H-109
y=P('Near-zero correlation is a finding in this dataset, not proof that sleep is irrelevant to student health or educational outcomes. The sleep chart deliberately indicates its zoomed axis and uncertainty bars.',48,y)
y-=10;y=image_block('05_sleep.png',y,maxw=475,maxh=253)
y-=8;y=P('The unadjusted sleep correlation is <b>-0.017</b>; small observed mean differences are close to the noise level. Approximate intervals are shown to discourage overinterpretation.',50,y,485,style='caption')
y-=16;y=image_block('06_correlations.png',y,maxw=475,maxh=256)
y-=5;P('Pearson correlation measures one type of association. It does not describe an independent causal contribution or establish how a variable would behave in real schools.',50,y,485,style='caption')
c.showPage()

header(5,'Method and reproducibility')
y=H-109
y=P('<b>Workflow</b>',48,y)
for line in [
    '1. Ingest the original 6,607-row, 20-column CSV without changing source exam scores.',
    '2. Execute three original PostgreSQL assignment queries and five optional investigation/validation queries.',
    '3. Prepare grouped summaries and six labeled charts with pandas and matplotlib.',
    '4. Export a 27-column Power BI-ready table with explicit categorical Unknown values, grouping fields and a score quality flag.',
    '5. Create a Power BI report with the supplied DAX measures, theme, page plan and QA checklist.'
]:
    y-=9;y=P(line,62,y,475)
y-=26;y=P('<b>Source data quality</b>',48,y)
for line in ['6,607 rows, 20 raw variables and no exact duplicate rows.',
             'Three original partially missing fields: teacher quality (78), parental education (90), distance from home (67).',
             'One score = 101 despite the conventional 0-100 scale: original assignment outputs retain it; the dashboard can filter or flag it.',
             'The overall average is 67.2357 with this flagged record and 67.2305 when it is excluded.']:
    y-=10;y=P('&bull; '+line,62,y,474)
y-=24;y=P('<b>Optional predictive illustration</b>',48,y)
y-=9;y=P('An 80/20 random held-out split of synthetic rows gives test MAE approximately <b>1.27</b> for a numerical ridge baseline and <b>1.23</b> after adding two categorical fields (teacher quality and extracurricular participation). This is a demonstration of evaluation mechanics, not a deployable assessment model.',48,y)
y-=25;y=P('<b>Important boundaries</b>',48,y)
y-=8;y=P('This dataset is described as <b>synthetic</b>, and no experimental treatment is assigned. Missing categories are preserved as Unknown. Neither predictive fit nor correlation is evidence of intervention effectiveness; source data are not representative of real students.',48,y)
y-=23;y=P('<b>How to review or rebuild</b>',48,y)
y-=8;P('The repository contains an executed Jupyter notebook, exact SQL and CSV query outputs, original source, Python scripts, an offline HTML report, and a Power BI build guide. The final native <b>.pbix must be saved from Power BI Desktop</b> using the prepared assets.',48,y)
c.save()
print('Created:',BI/'dashboard_design_mockup.png',REPORT/'portfolio_overview.html',PDF)
