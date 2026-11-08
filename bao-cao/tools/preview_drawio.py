"""Simple geometry preview when the draw.io desktop exporter is unavailable."""
from pathlib import Path
import sys
import re
from xml.etree import ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'docs'/'ibanking-so-do-day-du.drawio'
DEST=ROOT/'docs'/'previews'
DEST.mkdir(exist_ok=True)
FONT='C:/Windows/Fonts/arial.ttf'
bold='C:/Windows/Fonts/arialbd.ttf'

tree=ET.parse(SRC)
for index,diagram in enumerate(tree.getroot().findall('diagram'),1):
    model=diagram.find('mxGraphModel'); w=int(model.get('pageWidth')); h=int(model.get('pageHeight'))
    im=Image.new('RGB',(w,h),model.get('background','#FFFFFF')); dr=ImageDraw.Draw(im)
    cells={c.get('id'):c for c in model.find('root').findall('mxCell')}
    boxes={}
    def box(cell_id):
        if cell_id in boxes:return boxes[cell_id]
        c=cells[cell_id];g=c.find('mxGeometry')
        x,y,bw,bh=[float(g.get(k,0)) for k in ('x','y','width','height')]
        parent=c.get('parent')
        if parent in cells and parent not in ('0','1'):
            px,py,_,_=box(parent);x+=px;y+=py
        boxes[cell_id]=(x,y,bw,bh);return boxes[cell_id]
    for c in cells.values():
        if c.get('vertex')=='1':box(c.get('id'))
    def split(text,font,max_width):
        lines=[]
        for para in text.split('\n'):
            words=para.split();cur=''
            for word in words:
                test=(cur+' '+word).strip()
                if cur and dr.textbbox((0,0),test,font=font)[2]>max_width:
                    lines.append(cur);cur=word
                else:cur=test
            lines.append(cur)
        return lines
    for c in cells.values():
        if c.get('vertex')!='1':continue
        id=c.get('id');x,y,bw,bh=boxes[id]; style=c.get('style','');value=c.get('value','')
        if not value and 'text;' in style:continue
        color='#E7F2F8';outline='#50738A'
        if 'fillColor=#E3F1E2' in style:color='#E3F1E2';outline='#6A9A67'
        elif 'fillColor=#F3F3F3' in style:color='#F3F3F3';outline='#888888'
        elif 'fillColor=#E9E3F3' in style:color='#E9E3F3';outline='#8970A7'
        elif 'fillColor=#FFF1C9' in style:color='#FFF1C9';outline='#B58E34'
        elif 'fillColor=#E1F1DF' in style:color='#E1F1DF';outline='#699A65'
        elif 'fillColor=#FAE0DE' in style:color='#FAE0DE';outline='#C4756F'
        elif 'fillColor=#F7FAFC' in style:color='#F7FAFC';outline='#B8CBD4'
        fill_match=re.search(r'fillColor=(#[0-9A-Fa-f]{6})',style)
        stroke_match=re.search(r'strokeColor=(#[0-9A-Fa-f]{6})',style)
        if fill_match:color=fill_match.group(1)
        if stroke_match:outline=stroke_match.group(1)
        if 'shape=umlActor' in style:
            cx=x+bw/2;dr.ellipse((cx-12,y,cx+12,y+24),outline=outline,width=2)
            dr.line((cx,y+24,cx,y+70),fill=outline,width=2)
            dr.line((cx-28,y+42,cx+28,y+42),fill=outline,width=2)
            dr.line((cx,y+70,cx-26,y+100),fill=outline,width=2)
            dr.line((cx,y+70,cx+26,y+100),fill=outline,width=2)
            y+=105;bh=30
        elif 'shape=cylinder3' in style:
            dr.rounded_rectangle((x,y,x+bw,y+bh),radius=15,fill=color,outline=outline,width=2)
            dr.ellipse((x,y-5,x+bw,y+24),fill=color,outline=outline,width=2)
        elif 'rhombus;' in style:
            dr.polygon([(x+bw/2,y),(x+bw,y+bh/2),(x+bw/2,y+bh),(x,y+bh/2)],fill=color,outline=outline)
        elif 'ellipse;' in style:
            dr.ellipse((x,y,x+bw,y+bh),fill=color,outline=outline,width=2)
        elif 'swimlane;' in style:
            dr.rectangle((x,y,x+bw,y+bh),fill=color,outline=outline,width=2)
        elif 'text;' not in style:
            dr.rounded_rectangle((x,y,x+bw,y+bh),radius=12,fill=color,outline=outline,width=2)
        size_match=re.search(r'fontSize=(\d+)',style)
        fs=int(size_match.group(1)) if size_match else 15
        font=ImageFont.truetype(bold if 'fontStyle=1' in style else FONT,fs)
        lines=split(value,font,max(30,bw-20))
        line_h=fs+5
        ty=y+8 if ('align=left' in style or 'verticalAlign=top' in style or 'swimlane;' in style) else y+(bh-len(lines)*line_h)/2
        for line in lines:
            if not line:ty+=line_h;continue
            tw=dr.textbbox((0,0),line,font=font)[2]
            tx=x+10 if ('align=left' in style or 'verticalAlign=top' in style) else x+(bw-tw)/2
            font_match=re.search(r'fontColor=(#[0-9A-Fa-f]{6})',style)
            dr.text((tx,ty),line,font=font,fill=font_match.group(1) if font_match else '#173045')
            ty+=line_h
    # Approximate edge preview; draw.io itself owns the editable routing.
    for c in cells.values():
        if c.get('edge')!='1':continue
        a,b=c.get('source'),c.get('target')
        if a not in boxes or b not in boxes:continue
        ax,ay,aw,ah=boxes[a];bx,by,bw,bh=boxes[b]
        ac=(ax+aw/2,ay+ah/2);bc=(bx+bw/2,by+bh/2)
        dx,dy=bc[0]-ac[0],bc[1]-ac[1]
        if abs(dx)>abs(dy):
            p1=(ax+aw if dx>0 else ax,ac[1]);p2=(bx if dx>0 else bx+bw,bc[1])
        else:
            p1=(ac[0],ay+ah if dy>0 else ay);p2=(bc[0],by if dy>0 else by+bh)
        color='#718999'
        dr.line((p1,p2),fill=color,width=2)
        label=c.get('value','')
        if label:
            font=ImageFont.truetype(FONT,12)
            mx,my=(p1[0]+p2[0])/2,(p1[1]+p2[1])/2-16
            tw=dr.textbbox((0,0),label,font=font)[2]
            dr.rectangle((mx-tw/2-4,my-2,mx+tw/2+4,my+16),fill='white')
            dr.text((mx-tw/2,my),label,font=font,fill='#425766')
    path=DEST/f'{index:02d}-{diagram.get("name").lower().replace(" ","-")}.png'
    im.save(path)
    print(path)
