const DRY=false;
const DECO=new Set(['f05257','5141b7','499e9f','c2f3e6','815625','d5865d','7b3342','82ad3c','b04085','e83bf6','a9cbcc','299d1f']);
const hashOf=n=>{ if(n.type!=='RECTANGLE'||!n.fills||n.fills===figma.mixed) return null; const f=n.fills[0]; return f&&f.type==='IMAGE'?f.imageHash.slice(0,6):null; };
const isDeco=n=>DECO.has(hashOf(n)||'')&&!/^写真|^画像枠/.test(n.name);
const out={};
for(const [pid,pre] of [['218:6550','SP'],['218:33823','PC']]){ const P=await figma.getNodeByIdAsync(pid); await figma.setCurrentPageAsync(P);
  let done=0, tg=0; const skip=[];
  for(const f of P.children.filter(c=>new RegExp('^'+pre+'｜No\\.\\d\\d ').test(c.name))){
    if(!DRY) f.clipsContent=true;
    for(const s of f.children){ if(!s.children||s.type==='INSTANCE') continue; const sb=s.absoluteBoundingBox;
      const decos=s.children.filter(isDeco); if(!decos.length) continue;
      const T=decos.filter(c=>{ const h=hashOf(c), b=c.absoluteBoundingBox; if(['5141b7','d5865d','815625'].includes(h)) return false; if(b.width>sb.width*1.05&&h!=='c2f3e6') return false; return b.y-sb.y<-5; });
      if(!T.length) continue;
      const over=s.children.filter(c=>!isDeco(c)&&c.visible!==false&&c.absoluteBoundingBox&&(()=>{const b=c.absoluteBoundingBox; return b.x<sb.x-1||b.y<sb.y-1||b.x+b.width>sb.x+sb.width+1||b.y+b.height>sb.y+sb.height+1;})());
      if(over.length){ skip.push(f.name.slice(3,5)+' '+s.name.slice(6,14)+': '+over.map(o=>o.name.slice(0,10)).join('/')); continue; }
      tg+=T.length;
      if(DRY){ done++; continue; }
      // clip frame for non-target decos
      const rest=decos.filter(c=>!T.includes(c));
      if(rest.length){ const idx=s.children.indexOf(decos[0]); const cf=figma.createFrame(); cf.name='背景あしらい（クリップ）'; cf.fills=[]; cf.clipsContent=true;
        s.insertChild(idx,cf); if(s.layoutMode&&s.layoutMode!=='NONE') cf.layoutPositioning='ABSOLUTE'; cf.resize(s.width,s.height); cf.x=0; cf.y=0;
        for(const r of rest){ const x=r.x,y=r.y; cf.appendChild(r); r.x=x; r.y=y; } }
      s.clipsContent=false; done++;
    } }
  out[pre]={sections:done,targets:tg,skip}; }
return JSON.stringify(out);
