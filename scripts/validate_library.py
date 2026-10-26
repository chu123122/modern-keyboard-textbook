#!/usr/bin/env python3
"""Verify saved bytes and known acquisition failures; does not verify musicianship."""
import hashlib
import json
import pathlib
import zipfile
import pymupdf
from download_sources import ROOT,LIB

def main():
    records=[]
    for name in ['download-manifest.json','omt-export-manifest.json','pulse-manifest.json','omt-web-manifest.json','omt-assets-manifest.json','pdf-index.json']:
        p=ROOT/'research'/name
        if p.exists():records+=json.loads(p.read_text())
    p=ROOT/'research/pulse-lesson-manifest.json'
    if p.exists():records+=json.loads(p.read_text())['downloads']
    p=ROOT/'research/workbook-manifest.json'
    if p.exists():records.append(json.loads(p.read_text()))
    errors=[];verified=set();known=[]
    for x in records:
        if x.get('error'):known.append({'url':x.get('url'),'error':x['error']});continue
        if not x.get('file') or not x.get('sha256'):continue
        path=ROOT/x['file']
        if not path.exists():errors.append('missing: '+x['file']);continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=x['sha256']:errors.append('hash mismatch: '+x['file'])
        else:verified.add(x['file'])
    pdfs=[]
    for p in (LIB/'raw').glob('*.pdf'):
        try:
            d=pymupdf.open(p);pdfs.append({'file':p.name,'pages':len(d)})
            if len(d)==0:errors.append('empty PDF: '+p.name)
        except Exception as e:errors.append('invalid PDF: '+p.name+': '+str(e))
    github=json.loads((ROOT/'research/github-manifest.json').read_text())
    for x in github:
        path=LIB/'github'/(x['repository'].replace('/','--')+'.zip')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=x['archive_sha256']:errors.append('repository archive hash mismatch: '+x['repository'])
        with zipfile.ZipFile(path) as z:
            if z.testzip():errors.append('repository archive corrupt: '+x['repository'])
    ledger=json.loads((ROOT/'research/reading-ledger.json').read_text())
    for x in ledger['omt_reading']:
        if not (ROOT/x['text_file']).exists():errors.append('missing reading copy: '+x['text_file'])
    report={'date':'2026-10-26','scope':'file integrity, parseability and reading-copy presence; no audio, playing, pedagogy or full semantic verification','verified_unique_files':len(verified),'pdf_files':len(pdfs),'pdf_pages':sum(x['pages'] for x in pdfs),'github_archives':len(github),'omt_reading_entries':len(ledger['omt_reading']),'known_acquisition_failures':known,'integrity_errors':errors,'integrity_status':'passed' if not errors else 'failed'}
    (ROOT/'research/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
