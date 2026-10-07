"""Reproducible synthetic benchmark. No real personal data."""
import json, pathlib, subprocess
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss

ROOT=pathlib.Path(__file__).parent
OUT=ROOT/'docs'; OUT.mkdir(exist_ok=True)
SEED=20261007
rng=np.random.default_rng(SEED)
features=['income','balance','rate','remaining','other_payment','tenure','credit','utilization','savings','payment','dti','late30','late6','lastlate','maxdays']
def sigmoid(x): return 1/(1+np.exp(-x))
rows=[]; histories=[]; targets=[]
for i in range(2000):
    income=float(np.clip(rng.lognormal(np.log(350),.45),100,1500))
    remaining=int(rng.integers(12,121)); balance=float(income*rng.uniform(3,24)); rate=float(rng.uniform(3,16))
    r=rate/1200; payment=balance*r/(1-(1+r)**(-remaining))
    other=float(income*rng.uniform(.02,.35)); tenure=float(rng.uniform(0,20)); utilization=float(rng.beta(2,3))
    credit=float(np.clip(900-220*utilization+rng.normal(0,65),350,1000)); savings=float(income*rng.gamma(1.3,1.4)); dti=(payment+other)/income
    history=[]; latent=rng.normal(0,.5)
    base=-4.4+3.6*dti+1.6*utilization+(750-credit)/170-.1*min(tenure,10)-.16*min(savings/income,8)+latent
    for m in range(30):
        p=sigmoid(base+.7*(history[-1]>0 if history else 0)+.3*np.sin(m/5))
        history.append(int(rng.choice([3,10,35,65],p=[.4,.35,.2,.05])) if rng.random()<p else 0)
    credit=float(np.clip(credit-2*sum(d>0 for d in history),350,1000))
    x=[income,balance,rate,remaining,other,tenure,credit,utilization,savings,payment,dti,sum(d>0 for d in history),sum(d>0 for d in history[-6:]),int(history[-1]>0),max(history)]
    p=sigmoid(base+.9*x[13]+.12*x[12]+.004*x[14])
    rows.append(x); histories.append(history); targets.append(int(rng.random()<p))
X=np.array(rows); y=np.array(targets)
idx=np.arange(len(y)); train,rest=train_test_split(idx,test_size=.4,stratify=y,random_state=SEED)
val,test=train_test_split(rest,test_size=.5,stratify=y[rest],random_state=SEED)
candidates=[('logistic',make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=SEED)),{'logisticregression__C':[.01,.1,1,10]}),('forest',RandomForestClassifier(random_state=SEED,n_jobs=2),{'n_estimators':[120],'max_depth':[4,8,None],'min_samples_leaf':[5,15]}),('boosting',GradientBoostingClassifier(random_state=SEED),{'n_estimators':[60,120],'learning_rate':[.03,.1],'max_depth':[1,2]})]
def metrics(a,p): return {'auc':roc_auc_score(a,p),'pr_auc':average_precision_score(a,p),'brier':brier_score_loss(a,p),'log_loss':log_loss(a,p)}
results=[]; models=[]; searches=[]
for name,model,grid in candidates:
    search=GridSearchCV(model,grid,scoring='neg_log_loss',cv=StratifiedKFold(4,shuffle=True,random_state=SEED),n_jobs=2)
    search.fit(X[train],y[train]); best=search.best_estimator_; m=metrics(y[val],best.predict_proba(X[val])[:,1])
    results.append({'model':name,'parameters':search.best_params_,'validation':m}); models.append(best)
    for params,mean,std in zip(search.cv_results_['params'],search.cv_results_['mean_test_score'],search.cv_results_['std_test_score']): searches.append({'model':name,'parameters':params,'cv_log_loss':-mean,'cv_std':std})
winner=int(np.argmin([r['validation']['log_loss'] for r in results])); model=models[winner]
def tree(t):
    return {'children_left':t.children_left.tolist(),'children_right':t.children_right.tolist(),'feature':t.feature.tolist(),'threshold':t.threshold.tolist(),'value':t.value.tolist()}
export={'kind':results[winner]['model'],'features':features}
if export['kind']=='logistic':
    s=model[0]; l=model[1]; export.update(mean=s.mean_.tolist(),scale=s.scale_.tolist(),coef=l.coef_[0].tolist(),intercept=float(l.intercept_[0]))
elif export['kind']=='forest': export['trees']=[tree(t.tree_) for t in model.estimators_]
else:
    export.update(trees=[tree(t[0].tree_) for t in model.estimators_],learning_rate=model.learning_rate,intercept=float(np.log(model.init_.class_prior_[1]/model.init_.class_prior_[0])))
(OUT/'model.json').write_text(json.dumps(export),encoding='utf-8')
report={'seed':SEED,'selected':export['kind'],'selection':'training 4-fold CV log loss; validation log loss chooses family; frozen model evaluated once on test','split':{'train':len(train),'validation':len(val),'test':len(test)},'prevalence':float(y.mean()),'test_prevalence':float(y[test].mean()),'results':results,'test':metrics(y[test],model.predict_proba(X[test])[:,1]),'search':searches}
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
frame=pd.DataFrame(X,columns=features); frame.insert(0,'borrower_id',[f'SYN-{i+1:04}' for i in idx]); frame['history_days']=list(map(json.dumps,histories)); frame['next_month_late']=y; frame['split']=['train' if i in train else 'validation' if i in val else 'test' for i in idx]; frame.to_csv(ROOT/'synthetic.csv',index=False)
(OUT/'samples.json').write_text(json.dumps([{'x':rows[i],'history':histories[i]} for i in range(200)]),encoding='utf-8')
(ROOT/'parity-fixtures.json').write_text(json.dumps({'X':X[test].tolist(),'expected':model.predict_proba(X[test])[:,1].tolist()}),encoding='utf-8')
print(json.dumps({'selected':export['kind'],'test':report['test'],'candidates':len(searches)},indent=2))
