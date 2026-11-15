// Original same-screen experiment: apparatus, field / current diagrams and directing.
import {T,renderer,scene,camera,apparatus,copper,cutEdge,metal,chrome,polymer,red,blue,mesh,cyl,ring,annulus,setLoop} from './apparatus.js';
import {M,stateAt,worldY,smooth,clamp} from './model.js';
const TL=await(await fetch('./timeline.json')).json(),W=1920,H=1080;
const left=apparatus(-3.30,false),right=apparatus(3.30,true);
const baseHalf=3.75;camera.left=-baseHalf*16/9;camera.right=baseHalf*16/9;camera.top=baseHalf;camera.bottom=-baseHalf;
const composite=document.createElement('canvas');composite.width=W;composite.height=H;document.body.appendChild(composite);const ctx=composite.getContext('2d',{alpha:false});
const palette={ink:'#263b3d',muted:'#65756f',current:'#246d7b',copper:'#945b41',rule:'#b5bfbb',field:'#749185'};
function ink(text,x,y,size=34,color=palette.ink,align='left') {ctx.font=`${size}px "Noto Sans CJK SC","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif`;ctx.fillStyle=color;ctx.textAlign=align;ctx.textBaseline='middle';ctx.fillText(text,x,y);}
function line(points,color=palette.rule,width=1,alpha=1,dash=[]){ctx.save();ctx.globalAlpha*=alpha;ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.restore();}
function project(x,y,z=0){const v=new T.Vector3(x,y,z).project(camera);return[(v.x+1)*W/2,(1-v.y)*H/2];}
function arrow(x,y,endY,color,width=3){line([[x,y],[x,endY]],color,width);const d=Math.sign(endY-y);ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x,endY);ctx.lineTo(x-7,endY-d*14);ctx.lineTo(x+7,endY-d*14);ctx.closePath();ctx.fill();}
function label(text,x,y,target,color=palette.muted,size=32){ink(text,x,y,size,color);const width=ctx.measureText(text).width;const start=x<target[0]?x+width+15:x-15;line([[start,y],[target[0]+(start<target[0]?-45:45),y],target],color,1.3);}
function setCamera(x,y,zoom=1,azimuth=0,elevation=.65){camera.zoom=zoom;camera.position.set(x+Math.sin(azimuth)*11,y+elevation,Math.cos(azimuth)*11);camera.lookAt(x,y,0);camera.updateProjectionMatrix();camera.updateMatrixWorld();}
function setBody(a,b,open,opacity){a.magnet.position.set(0,worldY(b.y),0);a.frontMat.opacity=opacity;for(const {jaw,sign} of a.jaws)jaw.position.x=sign*(M.magnetRadius*M.scale+.042+.20*open);}
function clearLoops(a){for(const loop of a.loops)loop.group.visible=false;}
function loopsFor(a,b,t,alpha=1){for(let i=0;i<2;i++){a.loops[i].direction=i?-1:1;const y=worldY(b.y)+(i?-.24:.24),inside=smooth((y-worldY(M.tubeBottom))/.15)*smooth((worldY(M.tubeTop)-y)/.15);setLoop(a.loops[i],y,t,inside*alpha*clamp(b.brake/(M.magnetMass*M.g)));}}

