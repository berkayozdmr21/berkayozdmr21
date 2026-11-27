"""Render the profile's original, deterministic technology animation.

Requires Pillow 10.4+: python -m pip install Pillow
Run from any directory. No network requests or third-party image assets.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'animation'
W, H = 1000, 520
FRAMES, DURATION, TRANSITION = 56, 80, 7
BG, PANEL, LINE = '#0d1117', '#131b24', '#293441'
TEXT, MUTED = '#e6edf3', '#9baab8'
FONT_ROOT = Path('C:/Windows/Fonts')
FONTS = {}


def font(size, bold=False):
    key = size, bold
    if key not in FONTS:
        path = FONT_ROOT / ('segoeuib.ttf' if bold else 'segoeui.ttf')
        if not path.exists():
            path = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
        FONTS[key] = ImageFont.truetype(str(path), size)
    return FONTS[key]


def text(d, xy, value, size=16, fill=TEXT, bold=False, anchor=None):
    d.text(xy, str(value), font=font(size, bold), fill=fill, anchor=anchor)


def box(d, rect, fill=PANEL, outline=LINE, radius=12, width=1):
    d.rounded_rectangle(tuple(round(x) for x in rect), radius, fill, outline, width)


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def point(d, xy, color, r=4):
    x, y = xy
    d.ellipse((x-r, y-r, x+r, y+r), fill=color)


def arrow(d, a, b, color=LINE, width=2):
    d.line([a, b], fill=color, width=width)
    theta = math.atan2(b[1]-a[1], b[0]-a[0])
    p = [(b[0]-8*math.cos(theta+s), b[1]-8*math.sin(theta+s)) for s in (-.5, .5)]
    d.polygon([b, *p], fill=color)


def packet(d, a, b, t, color, count=2):
    d.line([a, b], fill=LINE, width=2)
    for k in range(count):
        u = (t + k/count) % 1
        point(d, (lerp(a[0], b[0], u), lerp(a[1], b[1], u)), color, 4)


def label_box(d, rect, title, subtitle='', accent='#8ebba2'):
    box(d, rect, '#17222c', accent, 9)
    x1, y1, x2, y2 = rect
    text(d, ((x1+x2)/2, y1+15), title, 17, bold=True, anchor='mt')
    if subtitle:
        text(d, ((x1+x2)/2, y1+42), subtitle, 13, MUTED, anchor='mt')


def regression(d, t, c):
    text(d, (28, 18), 'VERİ → MODEL → TAHMİN', 14, MUTED, True)
    x0, y0, x1, y1 = 66, 258, 600, 55
    for i in range(6):
        x = x0 + (x1-x0)*i/5
        y = y0 - (y0-y1)*i/5
        d.line([(x, y0), (x, y1)], fill='#202c37')
        d.line([(x0, y), (x1, y)], fill='#202c37')
    d.line([(x0, y1), (x0, y0), (x1, y0)], fill='#657684', width=2)
    values = [(i/13, .16+.68*i/13 + math.sin(i*2.2)*.10) for i in range(14)]
    mean_x = sum(x for x,y in values)/len(values)
    mean_y = sum(y for x,y in values)/len(values)
    slope = sum((x-mean_x)*(y-mean_y) for x,y in values)/sum((x-mean_x)**2 for x,y in values)
    intercept = mean_y-slope*mean_x
    fit = ease(t/.72)
    m, b = lerp(-.12, slope, fit), lerp(.55, intercept, fit)
    coord = lambda x,y: (x0+x*(x1-x0), y0-y*(y0-y1))
    for x,y in values:
        d.line([coord(x,y), coord(x,m*x+b)], fill='#4e5546', width=1)
        point(d, coord(x,y), '#b9c6cf', 4)
    d.line([coord(0,b),coord(1,m+b)], fill=c, width=3)
    text(d, (86, 274), 'girdi  x', 13, MUTED)
    text(d, (516, 274), 'ŷ = wx + b', 15, c, True)
    box(d, (380, 14, 609, 44), '#1d2c2b', None, 7)
    text(d, (494, 20), 'Örnek: doğrusal regresyon', 13, c, anchor='mt')


def vision(d, t, c):
    text(d, (28, 18), 'GÖRÜNTÜ → NESNE → METİN', 14, MUTED, True)
    box(d, (29, 56, 408, 276), '#1a2731', '#334654')
    for x in range(44, 400, 28):
        d.line([(x,68),(x,263)], fill='#233442')
    d.polygon([(43,261),(131,152),(275,152),(394,261)], fill='#26333c')
    dx = math.sin(t*math.pi*2)*14
    car = [(x+dx,y) for x,y in [(111,182),(141,162),(227,162),(256,186),(280,190),(280,226),(95,226),(95,195)]]
    d.polygon(car, fill='#8ba0a5')
    d.polygon([(147+dx,169),(223+dx,169),(242+dx,186),(128+dx,186)],fill='#32434c')
    point(d,(132+dx,226),'#101820',14); point(d,(249+dx,226),'#101820',14)
    box(d,(154+dx,202,224+dx,217),'#e1e5df',None,2)
    text(d,(189+dx,202),'31 BK 021',9,'#283b41',True,'mt')
    d.rectangle((83+dx,148,291+dx,244), outline=c, width=2)
    box(d,(83+dx,125,208+dx,148), c,None,3)
    text(d,(91+dx,127),'araç / YOLOv8',12,BG,True)
    scan=63+188*((t*1.7)%1)
    d.line([(40,scan),(397,scan)],fill=c,width=1)
    arrow(d,(421,164),(454,164),c)
    label_box(d,(464,77,610,153),'TESPİT','OpenCV + YOLO',c)
    label_box(d,(464,184,610,260),'OCR','31 BK 021',c)
    packet(d,(537,154),(537,181),t*2,c,1)


def frontend(d, t, c):
    text(d,(28,18),'TASARIM → BİLEŞEN → ETKİLEŞİM',14,MUTED,True)
    box(d,(30,59,609,279),'#101820','#415362',10)
    d.line([(30,86),(609,86)], fill=LINE)
    for i in range(3):point(d,(46+i*13,73),['#bb8370','#c6ad7c','#85a991'][i],3)
    text(d,(104,64),'localhost / uygulama',12,MUTED)
    box(d,(44,101,154,264),'#19242f',None,6)
    for i in range(4):
        box(d,(56,120+i*32,141,139+i*32),'#314653' if i==int(t*4)%4 else '#23313d',None,4)
    text(d,(174,105),'Arayüz, parça parça.',21,TEXT,True)
    d.line([(175,139),(379,139)], fill='#4a5e6c',width=4)
    for i in range(3):
        x=174+i*134
        box(d,(x,162,x+120,248),'#1c2b35',None,7)
        h=22+22*(.5+.5*math.sin(t*math.pi*2+i))
        for j in range(4):
            bh=12+(j+1)*h/5
            box(d,(x+15+j*23,230-bh,x+29+j*23,230),c,None,2)
    cursor=(int(510+50*math.sin(t*math.pi*2)),int(133+27*math.cos(t*math.pi*2)))
    d.polygon([cursor,(cursor[0]+1,cursor[1]+19),(cursor[0]+7,cursor[1]+13),(cursor[0]+16,cursor[1]+12)],fill=TEXT)


def backend(d,t,c):
    text(d,(28,18),'İSTEK → SERVİS → YANIT',14,MUTED,True)
    a,b,cc,db=(91,165),(272,165),(454,165),(559,261)
    packet(d,(151,165),(211,165),t*1.4,c)
    packet(d,(333,165),(393,165),t*1.4-.2,c)
    packet(d,(454,205),(559,240),t*1.4-.5,c,1)
    label_box(d,(30,125,151,205),'İSTEMCİ','HTTP / JSON',c)
    label_box(d,(211,125,333,205),'API','REST',c)
    label_box(d,(393,125,515,205),'SERVİS','iş kuralları',c)
    box(d,(511,240,609,282),'#26332e',c,6)
    text(d,(560,250),'VERİ',15,c,True,'mt')
    # Response follows a separate return route.
    route=[(454,115),(454,83),(91,83),(91,115)]
    d.line(route,fill='#3d4b50',width=2)
    u=(t*1.4)%1
    if u<.12:p=(454,lerp(115,83,u/.12))
    elif u<.88:p=(lerp(454,91,(u-.12)/.76),83)
    else:p=(91,lerp(83,115,(u-.88)/.12))
    point(d,p,'#c5d7c8',4)
    text(d,(272,54),'200 OK  /  yapılandırılmış yanıt',13,c,anchor='mt')


def database(d,t,c):
    text(d,(28,18),'KAYDET → SORGULA → AKIŞI SÜRDÜR',14,MUTED,True)
    for i,title in enumerate(['TALEP','DOĞRULA','TAMAMLA']):
        x=28+i*151
        label_box(d,(x,75,x+122,137),title,'',c if i<=int(t*3)%3 else LINE)
        if i<2:packet(d,(x+124,105),(x+149,105),t*2-i*.2,c,1)
    x,y=493,125
    d.rectangle((x-63,y,x+63,y+102),fill='#233339',outline=c,width=2)
    d.ellipse((x-63,y+79,x+63,y+119),fill='#233339',outline=c,width=2)
    d.rectangle((x-61,y+64,x+61,y+94),fill='#233339')
    d.arc((x-63,y+42,x+63,y+82),0,180,fill=c,width=2)
    d.ellipse((x-63,y-20,x+63,y+20),fill='#30454a',outline=c,width=2)
    text(d,(x,y+35),'SQL',24,TEXT,True,'mt')
    packet(d,(390,137),(450,169),t*1.3,c,1)
    box(d,(28,182,383,273),'#17222c',None,8)
    text(d,(44,197),'SELECT durum, COUNT(*)',17,c)
    text(d,(44,224),'FROM işler GROUP BY durum;',16,TEXT)
    text(d,(29,286),'Temporal: kalıcı adımlar  ·  PostgreSQL: ilişkisel veri',13,MUTED)


def mobile(d,t,c):
    text(d,(28,18),'TEK ARAYÜZ → MOBİL DENEYİM',14,MUTED,True)
    box(d,(222,49,397,294),'#101820','#687885',22,2)
    box(d,(234,63,385,281),'#1c2a35',None,13)
    box(d,(278,64,341,72),'#101820',None,4)
    text(d,(250,87),'Merhaba, Berkay.',14,TEXT,True)
    box(d,(248,116,372,168),'#354d4e',None,8)
    text(d,(259,125),'Her cihazda',13,c,True)
    text(d,(259,144),'aynı deneyim.',12,TEXT)
    for i in range(3):
        y=181+i*27
        box(d,(248,y,372,y+20),'#293b48',None,4)
        point(d,(259,y+10),c,3)
        d.line([(272,y+9),(345-(i%2)*22,y+9)],fill='#91a4b1',width=2)
    pulse=.5+.5*math.sin(t*math.pi*2)
    box(d,(70,101,169,162),'#1c2c36',c,9)
    text(d,(120,120),'WIDGET',15,c,True,'mt')
    packet(d,(171,132),(221,132),t*1.5,c,1)
    label_box(d,(453,159,585,232),'API','veri eşitleme',c)
    packet(d,(399,202),(451,202),t*1.5,c,1)
    point(d,(363,92),c,3+2*pulse)
    text(d,(520,249),'Flutter + Dart',14,MUTED,anchor='mt')


def project3d(x,y,z,angle):
    xx=x*math.cos(angle)-z*math.sin(angle)
    zz=x*math.sin(angle)+z*math.cos(angle)
    return (320+xx*62+zz*28,194-y*62+zz*17)


def game(d,t,c):
    text(d,(28,18),'MODEL → SAHNE → OYNANIŞ',14,MUTED,True)
    for k in range(-3,4):
        p=lambda x,z:(320+x*64+z*29,216+z*17)
        d.line([p(k,-3),p(k,3)],fill='#293a43')
        d.line([p(-3,k),p(3,k)],fill='#293a43')
    angle=t*math.pi*2
    vertices=[project3d(x,y,z,angle) for x,y,z in [(-.7,0,-.7),(.7,0,-.7),(.7,0,.7),(-.7,0,.7),(-.7,1.4,-.7),(.7,1.4,-.7),(.7,1.4,.7),(-.7,1.4,.7)]]
    for face,col in [([0,1,5,4],'#526353'),([1,2,6,5],'#384e48'),([4,5,6,7],'#7d906b')]:
        d.polygon([vertices[i] for i in face],fill=col)
    for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
        d.line([vertices[a],vertices[b]],fill=c,width=2)
    # A tiny playable character jumps alongside the 3D model.
    xx=510+25*math.sin(t*math.pi*2)
    yy=224-abs(math.sin(t*math.pi*2))*46
    point(d,(xx,yy-22),TEXT,8)
    d.line([(xx,yy-12),(xx,yy+7)],fill=c,width=5)
    d.line([(xx-11,yy+22),(xx,yy+7),(xx+11,yy+22)],fill=c,width=4)
    d.line([(xx-13,yy),(xx,yy-8),(xx+13,yy-2)],fill=c,width=4)
    text(d,(31,69),'SCENE',13,MUTED,True)
    for i,name in enumerate(['Camera','Light','Mesh','Player']):
        yy=104+i*27
        d.polygon([(35,yy-4),(39,yy),(35,yy+4),(31,yy)],outline=c if name=='Mesh' else MUTED)
        text(d,(47,96+i*27),name,14,c if name=='Mesh' else MUTED)
    text(d,(320,280),'Blender: model  /  Unity + C#: etkileşim',14,MUTED,anchor='mt')


def gitflow(d,t,c):
    text(d,(28,18),'FİKİR → BRANCH → REVIEW → MERGE',14,MUTED,True)
    d.line([(55,204),(585,204)],fill='#57666f',width=3)
    d.line([(153,204),(225,113),(401,113),(490,204)],fill=c,width=3)
    for x in [70,153,490,578]:
        point(d,(x,204),BG,8);d.ellipse((x-7,197,x+7,211),outline=MUTED,width=2)
    for x in [239,320,390]:point(d,(x,113),c,7)
    route=[(153,204),(225,113),(401,113),(490,204),(578,204)]
    lengths=[math.dist(route[i],route[i+1]) for i in range(len(route)-1)]
    progress=(t%1)*sum(lengths)
    for i,length in enumerate(lengths):
        if progress<=length:
            a,b=route[i],route[i+1];p=(lerp(a[0],b[0],progress/length),lerp(a[1],b[1],progress/length));break
        progress-=length
    point(d,p,TEXT,5)
    text(d,(55,233),'main',16,MUTED,True)
    text(d,(237,74),'feature / geliştirme',15,c,True)
    box(d,(248,157,403,185),'#25372c',None,6)
    d.line([(265,170),(270,175),(279,165)],fill='#b4cfb3',width=2)
    text(d,(334,161),'kontrol + review',13,'#b4cfb3',anchor='mt')
    text(d,(488,263),'merge',16,c,True)


SCENES = [
    ('Yapay zekâ', ['Veriden', 'öğrenen modeller.'], ['Python','PyTorch','Google Colab'], ['Noktalar, bir modele dönüşür.', 'Regresyon çizgisi veriye yaklaşır.'], '#b5c88c', regression, 'VERİ'),
    ('Bilgisayarlı görü', ['Piksellerden', 'anlam çıkar.'], ['OpenCV','YOLOv8','EasyOCR'], ['Nesneyi bul, hareketini izle,', 'görüntüdeki metni oku.'], '#d3b17c', vision, 'GÖRÜ'),
    ('Web geliştirme', ['Tasarımdan', 'yaşayan arayüze.'], ['React','TypeScript','JavaScript','Vite','Figma'], ['Bileşenleri bir araya getir.', 'Etkileşimi her ekrana taşı.'], '#8fbcc6', frontend, 'WEB'),
    ('Backend & API', ['Görünmeyen', 'sistemi tasarla.'], ['ASP.NET','FastAPI','Laravel','REST API'], ['İsteği karşıla, kuralları uygula,', 'yapılandırılmış yanıtı ilet.'], '#c7a88f', backend, 'API'),
    ('Veri & iş akışı', ['Veriyi koru.', 'Akışı sürdür.'], ['PostgreSQL','SQL','Temporal'], ['İlişkisel veriyi sorgula.', 'İş adımlarını kalıcı olarak yürüt.'], '#90b6b0', database, 'VERİ / AKIŞ'),
    ('Mobil geliştirme', ['Her dokunuşta', 'tutarlı deneyim.'], ['Flutter','Dart'], ['Widget’larla arayüz kur.', 'Mobil ekranı API’ye bağla.'], '#92b9d2', mobile, 'MOBİL'),
    ('Oyun & 3D', ['Sahneyi kur.', 'Hayat ver.'], ['Unity','C#','Blender'], ['Modeli üç boyutta şekillendir.', 'Hareketi ve etkileşimi kodla.'], '#b3c28c', game, 'OYUN / 3D'),
    ('Sürüm kontrolü', ['Birlikte geliştir.', 'Güvenle birleştir.'], ['Git','GitHub'], ['Değişikliği bir dalda geliştir.', 'İncele, doğrula ve birleştir.'], '#c4aece', gitflow, 'GIT'),
]


def render(index, t):
    area,title,tech,description,accent,draw_stage,short=SCENES[index]
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    box(d,(1,1,W-2,H-2),BG,LINE,16)
    text(d,(33,24),'TEKNOLOJİLERİM / HAREKETLİ BİR BAKIŞ',14,MUTED,True)
    text(d,(33,52),'Fikirden çalışan sisteme.',23,TEXT,True)
    text(d,(966,36),f'{index+1:02d} / 08',15,accent,True,'rt')
    d.line([(33,99),(967,99)],fill=LINE)
    text(d,(33,129),area.upper(),14,accent,True)
    for i,line in enumerate(title):text(d,(31,164+i*39),line,29,TEXT,True)
    for i,line in enumerate(description):text(d,(33,267+i*26),line,16,MUTED)
    x,y=33,346
    for name in tech:
        width=d.textlength(name,font=font(14))+22
        if x+width>309:x,y=33,y+35
        box(d,(x,y,x+width,y+27),'#1c2831',LINE,6)
        text(d,(x+11,y+3),name,14,TEXT)
        x+=width+7
    stage=Image.new('RGB',(638,310),PANEL)
    draw_stage(ImageDraw.Draw(stage),t,accent)
    im.paste(stage,(329,127))
    box(d,(328,126,968,438),None,LINE,12)
    for j,scene in enumerate(SCENES):
        xx=33+j*118
        text(d,(xx,461),scene[6],12,accent if j==index else MUTED,bold=j==index)
        box(d,(xx,485,xx+108,489),'#26323d',None,2)
        if j==index:box(d,(xx,485,xx+max(2,108*t),489),accent,None,2)
    return im


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    samples=[render(i,.62) for i in range(8)]
    overview=Image.new('RGB',(W*2,H*4),BG)
    for i,im in enumerate(samples):overview.paste(im,((i%2)*W,(i//2)*H))
    overview.save(OUT/'technology-overview.png',optimize=True)
    palette=overview.resize((500,520)).quantize(colors=128)
    frames=[]
    for i in range(8):
        for k in range(FRAMES):
            t=k/(FRAMES-1)
            im=render(i,t)
            if k>=FRAMES-TRANSITION:
                u=ease((k-(FRAMES-TRANSITION))/(TRANSITION-1))
                im=Image.blend(im,render((i+1)%8,0),u)
            frames.append(im.quantize(palette=palette,dither=Image.Dither.NONE))
        print(f'Rendered {i+1}/8: {SCENES[i][0]}',flush=True)
    target=OUT/'technology-in-motion.gif'
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=DURATION,loop=0,optimize=True,disposal=1)
    with Image.open(target) as gif:
        assert gif.n_frames>400 and gif.info.get('loop')==0
        duration=sum((gif.seek(i) or gif.info.get('duration',0)) for i in range(gif.n_frames))
        print(f'GIF: {gif.n_frames} frames, {duration/1000:.2f}s, {target.stat().st_size/1024/1024:.2f} MiB')
    assert target.stat().st_size<10*1024*1024,'Review GIF size before publication.'


if __name__=='__main__':
    build()
