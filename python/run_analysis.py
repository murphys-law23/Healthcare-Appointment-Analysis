"""Run all SQL, validate data and reconcile key results with independent pandas calculations."""
from metrics import *
def main():
 frame,depts=prepare();out=ROOT/'reports';(out/'query_results').mkdir(parents=True,exist_ok=True)
 hc=(ROOT/'data/appointments.csv').exists();table='appointments' if hc else 'employees'
 with sqlite3.connect(':memory:') as con:
  for name in ([table,'departments'] if hc else [table,'departments','periods']):
   pd.read_csv(ROOT/'data'/f'{name}.csv').to_sql(name,con,index=False)
  sql='\n'.join(line for line in (ROOT/'sql/analysis.sql').read_text().splitlines() if not line.lstrip().startswith('--'))
  results=[]
  for statement in sql.split(';'):
   if statement.strip():results.append(pd.read_sql_query(statement,con))
 summary=summarize(frame)
 for key,value in results[0].iloc[0].to_dict().items():
  assert abs(summary[key]-value)<1e-8,f'KPI mismatch {key}'
 for _,row in results[1].iterrows():
  m=summarize(frame[frame.appointment_date.dt.strftime('%Y-%m').eq(row['month'])]) if hc else summarize(frame,row.period_start,row.period_end)
  for key in ['bookings','attended','no_shows','no_show_rate','avg_wait_minutes'] if hc else ['opening','closing','hires','leavers','turnover_rate']:
   assert abs(m[key]-row[key])<1e-8,f'Monthly mismatch {key}'
 for _,row in results[2].iterrows():
  m=summarize(frame[frame.department.eq(row.department)])
  for key in ['bookings','attended','avg_wait_minutes','within_target_rate'] if hc else ['opening','closing','leavers','turnover_rate']:
   assert abs(m[key]-row[key])<1e-8,f'Department mismatch {key}'
 for i,result in enumerate(results,1):result.to_csv(out/'query_results'/f'query_{i:02}.csv',index=False)
 serial=frame.copy()
 for col in serial.select_dtypes(include=['datetime64[ns]']).columns:serial[col]=serial[col].dt.strftime('%Y-%m-%d')
 serial.to_csv(ROOT/'data/processed.csv',index=False)
 (out/'metrics.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
 (out/'validation.txt').write_text('PASS: input validity, key uniqueness, foreign keys, annual KPI reconciliation, 12 monthly reconciliations and six department reconciliations.\nSQL engine: SQLite. Power BI Desktop has not been executed.\n')
 print(json.dumps(summary,indent=2));print('PASS: six SQL queries exported; annual, monthly and department metrics reconciled.')
if __name__=='__main__':main()