// Magnified pipe cross-sections. The actual angular gap is retained.
const rims=new T.Group();scene.add(rims);
function pipeSection(parent,broken){
 const ri=.76,ro=.97,half=.225,gap=broken?M.slitHalfAngle:0;
 const p=[new T.Vector2(ri,-half),new T.Vector2(ri,half),new T.Vector2(ro,half),new T.Vector2(ro,-half),new T.Vector2(ri,-half)];
 mesh(new T.LatheGeometry(p.reverse(),180,gap,Math.PI*2-gap*2),copper,parent,0,.35,0);
 if(broken)for(const angle of [-gap,gap]){const s=Math.sin(angle),c=Math.cos(angle),g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute([ri*s,.125,ri*c,ro*s,.125,ro*c,ro*s,.575,ro*c,ri*s,.575,ri*c],3));g.setIndex([0,1,2,0,2,3]);g.computeVertexNormals();const mat=cutEdge.clone();mat.side=T.DoubleSide;mesh(g,mat,parent);}
 mesh(cyl(1.10,.12,128),polymer,parent,0,.065,0);
 const r=.864,path=[];for(let i=0;i<=160;i++){const a=gap+(Math.PI*2-2*gap)*i/160;path.push(new T.Vector3(Math.sin(a)*r,.585,Math.cos(a)*r));}
 const material=new T.MeshBasicMaterial({color:broken?'#77938a':palette.current,transparent:true,opacity:0,depthTest:false,depthWrite:false});
 const tube=mesh(new T.TubeGeometry(new T.CatmullRomCurve3(path),180,.012,8,false),material,parent);tube.renderOrder=24;
 const arrows=[];for(let i=0;i<3;i++){const a=mesh(new T.ConeGeometry(.05,.17,16),material,parent);a.renderOrder=25;arrows.push(a);}
 const locals=[];
 if(broken)for(const side of [-1,1]){
  const m=material.clone();m.color.set(palette.current);const loop=ring(parent,.065,.006,.590,m);loop.position.x=side*.86;loop.renderOrder=25;
  const head=mesh(new T.ConeGeometry(.018,.055,12),m,parent);head.renderOrder=26;locals.push({loop,head,material:m,side});
 }
 return{material,arrows,locals,broken};
}
const rimLeft=new T.Group(),rimRight=new T.Group();rims.add(rimLeft,rimRight);rimLeft.position.x=-2.0;rimRight.position.x=2.0;
const rimA=pipeSection(rimLeft,false),rimB=pipeSection(rimRight,true);
function animateRims(t,current,localAlpha){
 for(const a of [rimA,rimB]){
  a.material.opacity=current*(a.broken?.20:.95);
  for(let i=0;i<a.arrows.length;i++){
   const angle=(t*.72+i*Math.PI*2/3)%(Math.PI*2);const h=a.arrows[i];h.visible=!a.broken&&current>.01;h.position.set(Math.sin(angle)*.864,.585,Math.cos(angle)*.864);h.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),new T.Vector3(Math.cos(angle),0,-Math.sin(angle)));
  }
  for(const b of a.locals){b.material.opacity=localAlpha*.88;const angle=t*1.2;b.head.position.set(b.side*.86+Math.sin(angle)*.065,.590,Math.cos(angle)*.065);b.head.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),new T.Vector3(Math.cos(angle),0,-Math.sin(angle)));}
 }
}

// Small still-life establishes copper and a nickel-plated permanent magnet.
const hero=new T.Group();scene.add(hero);
annulus(hero,.51,.65,.82,.53,copper).position.x=-.77;
mesh(cyl(.80,.12,96),polymer,hero,-.77,.065,0);
mesh(cyl(.65,.12,96),polymer,hero,.92,.065,0);
mesh(cyl(.245,.44,96),chrome,hero,.92,.35,0);mesh(cyl(.246,.034,96),red,hero,.92,.547,0);mesh(cyl(.246,.034,96),blue,hero,.92,.153,0);

