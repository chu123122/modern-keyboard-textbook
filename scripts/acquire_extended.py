#!/usr/bin/env python3
"""Archive OMT2 and pinned public tool repositories. No downloaded code is run."""
import concurrent.futures
import hashlib
import json
import pathlib
import zipfile
import io
import requests
from bs4 import BeautifulSoup
from download_sources import ROOT, LIB, fetch

REPOS=['xx-hub/craft-your-textbook','dmccreary/ibook-skills','anthropics/skills']

def repository(repo):
    api='https://api.github.com/repos/'+repo
    meta=requests.get(api,timeout=45).json()
    branch=meta['default_branch']
    sha=requests.get(api+'/commits/'+branch,timeout=45).json()['sha']
    url=f'https://codeload.github.com/{repo}/zip/{sha}'
    r=requests.get(url,timeout=(20,240));r.raise_for_status()
    name=repo.replace('/','--')
    target=LIB/'github'/name
    target.mkdir(parents=True,exist_ok=True)
    (LIB/'github'/f'{name}.zip').write_bytes(r.content)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for item in z.infolist():
            rel=pathlib.PurePosixPath(item.filename)
            if '..' in rel.parts or rel.is_absolute():raise ValueError('Unsafe archive path')
            if item.is_dir():continue
            # All files are archived. Extract readable workflow documents and scripts only.
            if rel.suffix.lower() not in ['.md','.txt','.py','.json','.yaml','.yml','.csv','.sh','.mjs','.js'] and rel.name not in ['LICENSE','LICENSE.txt']:continue
            out=target.joinpath(*rel.parts[1:]);out.parent.mkdir(parents=True,exist_ok=True)
            out.write_bytes(z.read(item))
    record=dict(repository=repo,url=meta['html_url'],commit=sha,branch=branch,license=meta.get('license'),archive_url=url,archive_bytes=len(r.content),archive_sha256=hashlib.sha256(r.content).hexdigest(),local_directory=str(target.relative_to(ROOT)))
    print(json.dumps(record,ensure_ascii=False),flush=True)
    return record

def omt_exports():
    return [fetch(x) for x in [('S3-PDF','omt2.pdf','https://viva.pressbooks.pub/openmusictheory/open/download?type=pdf'),('S3-XML','omt2.xml','https://viva.pressbooks.pub/openmusictheory/open/download?type=wxr')]]

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(repository,x) for x in REPOS]
        exports=pool.submit(omt_exports)
        records=[f.result() for f in futures]
        (ROOT/'research/github-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        (ROOT/'research/omt-export-manifest.json').write_text(json.dumps(exports.result(),ensure_ascii=False,indent=2)+'\n')
