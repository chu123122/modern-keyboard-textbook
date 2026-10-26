#!/usr/bin/env python3
"""Archive only OMT2's linked table of contents and PULSE's official PDFs."""
import concurrent.futures
import hashlib
import json
import pathlib
import time
from urllib.parse import urljoin,urldefrag,urlsplit
import requests
from bs4 import BeautifulSoup
from download_sources import ROOT,LIB,fetch

def archive(item):
    number,title,url=item
    slug=urlsplit(url).path.strip('/').split('/')[-1]
    raw=LIB/'omt-web'/f'{number:03d}-{slug}.html'
    record=dict(index=number,title=title,url=url,file=str(raw.relative_to(ROOT)))
    try:
        r=requests.get(url,timeout=(20,90),headers={'User-Agent':'Mozilla/5.0 (personal educational source audit)'});r.raise_for_status()
        raw.parent.mkdir(parents=True,exist_ok=True);raw.write_bytes(r.content)
        soup=BeautifulSoup(r.content,'html.parser')
        body=soup.select_one('.chapter') or soup.select_one('.front-matter') or soup.select_one('.back-matter') or soup.select_one('.entry-content') or soup.select_one('main')
        if body is None:raise ValueError('No chapter body')
        for el in body.select('script,style,nav,.navigation'):el.decompose()
        content=body.get_text('\n',strip=True)
        text_path=LIB/'text/omt-web'/f'{number:03d}-{slug}.txt';text_path.parent.mkdir(parents=True,exist_ok=True)
        text_path.write_text(f'{title}\nURL: {url}\n\n'+content)
        record.update(status=r.status_code,bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest(),characters=len(content),text_file=str(text_path.relative_to(ROOT)),images=[urljoin(url,x['src']) for x in body.select('img[src]')],media=[x.get('src') for x in body.select('iframe[src],audio[src],source[src]')],download_links=[urljoin(url,a['href']) for a in body.select('a[href]') if any(t in a['href'].lower() for t in ['.pdf','.mxl','.musicxml','.mp3','.mid','.zip'])])
    except Exception as e:record.update(error=str(e))
    print(number,title,record.get('status',record.get('error')),flush=True)
    return record

if __name__=='__main__':
    s=BeautifulSoup((LIB/'raw/omt2-viva.html').read_text(),'html.parser')
    items=[];seen=set()
    for a in s.select('a[href]'):
        url=urldefrag(a['href'])[0]
        if not url.startswith('https://viva.pressbooks.pub/openmusictheory/'):continue
        if not any(t in url for t in ['/chapter/','/front-matter/','/back-matter/']):continue
        if url in seen:continue
        seen.add(url);items.append((len(items)+1,a.get_text(' ',strip=True),url))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(archive,items))
    (ROOT/'research/omt-web-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    s=BeautifulSoup((LIB/'raw/pulse-practice.html').read_text(),'html.parser');pdfs=[]
    for a in s.select('a[href]'):
        if '.pdf' in a['href'].lower():
            url=urljoin('https://pulse.berklee.edu/casio?id=5&lang=en',a['href'])
            pdfs.append(fetch((f'S5-PDF-{len(pdfs)+1}',f'pulse-{len(pdfs)+1}.pdf',url)))
    (ROOT/'research/pulse-manifest.json').write_text(json.dumps(pdfs,ensure_ascii=False,indent=2)+'\n')
