// Original qualitative model. Equal gravity, magnets and release conditions;
// a longitudinal slit reduces, rather than eliminates, magnetic damping.
export const M={duration:16,release:.55,timeScale:3.8,g:9.81,scale:9,origin:.45,
 initialY:.479,tubeTop:.455,tubeBottom:.055,magnetHeight:.032,magnetMass:.05,
 insideRadius:.024,outsideRadius:.027,magnetRadius:.018,slitHalfAngle:.14,
 gammaClosed:60,gammaSlit:1.2,dt:1/2400};
export const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
export const smooth=v=>{v=clamp(v);return v*v*(3-2*v);};
const floor=M.magnetHeight/2;
export const worldY=y=>M.origin+y*M.scale;
export function immersion(y){
 const top=clamp((M.tubeTop+M.magnetHeight/2-y)/M.magnetHeight);
 const bottom=clamp((y-M.tubeBottom+M.magnetHeight/2)/M.magnetHeight);
 return smooth(top)*smooth(bottom);
}
function run(gamma){
 const initialEnergy=M.magnetMass*M.g*(M.initialY-floor);
 const samples=[{y:M.initialY,v:0,brake:0,heat:0,pad:0,landed:false}];let y=M.initialY,v=0,impact=null,heat=0,pad=0;
 const acceleration=(p,u)=>M.g-gamma*immersion(p)*u;
 const count=Math.ceil((M.duration-M.release)/M.timeScale/M.dt)+2;
 for(let i=1;i<=count;i++){
  const h=M.dt;
  if(y>floor){
   const a1=acceleration(y,v),p1=-v;
   const a2=acceleration(y+p1*h/2,v+a1*h/2),p2=-(v+a1*h/2);
   const a3=acceleration(y+p2*h/2,v+a2*h/2),p3=-(v+a2*h/2);
   const a4=acceleration(y+p3*h,v+a3*h),p4=-(v+a3*h);
   const power=(p,u)=>M.magnetMass*gamma*immersion(p)*u*u;
   heat+=h*(power(y,v)+2*power(y+p1*h/2,v+a1*h/2)+2*power(y+p2*h/2,v+a2*h/2)+power(y+p3*h,v+a3*h))/6;
   const next=y+h*(p1+2*p2+2*p3+p4)/6;
   v+=h*(a1+2*a2+2*a3+a4)/6;
   if(next<=floor){if(impact===null)impact=M.release+(i-1+(y-floor)/(y-next))*h*M.timeScale;y=floor;v=0;pad=Math.max(0,initialEnergy-heat);}
   else y=next;
  }
  samples.push({y,v,brake:M.magnetMass*gamma*immersion(y)*v,heat,pad,landed:y<=floor});
 }
 return{samples,impact};
}
const closed=run(M.gammaClosed),slit=run(M.gammaSlit);
function at(table,t){
 if(t<=M.release)return{y:M.initialY,v:0,brake:0,heat:0,pad:0,landed:false};
 const index=Math.max(0,(t-M.release)/M.timeScale/M.dt),i=Math.floor(index),u=index-i;
 const a=table.samples[Math.min(i,table.samples.length-1)],b=table.samples[Math.min(i+1,table.samples.length-1)];
 return{y:a.y+(b.y-a.y)*u,v:a.v+(b.v-a.v)*u,brake:a.brake+(b.brake-a.brake)*u,heat:a.heat+(b.heat-a.heat)*u,pad:a.pad+(b.pad-a.pad)*u,landed:a.landed&&b.landed};
}
export function stateAt(t){t=clamp(t,0,M.duration);return{t,left:at(closed,t),right:at(slit,t),released:t>=M.release,
 opening:smooth((t-.35)/.20),reveal:smooth((t-.67)/.55),diagram:smooth((t-1.65)/.55),rightImpact:slit.impact,leftImpact:closed.impact};}
export const events={rightImpact:slit.impact,leftImpact:closed.impact};
