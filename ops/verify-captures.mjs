import {readFile,mkdir,writeFile} from 'node:fs/promises';import {spawnSync} from 'node:child_process';
const root=process.env.AGENT_STATE_DIR||'/var/lib/smartmeet-marketing';await mkdir(root,{recursive:true});const results=[];
for(const feature of JSON.parse(await readFile(new URL('../config/features.json',import.meta.url),'utf8')).filter(f=>f.enabled)){
 const r=spawnSync('node',['src/capture.mjs'],{input:JSON.stringify({feature,out:root+'/verification/'+feature.id}),encoding:'utf8',timeout:90000});
 const result={feature:feature.id,passed:r.status===0,error:r.stderr.slice(-600)};results.push(result);console.log(feature.id,result.passed?'PASS':'FAIL');
}
await writeFile(root+'/capture-verification.json',JSON.stringify(results,null,2));if(results.some(r=>!r.passed))process.exitCode=1;
