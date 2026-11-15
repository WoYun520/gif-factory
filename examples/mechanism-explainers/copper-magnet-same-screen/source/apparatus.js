// Independently authored apparatus and motion, built on the previous own control-test format.
import * as T from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {M,stateAt,worldY,smooth,clamp} from './model.js';
const W=1920,H=1080;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(2);renderer.setSize(W,H);renderer.outputColorSpace=T.SRGBColorSpace;
renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=.99;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
const scene=new T.Scene();scene.background=new T.Color('#e7ebe7');
const pmrem=new T.PMREMGenerator(renderer),room=new RoomEnvironment();scene.environment=pmrem.fromScene(room,.05).texture;pmrem.dispose();room.dispose();
const camera=new T.OrthographicCamera(-6.044,6.044,3.4,-3.4,.1,50);
camera.position.set(0,3.62,11);camera.lookAt(0,2.97,0);camera.updateMatrixWorld();
scene.add(new T.HemisphereLight('#f4f8f8','#a8b7ac',1.1));
const key=new T.DirectionalLight('#fff5e7',2.5);key.position.set(-4,8,6);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-7,right:7,top:7,bottom:-5});key.shadow.bias=-.00008;key.shadow.normalBias=.015;key.shadow.radius=4;scene.add(key);
const rim=new T.DirectionalLight('#cee3ef',1.6);rim.position.set(4,6,-4);scene.add(rim);
const floor=new T.Mesh(new T.PlaneGeometry(200,200),new T.MeshStandardMaterial({color:'#ced7d0',roughness:.85}));floor.rotation.x=-Math.PI/2;floor.position.y=-.012;floor.receiveShadow=true;scene.add(floor);

