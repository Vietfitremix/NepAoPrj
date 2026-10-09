// Align independently generated garment sprites to the original body canvas.
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url));
const {createCanvas,loadImage}=require('@napi-rs/canvas');
const items=JSON.parse(await readFile(path.join(root,'assets/metadata/bottoms-items.json'),'utf8'));
const partial=process.argv.includes('--partial'),records=[];
async function raster(file){const img=await loadImage(await readFile(file)),canvas=createCanvas(1024,1536),ctx=canvas.getContext('2d');ctx.drawImage(img,0,0,1024,1536);return{canvas,ctx,data:ctx.getImageData(0,0,1024,1536)};}
function bounds(data,y0=0,y1=1535,x0=0,x1=1023){let lo=1024,hi=-1,top=1536,bottom=-1;for(let y=Math.max(0,Math.floor(y0));y<=Math.min(1535,Math.ceil(y1));y++)for(let x=x0;x<=x1;x++)if(data[(y*1024+x)*4+3]>=230){lo=Math.min(lo,x);hi=Math.max(hi,x);top=Math.min(top,y);bottom=Math.max(bottom,y);}if(hi<lo)throw Error('Empty garment/body region');return{left:lo,right:hi,top,bottom,width:hi-lo+1,height:bottom-top+1,center:(lo+hi)/2};}
function legs(data,y,left=0,right=1023){const runs=[];let start=-1;y=Math.round(y);for(let x=left;x<=right+1;x++){const opaque=x<=right&&data[(y*1024+x)*4+3]>=230;if(opaque&&start<0)start=x;if(!opaque&&start>=0){if(x-start>8)runs.push([start,x]);start=-1;}}return runs;}
for(const item of items)for(const view of ['front','left','right','back']){
 const dir=path.join(root,`frontend/public/figure/${item.gender}-layers`);
 const base=`body/${view}.png`;
 const body=await raster(path.join(dir,base));let raw;
 const itemDirectory=`${item.category}/${item.id}`;
 const rawFile=`assets/wardrobe/${item.gender}/${itemDirectory}/source/${view}.png`;
 try{raw=await raster(path.join(root,rawFile));}catch(error){if(partial&&error.code==='ENOENT')continue;throw error;}
 // Remove non-opaque generated halos, retaining the anti-aliased fabric edge.
 for(let i=3;i<raw.data.data.length;i+=4){const alpha=raw.data.data[i];raw.data.data[i]=alpha<220?0:Math.round(Math.min(1,(alpha-220)/25)*255);}
 raw.ctx.putImageData(raw.data,0,0);
 const source=bounds(raw.data.data),waist=bounds(body.data.data,655,680,340,684);
 const canvas=createCanvas(1024,1536),ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 const start=650,end=item.hem;
 const sourceWaist=bounds(raw.data.data,source.top,source.top+Math.max(12,source.height*.035));
 const scale=(waist.width+(item.fit==='slim'?8:20))/sourceWaist.width;
 const translation=waist.center-sourceWaist.center*scale;
 for(let y=start;y<end;y++){
  const t=(y-start)/(end-start),sy=source.top+t*source.height,sourceRow=bounds(raw.data.data,sy-2,sy+2);
  if(item.fit==='skirt'){
   // Preserve the A-line/pleated silhouette; skirts must remain one panel.
   ctx.drawImage(raw.canvas,0,sy,1024,source.height/(end-start),translation,y,1024*scale,1.25);
  }else{
   let target=bounds(body.data.data,y-2,y+2,340,684);
   const transitionEnd=item.gender==='male'?980:900,transitionStart=750;
   if(y>=transitionStart&&y<transitionEnd){
    const upper=bounds(body.data.data,transitionStart-2,transitionStart+2,340,684),lower=bounds(body.data.data,transitionEnd-2,transitionEnd+2,340,684),u=(y-transitionStart)/(transitionEnd-transitionStart);
    target={...target,width:upper.width*(1-u)+lower.width*u,center:upper.center*(1-u)+lower.center*u};
   }
   if(y>=transitionEnd){
    const neighborRows=[];for(let offset=-20;offset<=20;offset+=5)neighborRows.push(bounds(body.data.data,y+offset,y+offset,340,684));
    target={...target,width:neighborRows.reduce((sum,r)=>sum+r.width,0)/neighborRows.length,center:neighborRows.reduce((sum,r)=>sum+r.center,0)/neighborRows.length};
   }
   const allowance=item.fit==='wide'?20+76*Math.min(1,t*3):item.fit==='slim'?8:22;
   const width=target.width+allowance;
   const sourceLegs=legs(raw.data.data,sy),bodyLegs=legs(body.data.data,y,340,684);
   if((view==='front'||view==='back')&&y>790&&y<end-12&&sourceLegs.length===2&&bodyLegs.length===2){
    const edges=[[target.center-width/2,bodyLegs[0][1]+allowance/4],[bodyLegs[1][0]-allowance/4,target.center+width/2]];
    sourceLegs.forEach(([left,right],index)=>{const [lo,hi]=edges[index];ctx.drawImage(raw.canvas,left,sy,right-left,source.height/(end-start),lo,y,hi-lo,1.25);});
    continue;
   }
   ctx.drawImage(raw.canvas,sourceRow.left,sy,sourceRow.width,source.height/(end-start),target.center-width/2,y,width,1.25);
  }
 }
 const filename=`${itemDirectory}/${view}.png`;
 await mkdir(path.join(dir,itemDirectory),{recursive:true});await writeFile(path.join(dir,filename),canvas.toBuffer('image/png'));
 if(view==='front'){
  const box=bounds(ctx.getImageData(0,0,1024,1536).data),thumbnail=createCanvas(512,512),tc=thumbnail.getContext('2d');
  const ratio=Math.min(460/box.width,460/box.height),w=box.width*ratio,h=box.height*ratio;
  tc.drawImage(canvas,box.left,box.top,box.width,box.height,(512-w)/2,(512-h)/2,w,h);
  await writeFile(path.join(dir,itemDirectory,'thumbnail.png'),thumbnail.toBuffer('image/png'));
 }
 records.push({gender:item.gender,id:item.id,view,rawFile,file:filename,source,start,end,scale,translation});
}
await writeFile(path.join(root,'assets/metadata/bottoms-alignment.json'),JSON.stringify(records,null,2));
console.log(`Prepared ${records.length}/36 bottom sprites.`);
if(process.argv.includes('--register')){
 if(records.length!==36)throw Error('All 36 sprites must be ready before registering.');
 for(const gender of ['male','female']){
  const file=path.join(root,`frontend/public/figure/${gender}-layers/catalog.json`),catalog=JSON.parse(await readFile(file,'utf8'));
  for(const item of items.filter(item=>item.gender===gender)){
   const entry={id:item.id,name:item.name,detail:item.detail,file:item.file,thumbnail:`${item.category}/${item.id}/thumbnail.png`,category:item.category,reference:item.reference,x:0,y:0,sx:1,sy:1,sourcePrepared:true};
   const index=catalog.pants.findIndex(pants=>pants.id===item.id);
   if(index<0)catalog.pants.push(entry);else catalog.pants[index]=entry;
  }
  await writeFile(file,JSON.stringify(catalog,null,2)+'\n');
 }
 console.log('Registered 5 male bottoms and 4 female bottoms in Studio.');
}
