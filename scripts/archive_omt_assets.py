#!/usr/bin/env python3
"""Cache official OMT assets for the selected, actually read chapters."""
import concurrent.futures
import hashlib
import json
from urllib.parse import urljoin,urlsplit,unquote
import requests
from bs4 import BeautifulSoup
from download_sources import ROOT,LIB

SELECTED=[1,11,12,13,15,16,17,18,19,20,21,22,24,25,26,27,28,44,45,47,58,72,85,86,87,88,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,143]

def acquire(pair):
    url,chapters=pair
    suffix=path_suffix=urlsplit(url).path.split('/')[-1]
    name=hashlib.sha256(url.encode()).hexdigest()[:12]+'-'+unquote(suffix)
    path=LIB/'omt-assets'/name
    record=dict(url=url,chapter_indexes=sorted(chapters),file=str(path.relative_to(ROOT)))
    try:
        r=requests.get(url,timeout=(20,90),headers={'User-Agent':'Mozilla/5.0 (personal educational source audit)'});r.raise_for_status()
        if 'text/html' in r.headers.get('Content-Type','') and not path.suffix.lower() in ['.html','.htm']:
            raise ValueError('Unexpected HTML response for asset')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(r.content)
        record.update(status=r.status_code,bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest(),content_type=r.headers.get('Content-Type'))
    except Exception as e:record.update(error=str(e))
    return record

if __name__=='__main__':
    manifests=json.loads((ROOT/'research/omt-web-manifest.json').read_text());urls={}
    for x in manifests:
        if x['index'] not in SELECTED or x.get('status')!=200:continue
        soup=BeautifulSoup((ROOT/x['file']).read_text(),'html.parser')
        body=soup.select_one('.chapter') or soup.select_one('.front-matter')
        for node in body.select('a[href],img[src],source[src],audio[src]'):
            u=urljoin(x['url'],node.get('href') or node.get('src'))
            parsed=urlsplit(u)
            if parsed.hostname!='viva.pressbooks.pub' or '/uploads/' not in parsed.path:continue
            if not parsed.path.lower().endswith(('.pdf','.docx','.mscz','.mscx','.mxl','.musicxml','.mid','.mp3','.png','.jpg','.jpeg','.svg','.webp')):continue
            urls.setdefault(u,set()).add(x['index'])
    print('Official assets to retrieve:',len(urls),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records=list(pool.map(acquire,urls.items()))
    (ROOT/'research/omt-assets-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    print('OK:',sum(x.get('status')==200 for x in records),'Failed:',sum('error' in x for x in records),flush=True)
