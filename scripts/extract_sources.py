#!/usr/bin/env python3
"""Create local reading copies and public structural indexes, never claim reading."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pymupdf
from download_sources import ROOT, LIB

def clean_html(html):
    soup=BeautifulSoup(html,'html.parser')
    for node in soup.select('script,style,nav,header,footer'):node.decompose()
    return soup.get_text('\n',strip=True),soup

def main():
    texts=LIB/'text';texts.mkdir(parents=True,exist_ok=True)
    pdfs=[]
    for p in (LIB/'raw').glob('*.pdf'):
        d=pymupdf.open(p)
        chunks=[f'\n\n===== PDF PAGE {i+1} =====\n'+page.get_text() for i,page in enumerate(d)]
        (texts/f'{p.stem}.txt').write_text(''.join(chunks))
        pdfs.append(dict(file=str(p.relative_to(ROOT)),pages=len(d),extracted_characters=sum(map(len,chunks)),empty_text_pages=[i+1 for i,page in enumerate(d) if len(page.get_text().strip())<20]))
    (ROOT/'research/pdf-index.json').write_text(json.dumps(pdfs,ensure_ascii=False,indent=2)+'\n')
    for p in (LIB/'raw').glob('*.html'):
        text,_=clean_html(p.read_text());(texts/f'{p.stem}.txt').write_text(text)
    xml=LIB/'raw/omt2.xml'
    if xml.exists():
        ns={'wp':'http://wordpress.org/export/1.2/','content':'http://purl.org/rss/1.0/modules/content/','dc':'http://purl.org/dc/elements/1.1/'}
        tree=ET.parse(xml);chapters=[]
        target=texts/'omt2';target.mkdir(exist_ok=True)
        for item in tree.findall('./channel/item'):
            kind=item.findtext('wp:post_type',default='',namespaces=ns)
            if kind not in ['chapter','front-matter','back-matter','part']:continue
            status=item.findtext('wp:status',default='',namespaces=ns)
            if status != 'publish':
                continue
            body=item.findtext('content:encoded',default='',namespaces=ns)
            title=item.findtext('title','')
            slug=item.findtext('wp:post_name',default='',namespaces=ns)
            text,soup=clean_html(body)
            filename=f'{len(chapters)+1:03d}-{slug}.txt'
            url=item.findtext('link','')
            (target/filename).write_text(f'{title}\nURL: {url}\n\n'+text)
            chapters.append(dict(index=len(chapters)+1,title=title,slug=slug,url=url,kind=kind,status=status,author=item.findtext('dc:creator',default='',namespaces=ns),characters=len(text),file=str((target/filename).relative_to(ROOT)),images=[x.get('src') for x in soup.select('img[src]')],media=[x.get('src') for x in soup.select('iframe[src],audio[src],source[src]')],headings=[x.get_text(' ',strip=True) for x in soup.select('h1,h2,h3')]))
        (ROOT/'research/omt-chapter-index.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2)+'\n')
        print('OMT WXR entries:',len(chapters),'characters:',sum(x['characters'] for x in chapters))
    print(json.dumps(pdfs,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
