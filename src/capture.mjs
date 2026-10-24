import {validateRoute,visibleEvidence} from './browser-policy.mjs';
import {installDemo,enterLive,roomId} from './demo-fixtures.mjs';
import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
const input=JSON.parse(await new Promise(resolve=>{let s='';process.stdin.on('data',c=>s+=c);process.stdin.on('end',()=>resolve(s));}));
const origin='https://smartmeet.org';
validateRoute(input.feature);
const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
try {
 const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 // No persisted sessions, cameras/microphones, arbitrary model navigation, meeting creation or provider calls.
 await context.route('**/*', async route=>{
  const request=route.request(); const u=new URL(request.url());
  if(request.resourceType()==='document' && u.origin!==origin) return route.abort();
  if(!['GET','HEAD','OPTIONS'].includes(request.method()) && !(u.origin===origin && u.pathname==='/api/auth/login')) return route.abort();
  return route.continue();
 });
 if(input.feature.demo) await installDemo(context,input.feature.demo);
 if(input.feature.auth){
  const res=await context.request.post(origin+'/api/auth/login',{data:{email:process.env.DEMO_EMAIL,password:process.env.DEMO_PASSWORD}});
  if(!res.ok()) throw Error('Demo login failed');const auth=await res.json();
  if(auth.user.email!==process.env.DEMO_EMAIL || auth.user.name!=='SmartMeet Marketing Demo') throw Error('Wrong demo identity');
  await context.addInitScript(({token,user})=>{localStorage.setItem('token',token);localStorage.setItem('user',JSON.stringify(user));},auth);
 }
 const page=await context.newPage();await page.goto(origin+input.feature.path,{waitUntil:'networkidle',timeout:45000});
 if(new URL(page.url()).pathname!==input.feature.path && !(input.feature.demo && ['/abc-defg-hjk','/abc-defg-hjk/summary'].includes(new URL(page.url()).pathname))) throw Error('Unexpected route / auth redirect');
 if(input.feature.demo==='live') await enterLive(page);
 for(const step of input.feature.steps||[]) {
  if(step.action==='click') await page.getByRole(step.role||'button',{name:step.name,exact:true}).click();
  else if(step.action==='scroll') await page.getByText(step.name,{exact:false}).first().scrollIntoViewIfNeeded();
  else throw Error('Unknown demo action');
 }
 await page.getByText(input.feature.anchor,{exact:false}).first().waitFor({timeout:15000});

 // Hide editable PII, links, account identifiers and notification text; never save storage state or request logs.
 if(input.feature.demo) await page.evaluate(()=>{const tag=document.createElement('div');tag.textContent='SMARTMEET DEMO · Synthetic meeting data';tag.style.cssText='position:fixed;right:12px;top:6px;z-index:2147483647;background:#0f172a;color:white;padding:7px 12px;border-radius:8px;font:12px sans-serif';document.body.append(tag);});
 await page.addStyleTag({content:'input[type=email],input[type=password],input[type=tel], input[readonly], [data-private], [role=alert] {visibility:hidden!important}'});
 await page.evaluate(()=>{for(const el of document.querySelectorAll('a')){if(/token=|joinToken|\/meeting\//i.test(el.href))el.style.visibility='hidden';}});
 const observed=await page.evaluate(visibleEvidence);
 for(const term of input.feature.evidence_terms||[]) if(!observed.toLowerCase().includes(term.toLowerCase()))throw Error('Missing feature evidence: '+term);
 await mkdir(input.out,{recursive:true,mode:0o700});
 await page.screenshot({path:input.out+'/screenshot.png',fullPage:false});
 const safe=observed.replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi,'[demo email]').replace(/https?:\/\/\S+/g,'[link]');
 await writeFile(input.out+'/evidence.json',JSON.stringify({feature_id:input.feature.id,route:input.feature.path,captured_at:new Date().toISOString(),observed:safe,kind:input.feature.demo?'actual deployed UI with synthetic demo fixtures; not a real meeting or outcome':'actual UI screenshot; no meeting started'},null,2));
} finally {await browser.close();}
