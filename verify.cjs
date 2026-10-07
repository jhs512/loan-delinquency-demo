const fs=require('fs'),assert=require('assert');const {predict}=require('./docs/inference.js');
const m=JSON.parse(fs.readFileSync('docs/model.json')),f=JSON.parse(fs.readFileSync('parity-fixtures.json'));
const errors=f.X.map((x,i)=>Math.abs(predict(m,x)-f.expected[i]));assert(Math.max(...errors)<1e-10);console.log(JSON.stringify({cases:errors.length,max_absolute_error:Math.max(...errors),passed:true}));
