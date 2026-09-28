"""Reproducible analysis, quality checks, Power BI export and portfolio graphics.

Run from anywhere: python scripts/analyze.py
This educational synthetic dataset is observational; all comparisons are descriptive.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'StudentPerformanceFactors.csv'
RESULTS = ROOT / 'results'
CHARTS = ROOT / 'charts'
POWERBI = ROOT / 'powerbi'
for p in [RESULTS, CHARTS, POWERBI]: p.mkdir(parents=True, exist_ok=True)

NAVY='#12263A'; BLUE='#2176AE'; TEAL='#129E91'; CYAN='#83D6CD'; LIGHT='#F4F7FA'; GRAY='#566574'; AMBER='#DE9A4B'; PURPLE='#8269B4'
plt.rcParams.update({
    'font.family':'DejaVu Sans','font.size':10.5,'axes.titlesize':15,'axes.titleweight':'bold',
    'axes.labelcolor':NAVY,'text.color':NAVY,'xtick.color':GRAY,'ytick.color':GRAY,
    'axes.edgecolor':'#CBD5E1','figure.facecolor':'white','axes.facecolor':'white',
    'figure.dpi':145, 'savefig.dpi':190
})

def style(ax, ygrid=True):
    ax.spines[['top','right']].set_visible(False)
    ax.set_axisbelow(True)
    if ygrid: ax.yaxis.grid(True,alpha=.20,color='#A6B3C2')

def save(fig, filename):
    fig.savefig(CHARTS / filename,bbox_inches='tight',pad_inches=.20)
    plt.close(fig)

def write(df, name):
    df.to_csv(RESULTS/name,index=False,float_format='%.4f')

def load():
    raw=pd.read_csv(RAW)
    assert raw.shape==(6607,20), f'Unexpected dataset shape {raw.shape}'
    assert raw['Hours_Studied'].between(1,44).all()
    df=raw.copy()
    df.insert(0,'Student_ID',np.arange(1,len(df)+1)) # stable row index in THIS CSV, not a genuine person ID
    for col in ['Teacher_Quality','Parental_Education_Level','Distance_from_Home']:
        df[col]=df[col].fillna('Unknown')
    df['Study_Hours_Range']=pd.cut(df.Hours_Studied,bins=[0,5,10,15,np.inf],
                                  labels=['1-5 hours','6-10 hours','11-15 hours','16+ hours']).astype(str)
    hours_sort={'1-5 hours':1,'6-10 hours':2,'11-15 hours':3,'16+ hours':4}
    df['Study_Range_Order']=df['Study_Hours_Range'].map(hours_sort)
    df['Attendance_Band']=pd.cut(df.Attendance,bins=[0,69,79,89,100],
                                labels=['60-69%','70-79%','80-89%','90-100%']).astype(str)
    att_sort={'60-69%':1,'70-79%':2,'80-89%':3,'90-100%':4}
    df['Attendance_Band_Order']=df['Attendance_Band'].map(att_sort)
    df['Tutoring_Group']=np.where(df.Tutoring_Sessions>0,'1+ sessions','No tutoring')
    df['Score_Quality_Flag']=np.where(df.Exam_Score>100,'Above 100','Within 0-100')
    assert df['Study_Hours_Range'].ne('nan').all() and df['Attendance_Band'].ne('nan').all()
    assert not df.isna().any().any()
    df.to_csv(POWERBI/'student_performance_powerbi.csv', index=False)
    return raw,df

def summaries(raw, df):
    group = df.groupby('Study_Hours_Range').Exam_Score.agg(students='size', avg_score='mean').reset_index()
    group['order']=group.Study_Hours_Range.map({'1-5 hours':1,'6-10 hours':2,'11-15 hours':3,'16+ hours':4})
    group=group.sort_values('order')
    write(group,'study_range_summary.csv')
    att=df.groupby('Attendance_Band').Exam_Score.agg(students='size',avg_score='mean').reset_index()
    att['order']=att.Attendance_Band.map({'60-69%':1,'70-79%':2,'80-89%':3,'90-100%':4})
    att=att.sort_values('order')
    write(att,'attendance_summary.csv')
    matrix=df.groupby(['Attendance_Band','Study_Hours_Range']).Exam_Score.agg(students='size',avg_score='mean').reset_index()
    matrix['attendance_order']=matrix.Attendance_Band.map({'60-69%':1,'70-79%':2,'80-89%':3,'90-100%':4})
    matrix['study_order']=matrix.Study_Hours_Range.map({'1-5 hours':1,'6-10 hours':2,'11-15 hours':3,'16+ hours':4})
    matrix=matrix.sort_values(['attendance_order','study_order'])
    write(matrix,'attendance_x_study_matrix.csv')
    tutor=df.groupby(['Study_Hours_Range','Tutoring_Group']).Exam_Score.agg(students='size',avg_score='mean').reset_index()
    tutor['study_order']=tutor.Study_Hours_Range.map({'1-5 hours':1,'6-10 hours':2,'11-15 hours':3,'16+ hours':4})
    tutor=tutor.sort_values(['study_order','Tutoring_Group'])
    write(tutor,'tutoring_by_study_range.csv')
    extra=df.groupby(['Study_Hours_Range','Extracurricular_Activities']).Exam_Score.agg(students='size',avg_score='mean').reset_index()
    extra['study_order']=extra.Study_Hours_Range.map({'1-5 hours':1,'6-10 hours':2,'11-15 hours':3,'16+ hours':4})
    write(extra,'extracurricular_by_study_range.csv')
    sleep=df.groupby('Sleep_Hours').Exam_Score.agg(students='size',avg_score='mean',std='std').reset_index()
    sleep['se']=sleep['std']/np.sqrt(sleep.students)
    sleep['lower95']=sleep.avg_score-1.96*sleep.se
    sleep['upper95']=sleep.avg_score+1.96*sleep.se
    write(sleep,'sleep_summary.csv')
    teacher=df.groupby('Teacher_Quality').Exam_Score.agg(students='size',avg_score='mean').reset_index()
    write(teacher,'teacher_quality_summary.csv')
    corr=raw.select_dtypes('number').corr()['Exam_Score'].drop('Exam_Score').sort_values(ascending=False)
    write(corr.rename_axis('feature').reset_index(name='pearson_r'),'numeric_correlations.csv')
    missing=raw.isna().sum()
    quality=pd.DataFrame({'metric':['records','columns_in_source','exact_duplicate_rows','missing_teacher_quality',
                                     'missing_parental_education_level','missing_distance_from_home',
                                     'scores_above_100','mean_score_including_flagged','mean_score_excluding_flagged'],
                          'value':[len(raw),len(raw.columns),raw.duplicated().sum(),int(missing.Teacher_Quality),
                                   int(missing.Parental_Education_Level),int(missing.Distance_from_Home),
                                   int((raw.Exam_Score>100).sum()),float(raw.Exam_Score.mean()),
                                   float(raw.loc[raw.Exam_Score<=100,'Exam_Score'].mean())]})
    write(quality,'data_quality_summary.csv')
    # A small two-by-two case study: descriptive contrasts, not individual equivalence.
    case=df.assign(Study_Group=np.where(df.Hours_Studied>=16,'16+ hours','<16 hours'),
                   Attendance_Group=np.where(df.Attendance>=80,'80%+','<80%'))
    ca=case.groupby(['Study_Group','Attendance_Group']).Exam_Score.agg(students='size',avg_score='mean').reset_index()
    write(ca,'attendance_study_case_study.csv')
    metrics={
        'record_count':int(len(df)), 'average_score':float(df.Exam_Score.mean()),
        'median_score':float(df.Exam_Score.median()),'average_attendance':float(df.Attendance.mean()),
        'avg_study_hours':float(df.Hours_Studied.mean()),
        'corr_attendance':float(corr.Attendance),'corr_study_hours':float(corr.Hours_Studied),
        'corr_sleep':float(corr.Sleep_Hours),
        'missing_total':int(missing.sum()),
        'mean_difference_excluding_flagged':float(raw.Exam_Score.mean()-raw.loc[raw.Exam_Score<=100,'Exam_Score'].mean()),
        'study_bands':group.to_dict('records'), 'attendance_bands':att.to_dict('records'),
        'case_study':ca.to_dict('records'),
    }
    (RESULTS/'project_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    return {'group':group,'att':att,'matrix':matrix,'tutor':tutor,'extra':extra,
            'sleep':sleep,'teacher':teacher,'corr':corr,'quality':quality,'case':ca,'metrics':metrics}

def figures(r):
    group=r['group']; att=r['att']; matrix=r['matrix']; tutor=r['tutor']; sleep=r['sleep']; corr=r['corr']
    # 1: exam scores by hour band, start zero for context, add counts for reliability.
    fig,ax=plt.subplots(figsize=(8.7,4.35))
    bars=ax.bar(group.Study_Hours_Range,group.avg_score,color=[CYAN,'#56BEB4',TEAL,BLUE],width=.64)
    for b,score,n in zip(bars,group.avg_score,group.students):
        ax.text(b.get_x()+b.get_width()/2,score+.75,f'{score:.2f}',ha='center',weight='bold',fontsize=11)
        ax.text(b.get_x()+b.get_width()/2,score/2, f'n={n:,}',ha='center',color='white' if n>=1000 else NAVY,fontsize=9,weight='bold')
    ax.set(title='Exam score rises across study-hour ranges',ylabel='Average exam score',ylim=(0,79))
    style(ax); fig.tight_layout(); save(fig,'01_study_hours.png')
    # 2 attendance
    fig,ax=plt.subplots(figsize=(8.7,4.2))
    bars=ax.bar(att.Attendance_Band,att.avg_score,color=[CYAN,'#56BEB4',TEAL,BLUE],width=.62)
    for b,v,n in zip(bars,att.avg_score,att.students):
        ax.text(b.get_x()+b.get_width()/2,v+.9,f'{v:.2f}',ha='center',weight='bold',fontsize=11)
        ax.text(b.get_x()+b.get_width()/2,v/2,f'n={n:,}',ha='center',color='white',weight='bold',fontsize=9)
    ax.set(title='Average exam score by class attendance',xlabel='Attendance range',ylabel='Average exam score',ylim=(0,81))
    style(ax);fig.tight_layout();save(fig,'02_attendance.png')
    # 3 attendance vs study heatmap WITH sample size in every cell.
    a_labels=['60-69%','70-79%','80-89%','90-100%']
    h_labels=['1-5 hours','6-10 hours','11-15 hours','16+ hours']
    vals=matrix.pivot(index='Attendance_Band',columns='Study_Hours_Range',values='avg_score').reindex(index=a_labels,columns=h_labels)
    ns=matrix.pivot(index='Attendance_Band',columns='Study_Hours_Range',values='students').reindex(index=a_labels,columns=h_labels)
    fig,ax=plt.subplots(figsize=(9.15,4.85)); im=ax.imshow(vals.values,cmap='YlGnBu',vmin=59,vmax=74,aspect='auto')
    for y in range(4):
        for x in range(4):
            val=vals.iloc[y,x];n=ns.iloc[y,x]
            ax.text(x,y, f'{val:.1f}\n(n={int(n)})',ha='center',va='center',color='white' if val>68 else NAVY,fontweight='bold' if int(n)>=100 else 'normal',fontsize=10)
    ax.set(xticks=range(4),yticks=range(4),xticklabels=h_labels,yticklabels=a_labels,
           xlabel='Weekly study hours',ylabel='Attendance', title='Attendance × study hours: average exam score')
    fig.colorbar(im,ax=ax,label='Average score',shrink=.77)
    fig.tight_layout();save(fig,'03_attendance_study_heatmap.png')
    # 4 tutoring comparisons inside hour strata; illustrates variation with limited conditioning.
    fig,ax=plt.subplots(figsize=(9.5,4.5)); order=['1-5 hours','6-10 hours','11-15 hours','16+ hours']; xpos=np.arange(4)
    no=tutor[tutor.Tutoring_Group=='No tutoring'].set_index('Study_Hours_Range').reindex(order)
    yes=tutor[tutor.Tutoring_Group=='1+ sessions'].set_index('Study_Hours_Range').reindex(order)
    b1=ax.bar(xpos-.19,no.avg_score,width=.37,color='#7391AD',label='No tutoring')
    b2=ax.bar(xpos+.19,yes.avg_score,width=.37,color=TEAL,label='1+ sessions')
    for bars,frame in [(b1,no),(b2,yes)]:
        for b,n,v in zip(bars,frame.students,frame.avg_score):
            ax.text(b.get_x()+b.get_width()/2,v+.55,f'{v:.1f}',ha='center',fontsize=8.5)
            ax.text(b.get_x()+b.get_width()/2,12,f'n={n:,}',ha='center',rotation=90,fontsize=7.8,color='white' if n>100 else NAVY)
    ax.set_xticks(xpos,order);ax.set(ylim=(0,80),ylabel='Average exam score',title='Tutoring comparison within study-hour groups')
    ax.legend(loc='upper left',ncol=2,frameon=False)
    style(ax);fig.tight_layout();save(fig,'04_tutoring.png')
    # 5 sleep: y-axis zoomed but show CIs & explicit context that near-flat is finding.
    fig,ax=plt.subplots(figsize=(9.0,4.1))
    ax.errorbar(sleep.Sleep_Hours,sleep.avg_score,yerr=1.96*sleep.se,marker='o',markersize=7,color=BLUE,capsize=4,lw=2)
    ax.axhline(r['metrics']['average_score'],ls='--',color=GRAY,alpha=.65,label='Overall mean')
    ax.set(xticks=sleep.Sleep_Hours.tolist(),xlabel='Sleep hours per night',ylabel='Average exam score',
           title='Little unadjusted score difference across sleep durations',ylim=(66,69.6))
    ax.text(.99,.02,'Zoomed axis; error bars show approximate 95% CIs',transform=ax.transAxes,ha='right',fontsize=8,color=GRAY)
    ax.legend(frameon=False,loc='upper right');style(ax);fig.tight_layout();save(fig,'05_sleep.png')
    # 6 numeric correlation forest, r full axis length meaningful.
    series=corr.sort_values()
    fig,ax=plt.subplots(figsize=(9.2,4.8));colors=[TEAL if v>=0 else PURPLE for v in series]
    ax.barh(series.index.str.replace('_',' '),series.values,color=colors,height=.64)
    for i,v in enumerate(series.values):
        ax.text(v+.012 if v>=0 else v-.012,i,f'{v:+.2f}',ha='left' if v>=0 else 'right',va='center',fontsize=10,weight='bold')
    ax.set(xlim=(-.1,.69),xlabel='Pearson correlation with exam score',title='Numerical associations (not causal effects)')
    ax.axvline(0,color=GRAY,lw=.8);style(ax,False);fig.tight_layout();save(fig,'06_correlations.png')
    # standalone executive snapshot for README hero
    fig=plt.figure(figsize=(12.5,6.3),facecolor=NAVY)
    a=fig.add_axes([0,0,1,1]);a.set_axis_off();a.set_xlim(0,1);a.set_ylim(0,1)
    a.text(.055,.89,'STUDENT PERFORMANCE',fontsize=23,fontweight='bold',color='white',ha='left')
    a.text(.056,.82,'Exploring the patterns behind exam outcomes',fontsize=14,color='#CAE8EF')
    metrics=[('6,607','student records'),(f'{r["metrics"]["average_score"]:.2f}','average exam score'),
             (f'{r["metrics"]["corr_attendance"]:+.2f}','attendance correlation'),
             (f'{r["metrics"]["corr_study_hours"]:+.2f}','study-hour correlation')]
    from matplotlib.patches import FancyBboxPatch
    for i,(v,l) in enumerate(metrics):
        x=.055+i*.235
        a.add_patch(FancyBboxPatch((x,.42),.214,.28,boxstyle='round,pad=.014,rounding_size=.02',facecolor='#213C51',edgecolor='#3C6577',linewidth=1))
        a.text(x+.021,.565,v,color='#90E1D6',fontsize=27,fontweight='bold',ha='left')
        a.text(x+.021,.467,l,color='white',fontsize=10,ha='left')
    a.plot([.056,.942],[.327,.327],color='#618394',lw=1)
    a.text(.056,.235,'SQL  /  PYTHON  /  POWER BI',fontsize=13,color='white',weight='bold')
    a.text(.056,.148,'Descriptive analysis of a synthetic education dataset | Correlation is not causation',fontsize=10,color='#C2DAE4')
    save(fig,'00_hero.png')

def model(raw):
    """Exploratory holdout linear model; no causal or deployment claim."""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import Ridge
        from sklearn.metrics import mean_absolute_error,r2_score
        nums=['Hours_Studied','Attendance','Previous_Scores','Tutoring_Sessions','Sleep_Hours','Physical_Activity']
        cats=['Extracurricular_Activities','Teacher_Quality']
        features=nums+cats
        Xtr,Xte,ytr,yte=train_test_split(raw[features],raw.Exam_Score,test_size=.20,random_state=42)
        baseline=Pipeline([('prep',ColumnTransformer([('numeric',SimpleImputer(strategy='median'),nums)])),
                           ('regressor',Ridge(alpha=1.0))])
        rich=Pipeline([('prep',ColumnTransformer([
            ('numeric',SimpleImputer(strategy='median'),nums),
            ('category',Pipeline([('missing',SimpleImputer(strategy='constant',fill_value='Unknown')),
                                  ('encode',OneHotEncoder(handle_unknown='ignore'))]),cats)
        ])),('regressor',Ridge(alpha=1.0))])
        rows=[]
        for label,pipeline in [('Numeric-only baseline',baseline),('Numeric + two categories',rich)]:
            pipeline.fit(Xtr,ytr)
            pred=pipeline.predict(Xte)
            rows.append({'model':label,'train_rows':len(Xtr),'test_rows':len(Xte),'test_mae':mean_absolute_error(yte,pred),'test_r2':r2_score(yte,pred)})
        write(pd.DataFrame(rows),'optional_holdout_model.csv')
        return rows
    except ImportError:
        return None

def main():
    raw,df=load()
    info=summaries(raw,df)
    figures(info)
    model_results=model(raw)
    print(json.dumps({k:v for k,v in info['metrics'].items() if not isinstance(v,list)},indent=2))
    print('Holdout metrics:',model_results)
    print('Charts, output CSVs and Power BI import exported.')

if __name__=='__main__': main()
