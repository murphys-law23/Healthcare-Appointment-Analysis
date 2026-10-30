from pathlib import Path
import json,sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def safe_div(n,d):return n/d if d else None

def prepare():
 a=pd.read_csv(ROOT/'data/appointments.csv',parse_dates=['appointment_date','booking_date'])
 d=pd.read_csv(ROOT/'data/departments.csv')
 assert a.appointment_id.is_unique and d.department_id.is_unique
 assert not a.drop(columns=['wait_minutes','service_minutes']).isna().any().any()
 assert set(a.status)<= {'Attended','No-show','Cancelled'}
 assert set(a.department_id)<=set(d.department_id)
 assert a.appointment_date.between('2025-01-01','2025-12-31').all()
 assert (a.booking_date<=a.appointment_date).all()
 assert a.loc[a.status.eq('Attended'),['wait_minutes','service_minutes']].notna().all().all()
 assert (a.loc[a.status.eq('Attended'),['wait_minutes','service_minutes']]>=0).all().all()
 assert a.loc[~a.status.eq('Attended'),['wait_minutes','service_minutes']].isna().all().all()
 a=a.merge(d,on='department_id',validate='many_to_one')
 a['lead_days']=(a.appointment_date-a.booking_date).dt.days
 a['lead_band']=pd.cut(a.lead_days,[-1,7,21,999],labels=['0-7 days','8-21 days','22+ days']).astype(str)
 return a,d

def summarize(a):
 attended=a[a.status.eq('Attended')];ns=int(a.status.eq('No-show').sum());cancelled=int(a.status.eq('Cancelled').sum())
 return {'bookings':len(a),'attended':len(attended),'no_shows':ns,'cancelled':cancelled,'no_show_rate':safe_div(ns,len(attended)+ns),'avg_wait_minutes':float(attended.wait_minutes.mean()) if len(attended) else None,'within_target_rate':float((attended.wait_minutes<=attended.wait_target_minutes).mean()) if len(attended) else None}
