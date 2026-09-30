"""Contact sheets from the five-state key PNGs; never edits source art."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview/five_states'
DATA=json.loads((OUT/'native_geometry.json').read_text())
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for state in [s['state'] for s in DATA['segments']]:
    frames=[f for f in DATA['qa_frames'] if f['state']==state]
    columns=2
    cell_w,cell_h=480,450
    sheet=Image.new('RGB',(columns*cell_w,((len(frames)+1)//2)*cell_h),'#090e18')
    draw=ImageDraw.Draw(sheet)
    for i,frame in enumerate(frames):
        image=Image.open(OUT/Path(frame['file']).with_suffix('.png')).convert('RGB')
        panel=image.crop((32,108,912,884)).resize((470,414),Image.Resampling.LANCZOS)
        x,y=(i%columns)*cell_w,(i//columns)*cell_h
        sheet.paste(panel,(x+5,y+31))
        draw.text((x+9,y+6),f'{state} / {frame["state_time"]:.2f} s',font=FONT,fill='#f1d5a0')
    sheet.save(OUT/f'contact_{state.lower()}.png')
    print(OUT/f'contact_{state.lower()}.png')
