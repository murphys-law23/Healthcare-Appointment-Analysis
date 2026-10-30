"""Generate fictional outpatient operations data. Fixed seed; no real patient data."""
from pathlib import Path
from datetime import date,timedelta
import random,csv
ROOT=Path(__file__).resolve().parents[1]
def main():
 rng=random.Random(20251029);out=ROOT/'data';out.mkdir(exist_ok=True)
 departments=[('D01','General Medicine',30),('D02','Cardiology',30),('D03','Dermatology',30),('D04','Orthopedics',30),('D05','Ophthalmology',30),('D06','Pediatrics',30)]
 with (out/'departments.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['department_id','department','wait_target_minutes']);w.writerows(departments)
 days=[date(2025,1,1)+timedelta(days=i) for i in range(365) if (date(2025,1,1)+timedelta(days=i)).weekday()<5]
 rows=[]
 for i in range(3600):
  appt=rng.choice(days);dep=rng.choices(departments,weights=[30,16,12,16,10,16])[0]
  lead=rng.randint(0,55);reminder=int(rng.random()<.72)
  # Design assumptions for teaching, not estimated real-world effects.
  ns=.08+.0024*lead+(.025 if dep[0]=='D04' else 0)-.025*reminder
  u=rng.random();status='Cancelled' if u<.09 else 'No-show' if u<.09+ns else 'Attended'
  wait=max(0,round(rng.gauss({'D01':26,'D02':39,'D03':20,'D04':35,'D05':23,'D06':29}[dep[0]]+(6 if appt.weekday()==0 else 0),12))) if status=='Attended' else ''
  service=max(5,round(rng.gauss(22,7))) if status=='Attended' else ''
  rows.append([f'A{i+1:05}',f'P{rng.randint(1,1100):04}',appt.isoformat(),(appt-timedelta(days=lead)).isoformat(),dep[0],rng.choice(['Central','North','South']),rng.choice(['New','Follow-up']),status,reminder,wait,service])
 with (out/'appointments.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['appointment_id','patient_id','appointment_date','booking_date','department_id','clinic','visit_type','status','reminder_sent','wait_minutes','service_minutes']);w.writerows(rows)
 print('Generated 3,600 synthetic appointments and six departments.')
if __name__=='__main__':main()
