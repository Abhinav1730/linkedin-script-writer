import {test} from 'node:test';import assert from 'node:assert/strict';
import {chromium} from 'playwright';import {validateRoute,visibleEvidence,demoRoomId} from '../src/browser-policy.mjs';
test('only approved public, own-account or synthetic routes',()=>{
 assert(validateRoute({path:'/dashboard'}));assert(validateRoute({path:'/meeting/'+demoRoomId,demo:'live'}));
 for(const f of [{path:'/admin'},{path:'/meeting/customer-room',demo:'live'},{path:'https://evil.example'},{path:'/meeting/'+demoRoomId},{path:'/dashboard',demo:'evil'}])assert.throws(()=>validateRoute(f));
});
test('private, hidden and instruction-bearing content excluded from evidence',async()=>{
 const browser=await chromium.launch({headless:true});try{
  const page=await browser.newPage();await page.setContent('<main>Meeting setup <p>demo@smartmeet.invalid</p><p>https://example.test/token=secret</p><div data-private>PRIVATE SECRET</div><div role="alert">ALERT SECRET</div><p hidden>HIDDEN SECRET</p><p style="visibility:hidden">CSS SECRET</p><input value="PASSWORD SECRET"><textarea>TEXT SECRET</textarea><script type="application/json">SCRIPT SECRET</script></main>');
  const evidence=await page.evaluate(visibleEvidence);assert(evidence.includes('Meeting setup'));assert(!evidence.includes('SECRET'));assert(!evidence.includes('@'));assert(!evidence.includes('https://'));
 }finally{await browser.close();}
});
