import sys,unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python'))
from metrics import summarize,safe_div
class HealthcareMetricTests(unittest.TestCase):
 def frame(self):
  return pd.DataFrame({'status':['Attended','No-show','Cancelled'],'wait_minutes':[0,None,None],'wait_target_minutes':[30,30,30]})
 def test_cancelled_excluded_from_no_show_rate(self):
  self.assertEqual(summarize(self.frame())['no_show_rate'],.5)
 def test_zero_wait_is_valid(self):
  self.assertEqual(summarize(self.frame())['avg_wait_minutes'],0)
  self.assertEqual(summarize(self.frame())['within_target_rate'],1)
 def test_empty_period_is_not_zero_rate(self):
  self.assertIsNone(summarize(self.frame().iloc[:0])['no_show_rate'])
 def test_target_boundary_is_inclusive(self):
  f=self.frame();f.loc[0,'wait_minutes']=30;self.assertEqual(summarize(f)['within_target_rate'],1)
if __name__=='__main__':unittest.main()
