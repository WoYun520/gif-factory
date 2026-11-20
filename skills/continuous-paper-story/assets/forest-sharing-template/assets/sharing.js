(()=>{
const c=document.getElementById('sharing-art').getContext('2d'),I={};let built=false;
const names=['background','loaf','small','large','small-bite','large-bite','crumbs',...Array.from({length:12},(_,i)=>`rabbit-${String(i).padStart(2,'0')}`),...Array.from({length:12},(_,i)=>`bear-${String(i).padStart(2,'0')}`),...Array.from({length:4},(_,i)=>`ride-rabbit-${String(i).padStart(2,'0')}`)];
for(const n of names){I[n]=new Image();I[n].src=`assets/${n}.png`}
const C=x=>Math.max(0,Math.min(1,x)),S=x=>{x=C(x);return x*x*(3-2*x)},L=(a,b,u)=>a+(b-a)*u;
const SCALE=1.3,Y=930-340*SCALE,BY=930-350*SCALE,BEAR=1461;
const rp={2:[92,188],3:[211,188],4:[211,190],5:[185,182],6:[182,181],7:[194,189],8:[196,190],9:[197,187],10:[234,168],11:[242,148]};
const rl={5:[236,175],6:[242,173],7:[269,165],8:[277,158]};
const bp={3:[139,178],4:[130,169],5:[232,213],6:[231,212],7:[145,178],8:[116,172],9:[235,205],10:[200,158],11:[210,159]};
function root(t){return L(430,1270,S(t/2.4))}
function camera(t){return Math.max(0,root(t)-760)}
function rabbitPose(t,x){if(t<2.12)return{family:'ride',n:Math.floor((x-430)/(60*SCALE/.97))%4};let n=0;for(const [time,pose] of [[2.4,1],[2.85,2],[3.3,3],[3.85,4],[4.35,5],[4.7,6],[5.1,7],[5.45,8],[5.85,9],[8.35,10],[8.85,11]])if(t>=time)n=pose;return{family:'rabbit',n}}
function bearPose(t){let n=0;for(const [time,pose] of [[.55,1],[1.75,2],[4.65,3],[5.35,4],[5.95,5],[6.5,6],[6.95,7],[7.3,8],[7.95,9],[8.45,10],[8.95,11]])if(t>=time)n=pose;return n}
function rpoint(p,x){return{x:x+(p[0]-190)*SCALE,y:Y+p[1]*SCALE}}
function bpoint(p){return{x:BEAR+(p[0]-190)*SCALE,y:BY+p[1]*SCALE}}
function bread(n,p,w,cam,angle=0){const im=I[n],h=w*im.height/im.width;c.save();c.translate(p.x-cam,p.y-h*.43);c.rotate(angle);c.drawImage(im,-w/2,-h/2,w,h);c.restore();return {name:n,x:p.x,y:p.y-h*.43,width:w,height:h}}
function shadow(x,y,rx,ry,a){c.save();c.globalAlpha=a;c.fillStyle='#3d392c';c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fill();c.restore()}
function title(t){if(t<8.9)return;const u=S((t-8.9)/.45);c.save();c.translate(420,L(-110,170,u));c.rotate(-.035);c.shadowColor='#22271d30';c.shadowBlur=10;c.shadowOffsetY=5;c.fillStyle='#eee2c8';c.fillRect(-290,-76,580,152);c.shadowColor='transparent';c.fillStyle='#49543c';c.textAlign='center';c.font='54px StorySong, serif';c.fillText('留一半给你',0,0);c.font='22px StorySong, serif';c.fillText('小 兔 的 林 间 奇 遇',0,43);c.restore()}
function draw(t){if(!built)return;const x=root(t),cam=camera(t),r=rabbitPose(t,x),b=bearPose(t);c.clearRect(0,0,1920,1080);c.drawImage(I.background,-cam,0,3060,1080);
 shadow(BEAR-cam,930,218,8,.18);c.drawImage(I[`bear-${String(b).padStart(2,'0')}`],BEAR-cam-190*SCALE,BY,362*SCALE,362*SCALE);
 shadow(x-cam,930,147,7,.18);if(t>2.4)shadow(x-cam-9,920,25,3,.17);
 const pieces=[];
 if(t<3){const p=rpoint([99,182],x);pieces.push({...bread('loaf',p,110,cam),state:'basket'})}
 c.drawImage(I[r.family==='ride'?`ride-rabbit-${String(r.n).padStart(2,'0')}`:`rabbit-${String(r.n).padStart(2,'0')}`],x-cam-190*SCALE,Y,362*SCALE,362*SCALE);
 if(t>=3&&t<4.35){const p=rpoint(rp[r.n]||[211,188],x);p.y+=20;pieces.push({...bread('loaf',p,110,cam),state:'rabbit-whole'})}
 if(t>=4.35){const p=rpoint(rp[r.n]||rp[9],x);pieces.push({...bread(t>=9.12?'small-bite':'small',p,48,cam,t>8.85?-.12:0),state:'rabbit-small'});
 let q;if(t<5.85)q=rpoint(rl[r.n]||rl[8],x);else if(t<5.95){const a=rpoint(rl[8],x),z=bpoint(bp[4]),u=S((t-5.85)/.1);q={x:L(a.x,z.x,u),y:L(a.y,z.y,u)}}else q=bpoint(bp[b]||bp[5]);
 pieces.push({...bread(t>=9.17?'large-bite':'large',q,80,cam,t>8.95?.1:0),state:t<5.85?'rabbit-offering':t<5.95?'both-contact':'bear-large'});
 if(t<4.65){const u=C((t-4.35)/.3),a=rpoint([211,188],x);c.save();c.globalAlpha=1-u;c.drawImage(I.crumbs,a.x-cam-14,a.y+u*u*65,28,20);c.restore()}
 }
 title(t);window.HALF_STORY={t,rabbit:r,bear:b,root:x,camera:cam,pieces};
}
const ready=(async()=>{await Promise.all([...Object.values(I).map(i=>i.decode()),document.fonts.load('54px StorySong, serif')]);built=true;draw(0);const st={t:0};window.__timelines.sharing=gsap.timeline({paused:true}).to(st,{t:10,duration:10,ease:'none',onUpdate:()=>draw(st.t)})})();window.__hf=window.__hf||{};window.__hf.buildReady={sharing:ready};window.addEventListener('hf-seek',e=>e.detail.waitUntil(ready.then(()=>draw(e.detail.time))));
})();
