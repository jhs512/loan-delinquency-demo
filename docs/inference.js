(function(root){
function sigmoid(x){return 1/(1+Math.exp(-x));}
function leaf(t,x){let i=0;while(t.children_left[i]!==-1){i=x[t.feature[i]]<=t.threshold[i]?t.children_left[i]:t.children_right[i];}return t.value[i][0];}
function predict(m,x){if(m.kind==='logistic')return sigmoid(m.intercept+x.reduce((s,v,i)=>s+(v-m.mean[i])/m.scale[i]*m.coef[i],0));
if(m.kind==='forest')return m.trees.reduce((s,t)=>{let v=leaf(t,x);return s+v[1]/(v[0]+v[1]);},0)/m.trees.length;
return sigmoid(m.intercept+m.learning_rate*m.trees.reduce((s,t)=>s+leaf(t,x)[0],0));}
root.predict=predict;if(typeof module!=='undefined')module.exports={predict};
})(typeof window!=='undefined'?window:globalThis);
