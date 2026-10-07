"""Use existing Git credential securely; never print credential material."""
import subprocess,json,urllib.request,urllib.error
from pathlib import Path
def api(method,path,data=None,token=None):
    request=urllib.request.Request('https://api.github.com'+path,data=json.dumps(data).encode() if data else None,method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'loan-demo','Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=20) as r:return json.load(r)
try:
    p=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,timeout=20)
    values=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
    token=values.get('password')
    if not token: raise RuntimeError('No existing GitHub HTTPS credential available')
    me=api('GET','/user',token=token)['login']; name='loan-delinquency-demo'
    try:repo=api('GET',f'/repos/{me}/{name}',token=token)
    except urllib.error.HTTPError as e:
        if e.code!=404:raise
        repo=api('POST','/user/repos',{'name':name,'description':'Synthetic next-month loan delinquency probability demo','private':False},token)
    if repo['size']>0: raise RuntimeError('Target repository already has content; refusing to overwrite')
    subprocess.run(['git','remote','add','origin',repo['clone_url']],check=True)
    subprocess.run(['git','push','-u','origin','main'],check=True,timeout=120)
    try:pages=api('POST',f'/repos/{me}/{name}/pages',{'build_type':'workflow'},token)
    except urllib.error.HTTPError as e:
        if e.code not in (409,422):raise
        pages=api('GET',f'/repos/{me}/{name}/pages',token=token)
    print(json.dumps({'repository':repo['html_url'],'pages':pages.get('html_url'),'status':'pushed; Pages enabled'}))
except Exception as e:
    print(json.dumps({'status':'blocked','reason':str(e) if not isinstance(e,urllib.error.HTTPError) else f'GitHub API HTTP {e.code}'}))
