#!/usr/bin/env python3
"""Archive five linked PULSE lesson pages and their official PDF attachments."""
import concurrent.futures
import json
from urllib.parse import urljoin,urlsplit
import requests
from bs4 import BeautifulSoup
from download_sources import ROOT,LIB,fetch

def lesson(n):
    url=f'https://pulse.berklee.edu/?id=4&lesson={n}'
    r=requests.get(url,timeout=45);r.raise_for_status()
    path=LIB/'raw'/f'pulse-lesson-{n}.html';path.write_bytes(r.content)
    s=BeautifulSoup(r.content,'html.parser')
    links={urljoin(url,a['href']) for a in s.select('a[href]') if '.pdf' in a['href'].lower()}
    (LIB/'text'/f'pulse-lesson-{n}.txt').write_text(s.get_text('\n',strip=True))
    return dict(id=n,url=url,pdf_links=sorted(x for x in links if urlsplit(x).hostname=='pulse.berklee.edu'))

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:lessons=list(pool.map(lesson,[23,25,26,27,28]))
    urls=sorted({u for x in lessons for u in x['pdf_links']})
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(fetch,[(f'S5-EXTRA-{i+1}',f'pulse-extra-{i+1:02d}.pdf',u) for i,u in enumerate(urls)]))
    (ROOT/'research/pulse-lesson-manifest.json').write_text(json.dumps({'lessons':lessons,'downloads':records},ensure_ascii=False,indent=2)+'\n')
