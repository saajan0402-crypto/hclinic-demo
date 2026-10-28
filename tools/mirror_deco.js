const DECO=new Set(['f05257','5141b7','499e9f','c2f3e6','815625','d5865d','7b3342','82ad3c','b04085','e83bf6','a9cbcc','299d1f']);
const hashOf=n=>{ if(n.type!=='RECTANGLE'||!n.fills||n.fills===figma.mixed) return null; const f=n.fills[0]; return f&&f.type==='IMAGE'?f.imageHash.slice(0,6):null; };
const isDeco=n=>DECO.has(hashOf(n)||'')&&!/^写真|^画像枠/.test(n.name);
const K=1.6, WS=375, WP=1440;
const rel=(n,P)=>{const a=n.absoluteBoundingBox,b=P.absoluteBoundingBox; return {x:a.x-b.x,y:a.y-b.y,w:a.width,h:a.height};};
const bandBot=s=>{ const b=s.children.find(c=>c.name==='写真帯'||/^写真｜DSC00335/.test(c.name)); return b?b.y+b.height:0; };
async function mirror(no){
  const SPP=await figma.getNodeByIdAsync('218:6550'), PCP=await figma.getNodeByIdAsync('218:33823');
  await figma.setCurrentPageAsync(SPP); const re=new RegExp('^SP｜No\\.'+no+' '); const fs=SPP.children.find(c=>re.test(c.name));
  await figma.setCurrentPageAsync(PCP); const rp=new RegExp('^PC｜No\\.'+no+' '); const fp=PCP.children.find(c=>rp.test(c.name));
  if(!fs||!fp) return no+' missing';
  let wide=0;
  for(const p of fp.children){ if(!p.children||p.type==='INSTANCE') continue;
    const s=fs.children.find(c=>c.name===p.name&&c.children&&c.type!=='INSTANCE'); if(!s) continue;
    const sd=s.children.filter(isDeco);
    const old=p.children.filter(isDeco); old.forEach(o=>o.remove());
    if(!sd.length) continue;
    const rs=bandBot(s), rpb=bandBot(p); const Hs=Math.max(1,s.height-rs), Hp=Math.max(1,p.height-rpb);
    let k0=0; while(k0<p.children.length){ const c=p.children[k0]; if(c.x<=1&&c.y<=1&&c.width>=p.width*0.95&&c.height>=p.height*0.9&&!isDeco(c)) k0++; else break; }
    for(const d of sd){ const bb=rel(d,s); if(bb.y+bb.h<rs+10) continue;
      const isWide=bb.w>WS*1.2;
      let k=isWide? WP*1.1/bb.w : K; if(!isWide&&bb.h*k>p.height*0.95) k=p.height*0.95/bb.h;
      const c=d.clone(); p.insertChild(k0,c); k0++; if(p.layoutMode&&p.layoutMode!=='NONE') c.layoutPositioning='ABSOLUTE';
      c.resize(d.width*k,d.height*k); c.blendMode='MULTIPLY';
      const W=bb.w*k,H=bb.h*k; const cx=bb.x+bb.w/2;
      const tx=isWide? (WP-W)/2 : (cx<WS/2? bb.x*k : WP-(WS-(bb.x+bb.w))*k-W);
      const cyr=(bb.y+bb.h/2-rs)/Hs; let ty;
      if(isWide) ty=rpb+cyr*Hp-H/2;
      else if(cyr<0.33) ty=rpb+(bb.y-rs)*k; else if(cyr>0.66) ty=p.height-(s.height-(bb.y+bb.h))*k-H; else ty=rpb+cyr*Hp-H/2;
      if(!isWide) ty=Math.min(Math.max(ty,Math.min(rpb,p.height-H)-H*0.1),p.height-H*0.9);
      const cur=rel(c,p); c.x+=tx-cur.x; c.y+=ty-cur.y; if(isWide) wide++; }
    p.clipsContent=true;
  }
  return no+(wide?' wide'+wide:'');
}