const copper=new T.MeshStandardMaterial({color:'#bb6944',metalness:1,roughness:.28,envMapIntensity:1.05});
const cutEdge=new T.MeshStandardMaterial({color:'#e1a078',metalness:1,roughness:.21,envMapIntensity:1.1});
const metal=new T.MeshStandardMaterial({color:'#a8b2ae',metalness:.85,roughness:.28});
const chrome=new T.MeshStandardMaterial({color:'#d4dbd9',metalness:1,roughness:.16,envMapIntensity:1.3});
const dark=new T.MeshStandardMaterial({color:'#3c514b',roughness:.7});
const polymer=new T.MeshStandardMaterial({color:'#81958b',roughness:.67,metalness:.02});
const foam=new T.MeshStandardMaterial({color:'#b9c8bf',roughness:.98});
const red=new T.MeshStandardMaterial({color:'#ab493b',roughness:.5,metalness:.15});
const blue=new T.MeshStandardMaterial({color:'#346676',roughness:.5,metalness:.15});
function mesh(geometry,material,parent,x=0,y=0,z=0){const a=new T.Mesh(geometry,material);a.position.set(x,y,z);a.castShadow=!material.transparent;a.receiveShadow=true;parent.add(a);return a;}
const cyl=(r,h,n=96)=>new T.CylinderGeometry(r,r,h,n);
function ring(parent,r,t,y,material){const a=mesh(new T.TorusGeometry(r,t,10,96),material,parent,0,y,0);a.rotation.x=Math.PI/2;return a;}
function annulus(parent,ri,ro,h,y,material){return mesh(new T.LatheGeometry([new T.Vector2(ri,-h/2),new T.Vector2(ri,h/2),new T.Vector2(ro,h/2),new T.Vector2(ro,-h/2),new T.Vector2(ri,-h/2)].reverse(),96),material,parent,0,y,0);}
const ri=M.insideRadius*M.scale,ro=M.outsideRadius*M.scale,tubeLength=(M.tubeTop-M.tubeBottom)*M.scale;
function sector(parent,start,length,material){
 const profile=[new T.Vector2(ri,0),new T.Vector2(ri,tubeLength),new T.Vector2(ro,tubeLength),new T.Vector2(ro,0),new T.Vector2(ri,0)];
 return mesh(new T.LatheGeometry(profile.reverse(),Math.ceil(length*30),start,length),material,parent,0,worldY(M.tubeBottom),0);
}
function slitFace(parent,angle){
 const y0=worldY(M.tubeBottom),y1=worldY(M.tubeTop),s=Math.sin(angle),c=Math.cos(angle);
 const vertices=[ri*s,y0,ri*c,ro*s,y0,ro*c,ro*s,y1,ro*c,ri*s,y1,ri*c];
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(vertices,3));g.setIndex([0,1,2,0,2,3]);g.computeVertexNormals();
 const mat=cutEdge.clone();mat.side=T.DoubleSide;return mesh(g,mat,parent);
}
function currentLoop(parent,broken,direction){
 const group=new T.Group();parent.add(group);const radius=ro+.065,gap=broken?.28:0;
 const points=[];for(let i=0;i<=120;i++){const a=gap+(Math.PI*2-2*gap)*i/120;points.push(new T.Vector3(Math.sin(a)*radius,0,Math.cos(a)*radius));}
 const path=new T.CatmullRomCurve3(points,false,'centripetal');
 const material=new T.MeshBasicMaterial({color:broken?'#79918a':'#246d7b',transparent:true,opacity:0,depthTest:false,depthWrite:false});
 const line=mesh(new T.TubeGeometry(path,160,.006,6,false),material,group);line.renderOrder=20;
 const arrows=[];for(let i=0;i<2;i++){const arrow=mesh(new T.ConeGeometry(.025,.078,12),material,group);arrow.renderOrder=21;arrows.push(arrow);}
 return{group,material,arrows,direction,broken,radius};
}
function setLoop(loop,y,t,alpha){
 loop.group.position.y=y;loop.group.visible=alpha>.001;loop.material.opacity=alpha*(loop.broken?.38:.96);
 for(let i=0;i<loop.arrows.length;i++){
  const margin=loop.broken?.36:0,span=2*Math.PI-2*margin;
  const phase=((t*.34*loop.direction+i*.5)%1+1)%1;
  const angle=margin+phase*span;
  loop.arrows[i].position.set(Math.sin(angle)*loop.radius,0,Math.cos(angle)*loop.radius);
  loop.arrows[i].quaternion.setFromUnitVectors(new T.Vector3(0,1,0),new T.Vector3(Math.cos(angle)*loop.direction,0,-Math.sin(angle)*loop.direction));
 }
}
function apparatus(x,slit){
 const group=new T.Group();group.position.x=x;scene.add(group);
 mesh(cyl(.77,.14,128),polymer,group,0,.075,0);ring(group,.65,.01,.15,dark);
 const catchCup=annulus(group,.35,.43,.28,.30,polymer);mesh(cyl(.345,.16,96),foam,group,0,.37,0);
 mesh(cyl(.027,4.45,64),metal,group,.73,2.39,-.20);mesh(cyl(.078,.12,64),polymer,group,.73,.22,-.20);
 mesh(cyl(.027,.36,64),metal,group,.73,4.70,-.20);
 for(const y of [1.25,4.13]){
  const arm=mesh(cyl(.025,.46,48),metal,group,.49,y,-.11);arm.rotation.z=Math.PI/2;
  annulus(group,ro+.003,ro+.035,.11,y,polymer);
  const screw=mesh(new T.CylinderGeometry(.055,.055,.10,6),metal,group,.68,y,.00);screw.rotation.x=Math.PI/2;
 }
 const frontMat=copper.clone();frontMat.transparent=true;frontMat.opacity=1;frontMat.depthWrite=false;frontMat.side=T.DoubleSide;
 const frontAngle=.88;
 sector(group,frontAngle,2*Math.PI-2*frontAngle,copper);
 if(slit){sector(group,-frontAngle,frontAngle-M.slitHalfAngle,frontMat);sector(group,M.slitHalfAngle,frontAngle-M.slitHalfAngle,frontMat);slitFace(group,-M.slitHalfAngle);slitFace(group,M.slitHalfAngle);}
 else sector(group,-frontAngle,2*frontAngle,frontMat);
 // Rim geometry keeps the real longitudinal opening on the right.
 for(const y of [worldY(M.tubeBottom),worldY(M.tubeTop)]){
  const p=[];const a=slit?M.slitHalfAngle:0;for(let i=0;i<=180;i++){const u=a+(2*Math.PI-2*a)*i/180;p.push(new T.Vector3(Math.sin(u)*(ri+ro)/2,y,Math.cos(u)*(ri+ro)/2));}
  mesh(new T.TubeGeometry(new T.CatmullRomCurve3(p),180,(ro-ri)*.48,10,false),cutEdge,group);
 }
 const magnet=new T.Group();group.add(magnet);magnet.position.y=worldY(M.initialY);
 const mr=M.magnetRadius*M.scale,mh=M.magnetHeight*M.scale;
 mesh(cyl(mr,mh,96),chrome,magnet);mesh(cyl(mr+.001,.027,96),red,magnet,0,mh/2-.023,0);mesh(cyl(mr+.001,.027,96),blue,magnet,0,-mh/2+.023,0);
 ring(magnet,mr-.009,.005,mh/2+.002,chrome);
 const jaws=[];
 for(const sign of [-1,1]){
  const jaw=mesh(new T.BoxGeometry(.085,.17,.15),polymer,group,sign*(mr+.042),worldY(M.initialY),-.014);jaws.push({jaw,sign});
 }
 const releaseArm=mesh(new T.BoxGeometry(1.20,.06,.10),metal,group,.18,worldY(M.initialY)+.05,-.14);
 const loops=[currentLoop(group,slit,1),currentLoop(group,slit,-1)];
 return{group,frontMat,magnet,jaws,loops,slit};
}

export {T,renderer,scene,camera,floor,apparatus,copper,cutEdge,metal,chrome,dark,polymer,foam,red,blue,mesh,cyl,ring,annulus,currentLoop,setLoop,ri,ro};
