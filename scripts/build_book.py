"""Build original scores, MIDI, synthetic audio and an offline Chinese textbook."""
from __future__ import annotations
import argparse, html, json, math, re, struct, wave
from pathlib import Path
import xml.etree.ElementTree as ET
import markdown, mido, numpy as np, verovio
from book_exercises import EXERCISES

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/'book'
ASSETS=BOOK/'assets'
DIV=8
TYPES={4:('whole',False),3:('half',True),2:('half',False),1.5:('quarter',True),
       1:('quarter',False),.75:('eighth',True),.5:('eighth',False),.25:('16th',False)}


def pitch(name):
    m=re.fullmatch(r'([A-G])([#b]?)([0-8])',name)
    if not m: raise ValueError(name)
    step,acc,octave=m.groups();alter={'':0,'#':1,'b':-1}[acc]
    number=(int(octave)+1)*12+{'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[step]+alter
    return step,alter,int(octave),number


def child(parent,tag,text=None,**attrs):
    e=ET.SubElement(parent,tag,attrs)
    if text is not None:e.text=str(text)
    return e


def length(e):return e['meter'][0]*4/e['meter'][1]


def validate(e):
    assert len(e['rh'])==len(e['lh']) and len(e['rh'])>0,e['id']
    if e['chords']:assert len(e['chords'])==len(e['rh'])
    for hand in ('rh','lh'):
        pending=None
        for bar in e[hand]:
            assert math.isclose(sum(n['duration'] for n in bar),length(e)),(e['id'],hand,bar)
            for event in bar:
                assert event['duration'] in TYPES
                for p in event['pitches']:
                    assert 40<=pitch(p)[3]<=100,(e['id'],p)
                if 'finger' in event:assert 1<=event['finger']<=5
                if event.get('tie')=='start':
                    assert pending is None;pending=event['pitches']
                elif event.get('tie')=='stop':
                    assert pending==event['pitches'];pending=None
                else:assert pending is None,'Unclosed tie before next note'
        assert pending is None


def musicxml(e):
    root=ET.Element('score-partwise',version='4.0')
    work=child(root,'work');child(work,'work-title',e['id'])
    ident=child(root,'identification');child(ident,'creator','Modern Keyboard Textbook',type='composer')
    plist=child(root,'part-list');sp=child(plist,'score-part',id='P1')
    child(sp,'part-name','Piano' if e['left_role']=='left-hand' else 'Keys + Bass ref.')
    part=child(root,'part',id='P1')
    for bi,(rh,lh) in enumerate(zip(e['rh'],e['lh'])):
        measure=child(part,'measure',number=str(bi+1))
        if bi==0:
            a=child(measure,'attributes');child(a,'divisions',DIV)
            child(child(a,'key'),'fifths',e['key'])
            t=child(a,'time');child(t,'beats',e['meter'][0]);child(t,'beat-type',e['meter'][1])
            child(a,'staves',2)
            for num,sign,line in [(1,'G',2),(2,'F',4)]:
                c=child(a,'clef',number=str(num));child(c,'sign',sign);child(c,'line',line)
            d=child(measure,'direction',placement='above');dt=child(d,'direction-type');met=child(dt,'metronome')
            child(met,'beat-unit','quarter')
            if e['meter']==[6,8]:child(met,'beat-unit-dot')
            child(met,'per-minute',round(e['bpm']*2/3) if e['meter']==[6,8] else e['bpm'])
            child(d,'staff',1);child(d,'sound',tempo=str(e['bpm']))
            d=child(measure,'direction',placement='above');child(child(d,'direction-type'),'words','R.H. / L.H.' if e['left_role']=='left-hand' else 'Upper: keys / lower: bass reference')
            child(d,'staff',1)
        if e['chords']:
            d=child(measure,'direction',placement='above');child(child(d,'direction-type'),'words',e['chords'][bi]);child(d,'staff',1)
        for staff,events in [(1,rh),(2,lh)]:
            if staff==2:child(child(measure,'backup'),'duration',int(length(e)*DIV))
            defaults={step:0 for step in 'ABCDEFG'}
            for step in 'FCGDAEB'[:max(0,e['key'])]:defaults[step]=1
            for step in 'BEADGCF'[:max(0,-e['key'])]:defaults[step]=-1
            accidentals={};position=0.
            for ei,event in enumerate(events):
                for ci,p in enumerate(event['pitches'] or [None]):
                    note=child(measure,'note')
                    if ci:child(note,'chord')
                    if p is None:child(note,'rest')
                    else:
                        step,alter,octave,_=pitch(p);pe=child(note,'pitch');child(pe,'step',step)
                        if alter:child(pe,'alter',alter)
                        child(pe,'octave',octave)
                    child(note,'duration',round(event['duration']*DIV))
                    if event.get('tie'):child(note,'tie',type=event['tie'])
                    child(note,'voice',staff)
                    typ,dot=TYPES[event['duration']];child(note,'type',typ)
                    if dot:child(note,'dot')
                    if p is not None:
                        key=(step,octave);previous=accidentals.get(key,defaults[step])
                        if alter!=previous:child(note,'accidental',{-1:'flat',0:'natural',1:'sharp'}[alter])
                        accidentals[key]=alter
                    child(note,'staff',staff)
                    if ci==0 and p is not None and event['duration']==.5:
                        group=1.5 if e['meter']==[6,8] else 1.
                        group_index=math.floor((position+1e-6)/group)
                        before=(ei>0 and events[ei-1]['duration']==.5 and bool(events[ei-1]['pitches'])
                                and math.floor((position-.5+1e-6)/group)==group_index)
                        after=(ei+1<len(events) and events[ei+1]['duration']==.5 and bool(events[ei+1]['pitches'])
                               and math.floor((position+.5+1e-6)/group)==group_index)
                        if before or after:child(note,'beam','continue' if before and after else 'end' if before else 'begin',number='1')
                    if event.get('finger') or event.get('tie'):
                        no=child(note,'notations')
                        if event.get('tie'):child(no,'tied',type=event['tie'])
                        if event.get('finger'):child(child(no,'technical'),'fingering',event['finger'])
                position+=event['duration']
        if bi==len(e['rh'])-1:child(child(measure,'barline',location='right'),'bar-style','light-heavy')
    return ET.tostring(root,encoding='unicode',xml_declaration=True)


def sounded(e):
    events=[]
    for channel,hand in enumerate(('rh','lh')):
        t=0.;pending=None
        for bar in e[hand]:
            for n in bar:
                for p in n['pitches']:
                    if n.get('tie')=='stop':
                        assert pending is not None
                        events[pending]['duration']+=n['duration'];pending=None
                    else:
                        events.append(dict(start=t,duration=n['duration'],pitch=pitch(p)[3],
                                           channel=channel,velocity=78 if channel==0 else 49))
                        if n.get('tie')=='start':pending=len(events)-1
                t+=n['duration']
    return events


def midi(e,events,hand=None):
    mid=mido.MidiFile(ticks_per_beat=480)
    meta=mido.MidiTrack();mid.tracks.append(meta)
    meta.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(e['bpm']),time=0))
    meta.append(mido.MetaMessage('time_signature',numerator=e['meter'][0],denominator=e['meter'][1],time=0))
    for channel,label in [(0,'Right hand'),(1,'Bass reference' if e['left_role']!='left-hand' else 'Left hand')]:
        if hand is not None and channel!=hand:continue
        track=mido.MidiTrack();mid.tracks.append(track)
        track.append(mido.MetaMessage('track_name',name=label,time=0))
        track.append(mido.Message('program_change',program=0,channel=channel,time=0));pending=[]
        for ev in events:
            if ev['channel']!=channel:continue
            pending += [(round(ev['start']*480),1,mido.Message('note_on',note=ev['pitch'],velocity=ev['velocity'],channel=channel)),
                        (round((ev['start']+ev['duration'])*480),0,mido.Message('note_off',note=ev['pitch'],velocity=0,channel=channel))]
        if e['pedal']:
            for i in range(len(e['rh'])):
                pending += [(round((i*length(e)+.1)*480),2,mido.Message('control_change',control=64,value=127,channel=channel)),
                            (round(((i+1)*length(e)-.1)*480),2,mido.Message('control_change',control=64,value=0,channel=channel))]
        last=0
        for tick,_,message in sorted(pending,key=lambda x:(x[0],x[1])):
            message.time=tick-last;track.append(message);last=tick
        end=round(len(e['rh'])*length(e)*480)
        track.append(mido.MetaMessage('end_of_track',time=max(0,end-last)))
    return mid


