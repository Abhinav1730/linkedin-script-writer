export const demoRoomId='sm_00000000-0000-4000-8000-000000000051';
export function validateRoute(feature){
 const allowed=new Set(['/','/meeting/new','/dashboard','/form','/integrations','/recent-meetings','/work','/book']);
 if(feature.demo==='canvas' && feature.path==='/work')return true;
 if(allowed.has(feature.path) && !feature.demo)return true;
 if(['live','recap'].includes(feature.demo) && [`/meeting/${demoRoomId}`,`/meeting/${demoRoomId}/summary`].includes(feature.path))return true;
 throw Error('Unapproved route');
}
export function visibleEvidence(){
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);const out=[];
 while(walker.nextNode()){
  const n=walker.currentNode,p=n.parentElement;
  if(!p||p.closest('input,textarea,[data-private],[role=alert],script,style,[hidden]')||!p.checkVisibility({checkVisibilityCSS:true}))continue;
  const t=n.textContent.trim();if(t)out.push(t);
 }
 return out.join('\n').slice(0,16000).replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi,'[demo email]').replace(/https?:\/\/\S+/g,'[link]');
}