// Dipole-shaped magnetic field lines; arrows run from N to S outside the magnet.
const fields=new T.Group();left.group.add(fields);const fieldMaterials=[];
function fieldPoint(theta,phi,L=.88){const r=L*Math.sin(theta)**2;return new T.Vector3(r*Math.sin(theta)*Math.cos(phi),r*Math.cos(theta),r*Math.sin(theta)*Math.sin(phi));}
for(const phi of [.25,1.15,2.15,3.35,4.45,5.4]){
 const points=[];for(let i=0;i<=90;i++)points.push(fieldPoint(.55+(Math.PI-1.10)*i/90,phi));
 const mat=new T.MeshBasicMaterial({color:palette.field,transparent:true,opacity:0,depthTest:false,depthWrite:false});fieldMaterials.push(mat);
 const a=mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points),120,.0048,6,false),mat,fields);a.renderOrder=19;
 for(const theta of [1.10,2.04]){const h=mesh(new T.ConeGeometry(.020,.070,12),mat,fields);h.position.copy(fieldPoint(theta,phi));h.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),fieldPoint(theta+.001,phi).sub(fieldPoint(theta-.001,phi)).normalize());h.renderOrder=20;}
}
const fixedY=3.10;
const fixedBand=annulus(left.group,M.outsideRadius*M.scale+.006,M.outsideRadius*M.scale+.018,.045,fixedY,new T.MeshBasicMaterial({color:palette.current,transparent:true,opacity:.9}));
const fixedCurrent=left.loops[0];
function showFields(body,alpha){fields.visible=alpha>.001;fields.position.y=worldY(body.y);for(const m of fieldMaterials)m.opacity=alpha*.72;}

