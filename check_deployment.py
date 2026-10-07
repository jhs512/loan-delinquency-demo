import subprocess,json,urllib.request,urllib.error
p=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,timeout=20)
token=dict(l.split('=',1) for l in p.stdout.splitlines() if '=' in l)['password']
def api(path,data=None):
    req=urllib.request.Request('https://api.github.com/repos/jhs512/loan-delinquency-demo/'+path,data=json.dumps(data).encode() if data else None,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'loan-demo'})
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r) if r.status!=204 else {}
runs=api('actions/runs')['workflow_runs'];print(json.dumps([{'id':r['id'],'status':r['status'],'conclusion':r['conclusion'],'url':r['html_url']} for r in runs[:3]]))
if runs and runs[0]['conclusion']=='failure':
    print(json.dumps(api('actions/runs/'+str(runs[0]['id'])+'/jobs')['jobs']))