def audio(e,events,path):
    rate=16000;unit=60/e['bpm'];intro=length(e)*unit;tail=.45
    buffer=np.zeros(math.ceil((intro+len(e['rh'])*length(e)*unit+tail)*rate),dtype=np.float64)
    # Only the count-in clicks. The piece itself is rendered without a click track.
    pulses=[0,1.5] if e['meter']==[6,8] else list(range(e['meter'][0]))
    for beat in pulses:
        at=int(beat*unit*rate);t=np.arange(int(.045*rate))/rate
        buffer[at:at+len(t)]+=.12*np.sin(2*np.pi*(1250 if beat==0 else 900)*t)*np.exp(-95*t)
    for ev in events:
        seconds=ev['duration']*unit
        if e['pedal']:
            end=ev['start']+ev['duration'];bar_end=(math.floor(ev['start']/length(e))+1)*length(e)-.1
            if end<bar_end:seconds=(bar_end-ev['start'])*unit
        count=math.ceil((seconds+.22)*rate);t=np.arange(count)/rate
        hz=440*2**((ev['pitch']-69)/12)
        envelope=np.minimum(1,t/.008)*(.75*np.exp(-3*t)+.25*np.exp(-.65*t))
        envelope*=np.exp(-np.maximum(0,t-seconds)*27)
        tone=sum(amp*np.sin(2*np.pi*hz*harmonic*t) for harmonic,amp in [(1,1),(2,.34),(3,.13),(4,.06)])
        tone*=envelope*(ev['velocity']/127)*.18
        at=round((intro+ev['start']*unit)*rate);stop=min(at+len(tone),len(buffer));buffer[at:stop]+=tone[:stop-at]
    peak=float(np.abs(buffer).max())
    if peak>.94:buffer*=.94/peak
    with wave.open(str(path),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
        wav.writeframes((buffer*32767).astype('<i2').tobytes())
    return dict(seconds=round(len(buffer)/rate,3),sample_rate=rate,peak=round(float(np.abs(buffer).max()),4))


def generate_assets():
    ASSETS.mkdir(parents=True,exist_ok=True);manifest=[]
    toolkit=verovio.toolkit()
    toolkit.setOptions(dict(pageWidth=1800,pageHeight=2400,scale=42,adjustPageHeight=True,
                           breaks='auto',header='none',footer='none',spacingStaff=13,
                           pageMarginTop=30,pageMarginBottom=25,pageMarginLeft=25,pageMarginRight=25))
    for e in EXERCISES:
        validate(e);ident=e['id'];xml=musicxml(e);(ASSETS/f'{ident}.musicxml').write_text(xml,encoding='utf-8')
        if not toolkit.loadData(xml):raise RuntimeError(f'Engraving failed: {ident}')
        pages=[]
        for pi in range(1,toolkit.getPageCount()+1):
            file=f'{ident}-{pi}.svg';(ASSETS/file).write_text(toolkit.renderToSVG(pi),encoding='utf-8');pages.append(file)
        ev=sounded(e)
        for suffix,hand in [('',None),('-rh',0),('-lh',1)]:midi(e,ev,hand).save(ASSETS/f'{ident}{suffix}.mid')
        stats=audio(e,ev,ASSETS/f'{ident}.wav')
        manifest.append(dict(**e,events=ev,score_pages=pages,audio=stats))
    (ASSETS/'exercises.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest


def keyboard_diagram():
    labels=[f'{letter}{octave}' for octave in (3,4) for letter in 'CDEFGAB']+['C5']
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="714" height="218" viewBox="0 0 714 218"><rect width="714" height="218" fill="white"/><text x="12" y="22" font-family="sans-serif" font-size="15" fill="#214a54">Central C = C4 / MIDI 60</text>']
    for i,label in enumerate(labels):
        fill='#d9ece7' if label=='C4' else '#ffffff'
        svg.append(f'<rect x="{12+i*46}" y="38" width="46" height="165" fill="{fill}" stroke="#354752"/><text x="{35+i*46}" y="186" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#203944">{label}</text>')
    for i in [0,1,3,4,5,7,8,10,11,12]:svg.append(f'<rect x="{12+(i+1)*46-14}" y="38" width="28" height="104" fill="#25343c"/>')
    svg.append('</svg>');(ASSETS/'keyboard.svg').write_text(''.join(svg),encoding='utf-8')


def example(e):
    id=e['id'];images=''.join(f'<img src="assets/{p}" alt="{id} {html.escape(e["title"])} 第{i+1}页五线谱" loading="lazy">' for i,p in enumerate(e['score_pages']))
    tempo=f'附点四分音符 = {round(e["bpm"]*2/3)}' if e['meter']==[6,8] else f'四分音符 = {e["bpm"]}'
    intro='两个大拍' if e['meter']==[6,8] else f'{e["meter"][0]} 拍'
    return f'''<figure class="example" id="{id}"><figcaption><b>{id} · {html.escape(e['title'])}</b><span>{e['meter'][0]}/{e['meter'][1]} · {tempo} · {len(e['rh'])} 小节</span></figcaption>{images}
<p class="score-note">{html.escape(e['note'])}</p>
<div class="player" data-exercise="{id}"><button type="button" data-hand="all">听双手</button><button type="button" data-hand="rh">听右手</button><button type="button" data-hand="lh">听{'贝斯' if e['left_role']=='bass-reference' else '左手'}</button><button type="button" class="stop">停止</button><label>速度 <select aria-label="{id} 示范速度"><option value="0.5">50%</option><option value="0.75">75%</option><option value="1" selected>100%</option></select></label><output aria-live="polite">预备数 {intro} 后进入</output></div>
<details class="downloads"><summary>音频与可编辑乐谱</summary><p>下方音频是合成参考；先有一小节预备拍。MIDI 从第一小节直接开始，无预备拍。</p><audio controls preload="none" src="assets/{id}.wav"></audio><p><a download href="assets/{id}.musicxml">MusicXML 乐谱</a> · <a download href="assets/{id}.mid">双手 MIDI</a> · <a download href="assets/{id}-rh.mid">右手 MIDI</a> · <a download href="assets/{id}-lh.mid">{'贝斯' if e['left_role']=='bass-reference' else '左手'} MIDI</a></p></details></figure>'''


def build_html(manifest):
    keyboard_diagram()
    by_id={x['id']:x for x in manifest};contents=[];nav=[]
    chapters=sorted((BOOK/'chapters').glob('*.md'))
    for file in chapters:
        text=file.read_text(encoding='utf-8');title=text.splitlines()[0].lstrip('# ');ident='ch-'+file.stem
        # Placeholders expand after Markdown rendering to keep figure HTML intact.
        body=markdown.markdown(text,extensions=['tables','fenced_code','sane_lists']).replace('src="../assets/','src="assets/')
        body=re.sub(r'<p>\[\[EX:(E\d+)\]\]</p>',lambda m:example(by_id[m.group(1)]),body)
        if '[[EX:' in body:raise ValueError('Unexpanded example in '+str(file))
        contents.append(f'<section class="chapter" id="{ident}">{body}</section>')
        nav.append(f'<a href="#{ident}">{html.escape(title)}</a>')
    css=(BOOK/'style.css').read_text(encoding='utf-8');js=(BOOK/'player.js').read_text(encoding='utf-8')
    data=json.dumps(manifest,ensure_ascii=False).replace('</','<\\/')
    page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>从第一段旋律到独奏一首歌 · 现代流行键盘</title><style>{css}</style></head><body>
<a class="skip" href="#main">跳到正文</a><aside><a class="brand" href="#cover">现代流行键盘</a><p>从第一段旋律<br>到独奏一首歌</p><nav aria-label="全书目录">{''.join(nav)}</nav><button type="button" onclick="window.print()">打印 / 保存 PDF</button></aside>
<main id="main"><header id="cover"><p class="eyebrow">现代流行键盘 · 中文自学教材</p><h1>从第一段旋律<br>到独奏一首歌</h1><p class="subtitle">把读谱、听觉、双手配合与和声放回音乐里</p><p>第一版初稿 · 2026 年 10 月 27 日</p><p class="edition">含 24 组原创五线谱、分手示范、MIDI 与 MusicXML<br>伯克利为主要参考 · 国外开放理论与公开教学资料补充</p></header><section class="print-toc"><h1>目录</h1>{''.join(nav)}</section>
{''.join(contents)}<footer>教材首稿 v0.1 · 合成音频供参考；真人演奏与试教待验收。完整来源与版本边界见附录。</footer></main>
<script id="exercise-data" type="application/json">{data}</script><script>{js}</script></body></html>'''
    (BOOK/'index.html').write_text(page,encoding='utf-8')
    def md_example(match):
        e=by_id[match.group(1)];id=e['id']
        images='\n\n'.join(f'![{id} {e["title"]}](assets/{p})' for p in e['score_pages'])
        return f'**{id} · {e["title"]}**\n\n{images}\n\n{e["note"]}\n\n[合成参考音频](assets/{id}.wav) · [MIDI](assets/{id}.mid) · [MusicXML](assets/{id}.musicxml)'
    merged='\n\n---\n\n'.join(x.read_text(encoding='utf-8') for x in chapters).replace('../assets/','assets/')
    merged=re.sub(r'\[\[EX:(E\d+)\]\]',md_example,merged)
    (BOOK/'完整正文.md').write_text(merged,encoding='utf-8')
    return len(chapters)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--html-only',action='store_true');args=parser.parse_args()
    manifest=json.loads((ASSETS/'exercises.json').read_text(encoding='utf-8')) if args.html_only else generate_assets()
    count=build_html(manifest)
    print(json.dumps(dict(chapters=count,exercises=len(manifest),verovio=verovio.toolkit().getVersion(),html=str(BOOK/'index.html')),ensure_ascii=False))
