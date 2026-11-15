// Small local artifact server, written for this sample.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.json':'application/json','.otf':'font/otf','.jpg':'image/jpeg','.png':'image/png','.mp4':'video/mp4'};
const server=http.createServer((req,res)=>{
 try{
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  const f=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
  if(!f.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
  if(!fs.existsSync(f)||!fs.statSync(f).isFile()){res.writeHead(404);res.end();return;}
  res.writeHead(200,{'content-type':mime[path.extname(f)]||'application/octet-stream','cache-control':'no-store'});fs.createReadStream(f).pipe(res);
 }catch{res.writeHead(400);res.end();}
});
server.listen(0,'127.0.0.1',()=>{
 const address=server.address();const info={pid:process.pid,url:`http://127.0.0.1:${address.port}/`};
 fs.mkdirSync(path.join(root,'out'),{recursive:true});fs.writeFileSync(path.join(root,'out/server.json'),JSON.stringify(info));console.log(JSON.stringify(info));
});
process.stdin.resume();process.stdin.on('data',b=>{if(b.toString().includes('stop'))server.close(()=>process.exit(0));});
process.on('SIGTERM',()=>server.close(()=>process.exit(0)));
