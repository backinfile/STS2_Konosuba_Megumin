"""Plot final Spine-runtime samples, without fitting or smoothing the data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]/'art/megumin-quartet-spine/actions-v9/verification'
before=json.loads((root/'motion-rhythm-before.json').read_text())
after=json.loads((root/'motion-rhythm.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig, axes=plt.subplots(1,3,figsize=(15,4.7),layout='constrained')
for report,label,color in [(before,'v8','#a65b4b'),(after,'v9','#217a73')]:
    for ax,clip,title in [(axes[0],'chant_enter','Chant entry: grip speed'),(axes[1],'get_up','Get up: chest speed')]:
        rows=report['traces'][clip]
        ax.plot([r['time'] for r in rows],[r['speed'] for r in rows],label=label,color=color,lw=1.8)
        ax.set(title=title,xlabel='Time (s)',ylabel='World units / s',ylim=(0,None))
        ax.grid(alpha=.18)
    rows=report['traces']['chant_enter']
    axes[2].plot([r['x'] for r in rows],[r['y'] for r in rows],label=label,color=color,lw=1.8)
    axes[2].scatter([r['x'] for r in rows[::12]],[r['y'] for r in rows[::12]],s=15,color=color)
axes[2].set(title='Chant grip path (dots every 0.1 s)',xlabel='World X',ylabel='World Y',aspect='equal')
axes[2].grid(alpha=.18)
for ax,clip in [(axes[0],'chant_enter'),(axes[1],'get_up')]:
    for c in after['checks']:
        if c['clip']==clip:ax.axvline(c['time'],color='#777',lw=.7,ls=':',alpha=.7)
for ax in axes:ax.legend(frameon=False)
fig.suptitle('Megumin v8 / v9 - unchanged duration, sampled in Spine Core 4.2.95',fontsize=14)
fig.savefig(root/'motion-comparison.png',dpi=160)
fig.savefig(root/'motion-comparison.svg')
print(root/'motion-comparison.png')