const titles=['只开一条缝','差别就在这一条缝','铜没有铁那样的强吸附','磁铁在动，磁场也在动','盯住管壁上的这一圈','电荷沿管壁兜圈：涡流','涡流带来电磁阻力','慢慢下落，没有悬浮','纵缝切断了整圈回路','仍可能存在局部涡流','慢下来的能量，去了哪？','回路一变，刹车就弱了'];
function captionAt(t){return TL.captions.find(c=>t>=c.start&&t<c.end);}
function frameOverlay(t,i,p,body,extra){
 ctx.drawImage(renderer.domElement,0,0,W,H);
 ctx.fillStyle='#e7ebe7';ctx.fillRect(0,0,W,222);ctx.fillRect(0,946,W,134);
 ink(titles[i],960,91,49,palette.ink,'center');line([[110,144],[1810,144]]);
 const mode=extra.mode;
 if(mode==='compare'){
  const lp=project(left.group.position.x,2.3),rp=project(right.group.position.x,2.3);
  ink('完整铜管',lp[0],190,36,palette.ink,'center');ink('纵向开缝',rp[0],190,36,palette.ink,'center');line([[960,235],[960,914]],palette.rule,1,.7);
  const show=smooth((t-extra.release-1.25)/.4);
  ctx.globalAlpha=show;ink('缓慢下落',168,520,33,palette.copper);ink('更快落下',1137,520,33,palette.current);ctx.globalAlpha=1;
  const a=project(left.group.position.x,worldY(body.left.y)),b=project(right.group.position.x,worldY(body.right.y));
  line([[315,520],[a[0]-65,520],[a[0]-65,a[1]],[a[0]-30,a[1]]],palette.copper,1.2,show);
  line([[1284,520],[b[0]-65,520],[b[0]-65,b[1]],[b[0]-30,b[1]]],palette.current,1.2,show);
  if(t<extra.release+.5){const y=project(0,worldY(M.initialY))[1];line([[lp[0]-105,y],[lp[0]+105,y]],'#80958d',1,.7,[5,5]);line([[rp[0]-105,y],[rp[0]+105,y]],'#80958d',1,.7,[5,5]);}
  if(i===11&&t>p.end+.2)ink('闭合回路 → 涡流 → 电磁阻力',960,865,32,palette.current,'center');
 }else if(mode==='rims'){
  const a=project(-2,.35),b=project(2,.35);ink('完整环向回路',a[0],190,35,palette.ink,'center');ink('贯通纵缝',b[0],190,35,palette.ink,'center');line([[960,236],[960,914]],palette.rule,1,.7);
  if(i===1){const at=project(2,.58,.95);label('从上到下贯通',1335,812,at,palette.copper,33);}
  if(i===8){ink('环向电流',360,820,34,palette.current);ink('整圈回路被切断',1270,820,34,palette.copper);}
  if(i===9){ink('没有跨过缝隙的整圈电流',1100,804,32,palette.muted);label('局部涡流示意',1320,875,project(2+.86,.595,0),palette.current,31);}
 }else if(mode==='hero'){
  label('铜：非铁磁性材料',170,744,project(-.77,.55,0),palette.copper,34);label('磁铁',1470,744,project(.92,.35,0),palette.current,34);
 }else{
  const a=project(left.group.position.x,worldY(body.left.y));
  for(let y=.95;y<4.56;y+=.35){const a=project(left.group.position.x+.42,y),b=project(left.group.position.x+.48,y);if(a[1]>230&&a[1]<930)line([a,b],'#99a9a1',1,.7);}
  if(i===3){label('磁场线随磁铁移动',1280,700,project(left.group.position.x+.67,worldY(body.left.y)),palette.field,33);ink('N',a[0]-18,a[1]-38,27,'#a74b3e');ink('S',a[0]-18,a[1]+38,27,'#376c7e');}
  if(i===4||i===5){
   const band=project(left.group.position.x,fixedY);label('固定的一圈铜',220,band[1]+5,[band[0]-80,band[1]],palette.current,33);
   ink(worldY(body.left.y)>fixedY?'磁铁正在接近这一圈':'磁铁正在远离这一圈',1265,360,31,palette.muted);
   if(i===5)label('感应环流',1295,690,[band[0]+65,band[1]],palette.current,34);
  }
  if(i===6){label('感应电流',250,a[1]-52,[a[0]-60,a[1]-68],palette.current,34);arrow(1270,a[1]+55,a[1]-90,palette.current);ink('阻碍下落',1320,a[1]-20,35,palette.current);}
  if(i===7){const force=clamp(body.left.brake/(M.magnetMass*M.g),0,1.5);arrow(630,a[1]-70,a[1]+75,palette.copper);ink('重力',440,a[1],35,palette.copper);arrow(1290,a[1]+75,a[1]+75-145*force,palette.current);ink('电磁阻力',1340,a[1],35,palette.current);ink('仍在向下运动',960,824,34,palette.muted,'center');}
  if(i===10){
   const initial=M.magnetMass*M.g*(M.initialY-M.magnetHeight/2),ep=M.magnetMass*M.g*(body.left.y-M.magnetHeight/2),ek=.5*M.magnetMass*body.left.v**2;
   const rows=[['重力势能',ep/initial,palette.copper],['动能',ek/initial,'#788c83'],['铜管内能',body.left.heat/initial,'#b87948']];
   for(let j=0;j<rows.length;j++){const [name,f,color]=rows[j],y=384+j*137;ink(name,1225,y,32,color);line([[1225,y+44],[1745,y+44]],'#bac6bf',22,.5);line([[1225,y+44],[1225+520*f,y+44]],color,22);}
   ink('能量分配示意',1225,817,25,palette.muted);label('势能减少',165,478,project(left.group.position.x,worldY(body.left.y)),palette.copper,32);
  }
 }
 const note=mode==='rims'?'管壁截面示意':mode==='hero'?'材料示意':i===10?'慢动作原理示意':'慢动作原理示意 · 前壁透视';ink(note,110,894,22,palette.muted);
 const cap=captionAt(t);if(cap)ink(cap.text,960,1003,40,palette.ink,'center');
}
export function render(t){
 t=clamp(t,0,TL.duration);let i=TL.paragraphs.findIndex((p,k)=>t>=p.shotStart&&(k===TL.paragraphs.length-1||t<TL.paragraphs[k+1].shotStart));if(i<0)i=0;
 const p=TL.paragraphs[i],u=clamp((t-p.shotStart)/(p.shotEnd-p.shotStart));
 left.group.visible=true;right.group.visible=false;rims.visible=false;hero.visible=false;fields.visible=false;fixedBand.visible=false;clearLoops(left);clearLoops(right);
 let raw=0,body,extra={mode:'close'},mode=extra.mode;
 if(i===0||i===11){
  const release=i===0?TL.cues.release:TL.cues.finalRelease;
  raw=Math.max(0,(t-release)*(i===11?1.2:1)+M.release);body=stateAt(raw);setBody(left,body.left,body.opening,1-smooth((t-release-.1)/.65)*.84);setBody(right,body.right,body.opening,1-smooth((t-release-.1)/.65)*.84);right.group.visible=true;
  setCamera(0,2.75,1);extra={mode:'compare',release};
  if(i===11){loopsFor(left,body.left,t,smooth((t-p.shotStart-1.4)/.5));}
 }else if(i===1||i===8||i===9){
  left.group.visible=false;rims.visible=true;setCamera(0,.76,1.42,.015*Math.sin(u*Math.PI),6.3);
  animateRims(t,i===1?0:smooth((t-p.shotStart-.2)/.5),i===9?smooth((t-p.shotStart-.15)/.5):0);extra.mode='rims';body=stateAt(0);
 }else if(i===2){
  left.group.visible=false;hero.visible=true;setCamera(0,.56,2.6,.15+.09*u,4.0);extra.mode='hero';body=stateAt(0);
 }else{
  if(i===3)raw=1.8+u*2.5;
  if(i===4||i===5){const start=TL.paragraphs[4].shotStart,end=TL.paragraphs[5].shotEnd;raw=2.2+clamp((t-start)/(end-start))*3.0;}
  if(i===6||i===7){const start=TL.paragraphs[6].shotStart,end=TL.paragraphs[7].shotEnd;raw=2.0+clamp((t-start)/(end-start))*4.6;}
  if(i===10)raw=1.7+u*6.4;
  body=stateAt(raw);setBody(left,body.left,1,.13);
  if(i===10){setCamera(left.group.position.x+.95,2.75,1.0);loopsFor(left,body.left,t,.5);}
  else if(i===4||i===5)setCamera(left.group.position.x,fixedY,2.05,.035,2.6);
  else setCamera(left.group.position.x,worldY(body.left.y)+.07,2.05,.04,.85);
  if(i===3)showFields(body.left,smooth((t-p.shotStart-.2)/.8));
  if(i===4||i===5){
   showFields(body.left,.70);fixedBand.visible=true;
   const dy=worldY(body.left.y)-fixedY,q=dy/.30;
   const strength=clamp(Math.abs(q)/(1+q*q)**2.5/(.5/1.25**2.5));fixedCurrent.direction=-Math.sign(dy||1);
   const alpha=i===5?smooth((t-TL.cues.current+.55)/.55)*strength:0;setLoop(fixedCurrent,fixedY,t,alpha);
  }
  if(i===6||i===7){loopsFor(left,body.left,t,1);if(i===6)showFields(body.left,.25);}
 }
 renderer.render(scene,camera);frameOverlay(t,i,p,body,extra);
 window.FRAME_STATE={t,shot:i,raw,mode:extra.mode,left:body.left,right:body.right,frontIsVisualOnly:true};
}
window.render=render;window.DUR=TL.duration;window.FPS=24;window.framePNG=()=>composite.toDataURL('image/png');window.frameJPEG=()=>composite.toDataURL('image/jpeg',.97);window.TIMELINE=TL;
window.cover=()=>{render(5.5);ctx.fillStyle='#e7ebe7';ctx.fillRect(0,0,W,150);ctx.fillRect(0,946,W,134);ink('一条缝，松开磁力刹车',960,89,72,palette.ink,'center');ink('铜管与磁铁',960,190,29,palette.muted,'center');ink('只改一个条件，结果完全不同',960,1003,43,palette.ink,'center');return composite.toDataURL('image/png');};
await document.fonts.ready;render(0);window.READY=true;
