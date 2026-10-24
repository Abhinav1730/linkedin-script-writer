// Synthetic data rendered by SmartMeet's actual deployed frontend. No customer or provider data.
export const roomId='sm_00000000-0000-4000-8000-000000000051';
export const room={roomId,title:'Demo: customer launch planning',agenda:'Agree on the launch checklist.',mode:'instant',role:'host',archiveAccess:true,organizerAccess:true,summaryRecipientConfigured:true,policyVersion:2,sessionStatus:'active',bookingStatus:'confirmed',mediaProvider:'livekit',avatarStatus:'disabled',voiceStatus:'disabled',humanCapacity:250,meetingCode:'abc-defg-hjk',shareUrl:'https://smartmeet.org/abc-defg-hjk',revision:1,resultStatus:'ready',captureStatus:'finished',summaryStatus:'ready',summaryEmailStatus:'sent',durationMinutes:30,startsAt:'2026-10-24T09:00:00.000Z',timezone:'Asia/Kolkata'};
const excerpt={turnId:'speech-1',speaker:'Alex (Demo)',text:'Prepare the launch checklist.',evidenceIds:['speech-1']};
export const results={status:'ready',captureStatus:'finished',summaryStatus:'ready',summaryEmailStatus:'sent',transcript:[{id:'speech-1',role:'user',participant_name:'Alex (Demo)',seconds_from_start:75,content:'I will prepare the launch checklist before our next meeting.'}],speakers:[{id:'p1',name:'Alex (Demo)',kind:'human',turnCount:1,verified:true}],coverage:{unidentifiedTurns:0,unverifiedNamedTurns:0,attendeesWithoutSpeech:0},screenCoverage:{analysedFrames:1,failedFrames:0,skippedFrames:0,pendingFrames:0,limitReached:false,captureComplete:true},screenInsights:[{id:'screen-1',presenterId:'p1',presenter:'Alex (Demo)',trackId:'demo-screen',timestamp:1000,seconds_from_start:60,observations:['A launch checklist is shown.'],uncertainties:[]}],summary:{schemaVersion:2,mode:'ai-synthesized',overview:'The demo team reviewed the launch checklist and agreed on the next preparation step.',overviewEvidenceIds:['speech-1'],notice:'Synthetic demo data, not a real customer meeting.',counts:{humanSpeakers:1,humanTurns:1},takeaways:[{text:'Prepare the launch checklist.',evidenceIds:['speech-1']}],screenHighlights:[{text:'The shared slide showed a launch checklist.',evidenceIds:['screen-1']}],discussion:[{topic:'Launch preparation',text:'Alex committed to preparing the launch checklist.',evidenceIds:['speech-1']}],highlights:[excerpt],decisions:[],actions:[{...excerpt,text:'Prepare the launch checklist.',owner:'Alex (Demo)',deadline:'before our next meeting'}],report:[{heading:'Launch preparation',text:'The team reviewed the checklist and agreed on preparation for the next meeting.',evidenceIds:['speech-1']}],openQuestions:[],contributions:[{id:'p1',name:'Alex (Demo)',kind:'human',turnCount:1,verified:true,excerpts:[excerpt]}]}};
const mediaMock=`export function createLiveKitCall(){const events={};let name='Alex (Demo)';const call={on(e,f){(events[e]??=[]).push(f);return call;},participants(){return{local:{session_id:'demo',user_id:'demo',user_name:name,local:true,tracks:{audio:{state:'off'},video:{state:'off'},screenVideo:{state:'off'},screenAudio:{state:'off'}}}};},async join(o){name=o.userName;for(const f of events['joined-meeting']||[])f({});},async leave(){},async destroy(){},getActiveSpeaker(){return{};},setLocalAudio(){},setLocalVideo(){},setVisibleParticipants(){},setBackground(){},localScreenVideo(){return false;},setUserName(){},startScreenShare(){},stopScreenShare(){},sendAppMessage(){},updateToken(){}};return call;}`;
export async function installDemo(context,kind){
 await context.addInitScript(id=>sessionStorage.setItem('smartmeet.room.'+id,'synthetic-demo-only'),roomId);
 await context.route(/\/assets\/livekitCall-[^/]+\.js/,r=>r.fulfill({contentType:'application/javascript',body:mediaMock}));
 await context.route('**/api/**',r=>{
  const path=new URL(r.request().url()).pathname;
  if(kind==='canvas' && path.startsWith('/api/canvas/v1/')) {
   let value;const project={id:'11111111-1111-4111-8111-111111111111',title:'Demo launch workspace',state:'active',createdBy:'demo-canvas',role:'owner'};
   if(path.endsWith('/session'))value={account:{id:'demo-canvas',email:'alex@example.test'},csrf:'synthetic-csrf'};
   else if(path.endsWith('/projects'))value={projects:[project]};
   else if(path.endsWith('/documents'))value={documents:[]};
   else if(path.endsWith('/artifacts'))value={artifacts:[]};
   else if(path.endsWith('/discussion/availability'))value={enabled:false};
   else if(path.includes('/apps/sessions'))value={sessions:[]};
   else return r.fulfill({status:404,contentType:'application/json',body:JSON.stringify({error:'No synthetic fixture for this Canvas operation'})});
   return r.fulfill({contentType:'application/json',body:JSON.stringify(value)});
  }
  let data;
  if(path.endsWith('/results'))data=results;
  else if(path.endsWith('/join'))data={roomId,mediaProvider:'livekit',serverUrl:'ws://synthetic.invalid',conversationUrl:'ws://synthetic.invalid',meetingToken:'demo-only',participantId:'demo',displayName:'Alex (Demo)'};
  else if(path.endsWith('/sessions')||path.endsWith('/control-state')||path.includes('/admission/')) {const own={id:'demo',name:'Alex (Demo)',state:'connected',host:true};data={revision:1,hostRevision:1,serverNow:Date.now(),roomId,canonicalUrl:room.shareUrl,ended:false,full:false,hostPresent:true,own,roster:[own],waiting:[]};if(path.endsWith('/sessions'))data={sessionCredential:'synthetic-session-only',state:data};}
  else if(path.startsWith('/api/smartmeet/tools/'))data={signedIn:false,managedByOther:false,actions:[],tools:[],items:[{index:0,text:'Prepare the launch checklist.',owner:'Alex (Demo)',deadline:null}]};
  else if(path.includes('simulation'))data={available:false,active:false};
  else if(path.includes('games'))data={available:true,games:[],revision:1};
  else if(path.includes('/resolve/') || path===`/api/smartmeet/rooms/${roomId}`)data={...room,sessionStatus:kind==='recap'?'ended':'active'};
  else {if(process.env.DEMO_DEBUG)console.error('Unmatched synthetic API',path);return r.fulfill({status:404,contentType:'application/json',body:JSON.stringify({ok:false,error:'No synthetic demo fixture for this operation'})});}
  return r.fulfill({contentType:'application/json',body:JSON.stringify({ok:true,data})});
 });
}
export async function enterLive(page){
 await page.getByLabel('Your name',{exact:true}).fill('Alex (Demo)');await page.getByLabel('Your email').fill('alex@example.test');
 await page.getByRole('button',{name:'Join meeting',exact:true}).click();await page.getByRole('button',{name:'Copy invite link',exact:true}).waitFor({timeout:20000}).catch(async e=>{if(process.env.DEMO_DEBUG)console.error(await page.locator('body').innerText());throw e;});
}
