from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[1]
HC=(ROOT/'data/appointments.csv').exists()
C=['#376b50','#a9be92','#ce9559'] if HC else ['#b75a3d','#515957','#d8a78c']
BG='#eef2ec' if HC else '#f5f0e9';DARK='#203f30' if HC else '#343b39';INK='#203a30' if HC else '#353331';EDGE='#c5cdc3'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK})
def main():
 k=json.loads((ROOT/'reports/metrics.json').read_text());q={i:pd.read_csv(ROOT/'reports/query_results'/f'query_{i:02}.csv') for i in range(1,7)}
 fig=plt.figure(figsize=(16,9),dpi=100,facecolor=BG)
 def txt(x,y,s,size=10,color=INK,bold=False,**kw):fig.text(x,y,s,fontsize=size,color=color,weight='bold' if bold else 'normal',**kw)
 def box(x,y,w,h,c='white'):fig.patches.append(Rectangle((x,y),w,h,facecolor=c,edgecolor=EDGE,lw=.8,transform=fig.transFigure,zorder=-1))
 def panel(x,y,w,h,title,sub,left=.045):
  box(x,y,w,h);txt(x+.012,y+h-.03,title,11,C[0],True);txt(x+.012,y+h-.055,sub,8)
  return fig.add_axes([x+left,y+.045,w-left-.022,h-.125],facecolor='none')
 def style(ax):
  ax.spines[['top','right','left']].set_visible(False);ax.spines['bottom'].set_color(EDGE);ax.tick_params(length=0,labelsize=8);ax.grid(axis='y',color=EDGE,lw=.6);ax.set_axisbelow(True)
 def bars(ax,labels,vals,fmt):
  order=sorted(zip(labels,vals),key=lambda z:z[1]);ls,vs=zip(*order);ax.barh(ls,vs,color=[C[1]]*(len(vs)-1)+[C[0]],height=.58);mx=max(vs);ax.set_xlim(0,mx*1.25);ax.spines[:].set_visible(False);ax.tick_params(length=0,labelbottom=False,labelsize=9)
  for i,v in enumerate(vs):ax.text(v+mx*.025,i,fmt(v),va='center',fontsize=9)
 box(.015,.88,.97,.1,DARK);txt(.03,.953,'MURPHY  /  ANALYTICS PORTFOLIO',9,'#dce4d6');txt(.03,.911,'HEALTHCARE APPOINTMENT OPERATIONS' if HC else 'HR WORKFORCE & ATTRITION',23,'white',True)
 txt(.97,.933,'2025  |  FULL YEAR',11,'white',True,ha='right');txt(.02,.855,'ALL DEPARTMENTS   /   '+('ALL CLINICS' if HC else 'ALL WORK MODES'),9)
 cards=([('APPOINTMENTS',f"{k['bookings']:,}",'All booking outcomes'),('NO-SHOW RATE',f"{k['no_show_rate']:.1%}",'Cancelled bookings excluded'),('AVERAGE WAIT',f"{k['avg_wait_minutes']:.1f} min",'Attended visits only'),('WITHIN WAIT TARGET',f"{k['within_target_rate']:.1%}",'30-minute planning target')]
 if HC else [('CLOSING HEADCOUNT',f"{k['closing']:,}",'At 31 December 2025'),('HIRES',f"{k['hires']:,}",'Started during the year'),('DEPARTURES',f"{k['leavers']:,}",'Voluntary and involuntary'),('TURNOVER RATE',f"{k['turnover_rate']:.1%}",'Leavers / average headcount')])
 for i,(label,val,note) in enumerate(cards):
  x=.015+i*.245;box(x,.72,.235,.115);box(x,.831,.235,.004,C[0]);txt(x+.012,.806,label,9,bold=True);txt(x+.012,.762,val,28,C[0],True);txt(x+.012,.734,note,8)
 months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];xs=list(range(12))
 if HC:
  ax=panel(.015,.405,.635,.295,'MONTHLY APPOINTMENT ACTIVITY','Bookings and attended visits');ax.fill_between(xs,q[2].bookings,color=C[0],alpha=.16);ax.plot(xs,q[2].bookings,color=C[0],marker='o',ms=3,label='Bookings');ax.plot(xs,q[2].attended,color=C[1],marker='o',ms=3,label='Attended');ax.set_xticks(xs,months);ax.set_ylim(0,q[2].bookings.max()*1.2);style(ax);ax.legend(loc='upper right',frameon=False,ncol=2,fontsize=8)
  ax=panel(.66,.09,.325,.61,'WAIT BY DEPARTMENT','Minutes · attended visits only',left=.105);bars(ax,q[3].department,q[3].avg_wait_minutes,lambda v:f'{v:.1f}')
  ax=panel(.34,.09,.31,.30,'NO-SHOWS BY LEAD TIME','Cancelled bookings excluded',left=.07);bars(ax,q[4].lead_band.str.slice(3),q[4].no_show_rate,lambda v:f'{v:.1%}')
  bx,by,bw,bh=.015,.09,.315,.30;vals=[k['attended'],k['no_shows'],k['cancelled']];labels=['Attended','No-show','Cancelled'];title='APPOINTMENT OUTCOMES';total=k['bookings']
 else:
  box(.015,.09,.18,.61,DARK);txt(.028,.665,'WORKFORCE SNAPSHOT',11,'#e9b59e',True)
  for y,l,v,note in [(.595,'Opening headcount',f"{k['opening']:,}",'At 1 January 2025'),(.43,'Net workforce change',f"{k['closing']-k['opening']:+,}",'Hires less departures'),(.265,'Voluntary exit share',f"{k['voluntary_leavers']/k['leavers']:.1%}",'Of all departures')]:
   txt(.028,y,l,10,'white');txt(.028,y-.052,v,28,'white',True);txt(.028,y-.083,note,8,'#ded5ce')
  ax=panel(.205,.405,.405,.295,'MONTH-END HEADCOUNT','Employees active at the end of each month');ax.fill_between(xs,q[2].closing,color=C[0],alpha=.15);ax.plot(xs,q[2].closing,color=C[0],marker='o',ms=3);ax.set_xticks(xs,months);ax.set_ylim(0,q[2].closing.max()*1.18);style(ax)
  ax=panel(.62,.405,.365,.295,'HIRING AND DEPARTURES','Monthly employee movements');ax.bar([x-.18 for x in xs],q[2].hires,.34,color=C[0],label='Hires');ax.bar([x+.18 for x in xs],q[2].leavers,.34,color=C[1],label='Departures');ax.set_xticks(xs,months);ax.set_ylim(0,max(q[2].hires.max(),q[2].leavers.max())*1.3);style(ax);ax.legend(frameon=False,ncol=2,fontsize=8)
  ax=panel(.205,.09,.405,.30,'TURNOVER BY DEPARTMENT','Departures / mean opening and closing headcount',left=.115);bars(ax,q[3].department,q[3].turnover_rate,lambda v:f'{v:.1%}')
  bx,by,bw,bh=.62,.09,.365,.30;vals=q[4].leavers.tolist();labels=q[4].exit_type.tolist();title='EXIT COMPOSITION';total=k['leavers']
 ax=panel(bx,by,bw,bh,title,'Count and share of '+('bookings' if HC else 'departures'));ax.remove();ax=fig.add_axes([bx+.008,by+.025,.14,.19]);ax.pie(vals,startangle=90,colors=C[:len(vals)],wedgeprops={'width':.25,'edgecolor':'white'});ax.text(0,0,f'{total:,}',ha='center',va='center',fontsize=20,weight='bold',color=INK)
 for i,(l,v) in enumerate(zip(labels,vals)):txt(bx+.155,by+.18-i*.055,f'{l}   {v:,}\n{v/total:.1%}',9,C[i])
 txt(.02,.051,'Illustrative 30-minute wait target; descriptive associations only.' if HC else 'Turnover uses mean opening and closing headcount; period rates are not annualized.',9)
 txt(.02,.022,'SYNTHETIC EDUCATIONAL DATA  •  STATIC PYTHON PREVIEW',8);txt(.98,.022,'PYTHON  /  SQL  /  POWER BI DAX',8,ha='right')
 fig.savefig(ROOT/'reports/dashboard_preview.png',dpi=100,facecolor=BG);plt.close(fig)
 print('Created dashboard_preview.png (1600 × 900).')
if __name__=='__main__':main()
