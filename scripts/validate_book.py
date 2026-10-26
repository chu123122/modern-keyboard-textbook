"""Validate produced artifacts independently of their generation routines."""
import hashlib,json,math,re,wave
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import unquote,urlsplit
import mido,numpy as np
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1];BOOK=ROOT/'book';ASSETS=BOOK/'assets'
data=json.loads((ASSETS/'exercises.json').read_text(encoding='utf-8'))
assert len(data)==24 and len({e['id'] for e in data})==24
report={'exercises':[],'limitations':['Not a human performance review','Synthetic sound checked as files and selected frequencies, not listened to','No learner study or ergonomic assessment']}


def number(p):
    step=p.findtext('step');octave=int(p.findtext('octave'));alter=int(p.findtext('alter') or 0)
    return 12*(octave+1)+{'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[step]+alter


for e in data:
    id=e['id'];xml=ET.parse(ASSETS/f'{id}.musicxml');measures=xml.findall('.//part/measure')
    assert len(measures)==len(e['rh'])
    divisions=int(measures[0].findtext('attributes/divisions'));expected=[];open_ties={};total=0
    for mi,m in enumerate(measures):
        staff_time={1:0,2:0};last_start={1:0,2:0}
        accidental_state={}
        signature={x:0 for x in 'ABCDEFG'}
        for step in 'FCGDAEB'[:max(0,e['key'])]:signature[step]=1
        for step in 'BEADGCF'[:max(0,-e['key'])]:signature[step]=-1
        for node in m.findall('note'):
            staff=int(node.findtext('staff'));dur=int(node.findtext('duration'));is_chord=node.find('chord') is not None
            start=last_start[staff] if is_chord else staff_time[staff]
            if not is_chord:last_start[staff]=start;staff_time[staff]+=dur
            typ=node.findtext('type');base={'whole':4,'half':2,'quarter':1,'eighth':.5,'16th':.25}[typ]
            if node.find('dot') is not None:base*=1.5
            assert math.isclose(dur/divisions,base),(id,'duration/type',mi)
            if node.find('rest') is not None:continue
            pitch=number(node.find('pitch'));at=(total+start)/divisions
            spelled=node.find('pitch');step=spelled.findtext('step');octave=int(spelled.findtext('octave'));alter=int(spelled.findtext('alter') or 0)
            state_key=(staff,step,octave);prior=accidental_state.get(state_key,signature[step])
            if alter!=prior:
                assert node.findtext('accidental')=={-1:'flat',0:'natural',1:'sharp'}[alter],(id,mi,'Missing printed accidental',step,alter)
            accidental_state[state_key]=alter
            assert 40<=pitch<=100,(id,pitch)
            tie=node.find('tie');key=(staff,pitch)
            if tie is not None and tie.get('type')=='stop':
                item=expected[open_ties.pop(key)]
                assert math.isclose(item[0]+item[1],at)
                item[1]+=dur/divisions
            else:
                expected.append([at,dur/divisions,pitch,staff-1])
                if tie is not None:open_ties[key]=len(expected)-1
        bar=e['meter'][0]*4/e['meter'][1]
        assert all(math.isclose(v/divisions,bar) for v in staff_time.values()),(id,mi,staff_time)
        total+=round(bar*divisions)
    assert not open_ties
    if id=='E16':assert len(xml.findall('.//note[staff="2"]/beam'))==32
    if id=='E19':
        beams=[x.text for x in xml.findall('.//note[staff="1"]/beam')]
        assert beams==['begin','continue','end']*6
    actual=[]
    midi=mido.MidiFile(ASSETS/f'{id}.mid');end_tick=0
    pedal_events=[]
    for track in midi.tracks:
        tick=0;active={}
        for msg in track:
            tick+=msg.time
            if msg.type=='control_change' and msg.control==64:pedal_events.append((msg.channel,tick,msg.value))
            if msg.type=='note_on' and msg.velocity>0:
                key=(msg.channel,msg.note);assert key not in active;active[key]=tick
            if msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0):
                key=(msg.channel,msg.note);start=active.pop(key)
                actual.append([start/midi.ticks_per_beat,(tick-start)/midi.ticks_per_beat,msg.note,msg.channel])
        assert not active;end_tick=max(end_tick,tick)
    assert sorted(expected)==sorted(actual),(id,'XML/MIDI mismatch')
    expected_pedals=[]
    if e['pedal']:
        for channel in (0,1):
            for bi in range(len(measures)):
                expected_pedals.extend([(channel,round((bi*bar+.1)*480),127),(channel,round(((bi+1)*bar-.1)*480),0)])
    assert sorted(pedal_events)==sorted(expected_pedals),(id,'pedal mismatch')
    assert math.isclose(end_tick/midi.ticks_per_beat,total/divisions)
    assert sorted(actual)==sorted([[x['start'],x['duration'],x['pitch'],x['channel']] for x in e['events']])
    for suffix,channel in [('-rh',0),('-lh',1)]:
        part=mido.MidiFile(ASSETS/f'{id}{suffix}.mid')
        assert sum(msg.type=='note_on' and msg.velocity>0 for t in part.tracks for msg in t)==sum(x[3]==channel for x in actual)
    for page in e['score_pages']:
        svg=ET.parse(ASSETS/page).getroot();assert svg.tag.endswith('svg')
        assert int(float(svg.get('width').replace('px','')))>0
    with wave.open(str(ASSETS/f'{id}.wav')) as wav:
        assert (wav.getnchannels(),wav.getsampwidth(),wav.getframerate())==(1,2,16000)
        samples=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2')/32768
        duration=len(samples)/16000
        expected_seconds=(len(e['rh'])+1)*bar*60/e['bpm']+.45
        assert abs(duration-expected_seconds)<1/16000+.0001
        assert .01<float(np.max(np.abs(samples)))<.96
    report['exercises'].append({'id':id,'bars':len(measures),'sounding_note_events':len(actual),'score_pages':len(e['score_pages']),'seconds':round(duration,3),'xml_midi_events_match':True,'audio_format_and_peak_checked':True})

