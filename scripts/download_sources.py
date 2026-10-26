#!/usr/bin/env python3
"""Download public official sources locally. Never publish the cache by default."""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import sys
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIB = ROOT / '.local-library'
SOURCES = [
 ('S1','berklee-theory.pdf','https://assets.online.berklee.edu/handbooks/berklee-online-music-theory-harmony-and-ear-training-handbook.pdf'),
 ('S2','berklee-piano.pdf','https://assets.online.berklee.edu/handbooks/berklee-online-piano-handbook.pdf'),
 ('S4','berklee-sound-design.pdf','https://assets.online.berklee.edu/handbooks/berklee-online-electronic-music-production-and-sound-design-handbook.pdf'),
 ('S3','omt2-viva.html','https://viva.pressbooks.pub/openmusictheory/'),
 ('S3-MIRROR','omt2-nebraska.html','https://pressbooks.nebraska.edu/openmusictheory/'),
 ('S3-CATALOG','omt2-catalog.html','https://open.umn.edu/opentextbooks/textbooks/1254'),
 ('S5','pulse-practice.html','https://pulse.berklee.edu/casio?id=5&lang=en'),
 ('HUB','berklee-handbooks.html','https://online.berklee.edu/handbooks'),
 ('C1','piano-chords-101.html','https://online.berklee.edu/courses/piano-chords-101'),
 ('C2','pop-rock-keyboard.html','https://online.berklee.edu/courses/pop-rock-keyboard'),
 ('C3','berklee-keyboard-method.html','https://online.berklee.edu/courses/berklee-keyboard-method'),
 ('C4','arranging-1.html','https://online.berklee.edu/courses/arranging-1-rhythm-section'),
 ('C5','live-performance.html','https://online.berklee.edu/courses/keyboards-for-live-performance-techniques-and-technology'),
]

def fetch(entry):
    sid, name, url = entry
    path = LIB / 'raw' / name
    record = dict(id=sid,url=url,file=str(path.relative_to(ROOT)),retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        r = requests.get(url, timeout=(20,180),headers={'User-Agent':'Mozilla/5.0 (personal educational source audit)'})
        record.update(status=r.status_code,final_url=r.url,content_type=r.headers.get('Content-Type'))
        if r.ok:
            if name.endswith('.pdf') and not r.content.startswith(b'%PDF'):
                raise ValueError('Response is not a PDF')
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(r.content)
            record.update(bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest())
        else:
            record['error']=r.reason
    except Exception as e:
        record['error']=str(e)
    print(json.dumps(record,ensure_ascii=False),flush=True)
    return record

if __name__ == '__main__':
    LIB.mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(fetch,SOURCES))
    (ROOT/'research'/'download-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
