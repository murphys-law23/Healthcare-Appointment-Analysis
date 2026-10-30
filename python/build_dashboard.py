"""Embed processed records in a self-contained offline dashboard."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 rows=list(csv.DictReader((ROOT/'data/processed.csv').open()))
 template=(ROOT/'dashboard/template.html').read_text()
 (ROOT/'dashboard/index.html').write_text(template.replace('__DATA__',json.dumps(rows,separators=(',',':'))))
 print('Built dashboard/index.html')
if __name__=='__main__':main()
