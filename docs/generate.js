// Fresh synthetic profiles, following train.py distribution assumptions.
(function(){
const u=()=>Math.max(Number.EPSILON,Math.random());
const normal=()=>Math.sqrt(-2*Math.log(u()))*Math.cos(2*Math.PI*u());
const clip=(x,a,b)=>Math.min(b,Math.max(a,x));
function gamma(a){if(a<1)return gamma(a+1)*Math.pow(u(),1/a);let d=a-1/3,c=1/Math.sqrt(9*d);for(;;){let z=normal(),v=Math.pow(1+c*z,3);if(v<=0)continue;let q=u();if(q<1-.0331*z**4||Math.log(q)<.5*z*z+d*(1-v+Math.log(v)))return d*v;}}
window.generateCustomer=function(){
let income=clip(Math.exp(Math.log(350)+.45*normal()),100,1500),remaining=12+Math.floor(Math.random()*109),balance=income*(3+21*Math.random()),rate=3+13*Math.random(),r=rate/1200,payment=balance*r/(1-(1+r)**(-remaining)),other=income*(.02+.33*Math.random()),tenure=20*Math.random(),a=gamma(2),b=gamma(3),util=a/(a+b),credit=clip(900-220*util+65*normal(),350,1000),savings=income*gamma(1.3)*1.4,dti=(payment+other)/income;
let base=-4.4+3.6*dti+1.6*util+(750-credit)/170-.1*Math.min(tenure,10)-.16*Math.min(savings/income,8)+.5*normal(),history=[];
for(let m=0;m<30;m++){let p=1/(1+Math.exp(-(base+.7*(m&&history[m-1]>0?1:0)+.3*Math.sin(m/5)))),q=Math.random();history.push(Math.random()<p?(q<.4?3:q<.75?10:q<.95?35:65):0);}
credit=clip(credit-2*history.filter(d=>d>0).length,350,1000);
return {x:[income,balance,rate,remaining,other,tenure,credit,util,savings],history};};
})();