# Check known independent pitch targets in monophonic examples, using audio FFT.
frequency_checks=[]
for id,start,target in [('E01',4.12,261.625565),('E09',10.12,739.988845),('E10',7.12,466.163762)]:
    with wave.open(str(ASSETS/f'{id}.wav')) as w:s=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float);rate=w.getframerate()
    sample=s[int(start*rate):int((start+.36)*rate)];spec=np.abs(np.fft.rfft(sample*np.hanning(len(sample))));freq=np.fft.rfftfreq(len(sample),1/rate)
    measured=float(freq[int(np.argmax(spec))]);assert abs(measured-target)<4,(id,measured,target)
    frequency_checks.append({'id':id,'target_hz':target,'measured_hz':round(measured,3),'tolerance_hz':4})
report['selected_audio_frequency_checks']=frequency_checks

soup=BeautifulSoup((BOOK/'index.html').read_text(encoding='utf-8'),'html.parser');ids={x['id'] for x in soup.select('[id]')}
assert len(soup.select('.chapter'))==18
assert {x['id'] for x in soup.select('figure.example')}=={x['id'] for x in data}
broken=[]
for x in soup.select('[src],a[href]'):
    url=x.get('src') or x.get('href');parts=urlsplit(url)
    if parts.scheme or parts.netloc:continue
    if not parts.path:
        if parts.fragment and unquote(parts.fragment) not in ids:broken.append(url)
    elif not (BOOK/unquote(parts.path)).is_file():broken.append(url)
assert not broken,broken
assert '[[EX:' not in soup.get_text()
all_text='\n'.join(p.read_text(encoding='utf-8') for p in (BOOK/'chapters').glob('*.md'))
report['chapters']=18;report['numbered_chapters']=16;report['chinese_characters']=len(re.findall(r'[\u4e00-\u9fff]',all_text));report['local_links']='passed'
report['asset_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ASSETS.iterdir()) if p.is_file()}
report['status']='passed'
(ROOT/'research/book-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','numbered_chapters','chapters','chinese_characters','local_links']},ensure_ascii=False))
