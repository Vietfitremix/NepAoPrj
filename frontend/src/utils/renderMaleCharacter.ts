import { maleLayers, maleWardrobe, getWardrobe } from './maleWardrobe.ts';
import type { MaleSelection, WardrobeCharacter } from './maleWardrobe.ts';
import { renderSourceDirection } from './sourceDirectionRenderer.ts';
import type { CharacterImages } from './sourceDirectionRenderer.ts';

import type { CharacterView } from './characterViews.ts';

export interface FitAnchor { x: number; y: number; dx: number; dy: number; rx: number; ry: number }
interface Point { x: number; y: number }
export interface BodyFitRow { y: number; points: number[][] }

// Each garment has its own measured silhouette. Map it to the avatar at
// shoulders, elbows, waist and cuffs without changing the flowing lower panels.
export function fitBodyPoint(point: Point, rows?: BodyFitRow[]): Point {
  if (!rows?.length || point.y < rows[0].y || point.y > rows[rows.length-1].y) return point;
  const edge=Math.min(point.x,1024-point.x);
  const mapRow=(row: BodyFitRow) => {
    const index=Math.max(1,row.points.findIndex(stop=>stop[0]>=edge));
    const [a,b]=[row.points[index-1],row.points[index]];
    return a[1]+(edge-a[0])/(b[0]-a[0])*(b[1]-a[1]);
  };
  const index=Math.max(1,rows.findIndex(row=>row.y>=point.y));
  const [a,b]=[rows[index-1],rows[index]];
  const weight=(point.y-a.y)/(b.y-a.y);
  const x=mapRow(a)*(1-weight)+mapRow(b)*weight;
  return {x:point.x<=512?x:1024-x,y:point.y};
}

// The original garments float below the shoulders and outside the wrists.
// Fit those regions independently while retaining the collar and skirt position.
export const shirtFit: FitAnchor[] = [
  { x: 304, y: 427, dx: 10, dy: -10, rx: 70, ry: 100 },
  { x: 720, y: 427, dx: -10, dy: -10, rx: 70, ry: 100 },
  { x: 264, y: 581, dx: 28, dy: -14, rx: 72, ry: 115 },
  { x: 760, y: 581, dx: -28, dy: -14, rx: 72, ry: 115 },
  { x: 215, y: 750, dx: 29, dy: -14, rx: 67, ry: 84 },
  { x: 809, y: 750, dx: -29, dy: -14, rx: 67, ry: 84 },
];

const femaleFit: FitAnchor[] = [
  { x: 340, y: 300, dx: 0, dy: 18, rx: 140, ry: 75 },
  { x: 684, y: 300, dx: 0, dy: 18, rx: 140, ry: 75 },
  { x: 512, y: 255, dx: 0, dy: 10, rx: 65, ry: 80 },
  { x: 370, y: 590, dx: 20, dy: -8, rx: 80, ry: 160 },
  { x: 654, y: 590, dx: -20, dy: -8, rx: 80, ry: 160 },
  { x: 244, y: 735, dx: 12, dy: 0, rx: 65, ry: 90 },
  { x: 780, y: 735, dx: -12, dy: 0, rx: 65, ry: 90 },
];

export function fitShirtPoint(point: Point, character: WardrobeCharacter = 'male'): Point {
  let dx = 0, dy = 0, total = 0;
  for (const anchor of shirtFit) {
    const distance = ((point.x - anchor.x) / anchor.rx) ** 2 + ((point.y - anchor.y) / anchor.ry) ** 2;
    const weight = Math.exp(-distance * 1.6);
    dx += anchor.dx * weight;
    dy += anchor.dy * weight;
    total += weight;
  }
  const smooth = (from: number, to: number, value: number) => {
    const t = Math.max(0,Math.min(1,(value-from)/(to-from)));
    return t*t*(3-2*t);
  };
  const shoulderX = Math.min(point.x, maleWardrobe.width-point.x);
  const shoulder = smooth(290,325,shoulderX)*(1-smooth(440,460,shoulderX))*(1-smooth(350,450,point.y));
  const fitted = { x: point.x + dx / Math.max(1, total), y: point.y + dy / Math.max(1, total) - shoulder*35 };
  if (character === 'male') return fitted;
  let femaleX = 0, femaleY = 0, femaleWeight = 0;
  for (const anchor of femaleFit) {
    const distance = ((fitted.x-anchor.x)/anchor.rx)**2+((fitted.y-anchor.y)/anchor.ry)**2;
    const weight = Math.exp(-distance*1.6);
    femaleX += anchor.dx*weight;
    femaleY += anchor.dy*weight;
    femaleWeight += weight;
  }
  return { x:fitted.x+femaleX/Math.max(1,femaleWeight), y:fitted.y+femaleY/Math.max(1,femaleWeight) };
}

function triangle(context: CanvasRenderingContext2D, image: HTMLImageElement | HTMLCanvasElement, source: Point[], target: Point[]) {
  const [s0, s1, s2] = source, [t0, t1, t2] = target;
  const ux = s1.x - s0.x, uy = s1.y - s0.y, vx = s2.x - s0.x, vy = s2.y - s0.y;
  const determinant = ux * vy - uy * vx;
  const a = ((t1.x-t0.x)*vy-(t2.x-t0.x)*uy)/determinant;
  const c = ((t2.x-t0.x)*ux-(t1.x-t0.x)*vx)/determinant;
  const b = ((t1.y-t0.y)*vy-(t2.y-t0.y)*uy)/determinant;
  const d = ((t2.y-t0.y)*ux-(t1.y-t0.y)*vx)/determinant;
  const center = { x: (t0.x+t1.x+t2.x)/3, y: (t0.y+t1.y+t2.y)/3 };
  context.save();
  context.beginPath();
  target.forEach((point, index) => {
    const length = Math.hypot(point.x-center.x, point.y-center.y);
    const x = point.x+(point.x-center.x)/length*2;
    const y = point.y+(point.y-center.y)/length*2;
    if (index === 0) context.moveTo(x,y); else context.lineTo(x,y);
  });
  context.closePath();
  context.clip();
  context.transform(a,b,c,d,t0.x-a*s0.x-c*s0.y,t0.y-b*s0.x-d*s0.y);
  context.drawImage(image,0,0);
  context.restore();
}
export function* fittedShirtMesh(layer: {x: number; y: number; width: number; height: number; mapY?: number[][]; sleeveX?: number; sleeveDx?: number; fitRows?: BodyFitRow[]}, character: WardrobeCharacter = 'male') {
  const stops = (size: number, count: number, extra: number[]) => [...new Set([
    ...Array.from({length:count+1},(_,index)=>index*size/count),
    ...extra.filter(value=>value>0&&value<size),
  ])].sort((a,b)=>a-b);
  const xStops=stops(maleWardrobe.width,32,[290,325,380,420,440,450,460,564,574,584,604,644,699,734].map(x=>(x-layer.x)*maleWardrobe.width/layer.width));
  const yStops=stops(maleWardrobe.height,48,[...[260,300,350,450,740].map(y=>(y-layer.y)*maleWardrobe.height/layer.height),...(layer.mapY?.map(stop=>stop[0])??[])]);
  const sourcePoint = (x: number,y: number) => ({x:xStops[x],y:yStops[y]});
  const targetPoint = (point: Point) => {
    let x=layer.x+point.x*layer.width/1024, y=layer.y+point.y*layer.height/1536;
    if (!layer.mapY) return fitBodyPoint(fitShirtPoint({x,y},character),layer.fitRows);
    const map=layer.mapY;
    const index=Math.max(1,map.findIndex(stop=>stop[0]>=point.y));
    const [a,b]=[map[index-1],map[index]];
    y=a[1]+(point.y-a[0])/(b[0]-a[0])*(b[1]-a[1]);
    if(layer.sleeveX !== undefined && layer.sleeveDx !== undefined){
      const side=x<512?1:-1, edge=Math.min(x,1024-x);
      const center=layer.sleeveX+(735-y)*0.23;
      const sleeveWeight=Math.min(1,Math.max(0,(y-300)/435))*Math.exp(-((Math.max(0,y-735)/160)**2));
      x+=side*layer.sleeveDx*Math.exp(-(((edge-center)/180)**2))*sleeveWeight;
    }
    if(character==='male'){
      const edge=Math.min(x,1024-x);
      y-=25*Math.exp(-(((edge-350)/80)**2))*Math.exp(-(((y-295)/70)**2));
    }
    // Retain coverage of the base torso while fitting the petite waist.
    if(character==='female')x+=(x<512?-1:1)*28*Math.exp(-(((y-590)/155)**2))*Math.exp(-(((Math.abs(x-512)-75)/90)**2));
    return fitBodyPoint({x,y},layer.fitRows);
  };
  for (let row=0;row<yStops.length-1;row++) for (let col=0;col<xStops.length-1;col++) {
    const points=[sourcePoint(col,row),sourcePoint(col+1,row),sourcePoint(col+1,row+1),sourcePoint(col,row+1)];
    for(const indices of [[0,1,2],[0,2,3]]) {
      const source=indices.map(index=>points[index]);
      yield {source,target:source.map(targetPoint)};
    }
  }
}

export function renderFrontLayers(context: CanvasRenderingContext2D, images: CharacterImages, selection: MaleSelection, character: WardrobeCharacter = 'male') {
  context.clearRect(0,0,maleWardrobe.width,maleWardrobe.height);
  context.imageSmoothingEnabled = true;
  context.imageSmoothingQuality = 'high';

  const catalog = getWardrobe(character);
  const shirt = catalog.outfits.find(item => item.id === selection.shirt);
  const shoe = catalog.shoes.find(item=>item.id===selection.shoes);
  for (const layer of maleLayers(selection,character)) {
    const image = images[layer.file];
    if (layer.file === catalog.base && shoe) {
      context.drawImage(image,layer.x,layer.y,layer.width,layer.height);
      const footwear=images[shoe.file];
      for(let side=0;side<2;side++){
        const width=character==='male'?140:102;
        const x=character==='male'?(side===0?307:582):(side===0?366:572);
        const crop=(shoe as typeof shoe & { crops?: number[][] }).crops?.[side];
        if(crop)context.drawImage(footwear,crop[0],crop[1],crop[2],crop[3],x,1300,width,140);
      }
      continue;
    }
    if (!shirt || layer.file !== shirt.file) {
      context.drawImage(image,layer.x,layer.y,layer.width,layer.height);
      continue;
    }
    for (const meshTriangle of fittedShirtMesh(layer,character)) triangle(context,image,meshTriangle.source,meshTriangle.target);
  }
}
export const characterHeadroom = 200;
export function renderMaleCharacter(context: CanvasRenderingContext2D, images: CharacterImages, selection: MaleSelection, character: WardrobeCharacter = 'male', view: CharacterView = 'front') {
  context.clearRect(0, 0, maleWardrobe.width, maleWardrobe.height+characterHeadroom);
  context.imageSmoothingEnabled = true;
  context.imageSmoothingQuality = 'high';
  context.save();context.translate(0,characterHeadroom);
  renderSourceDirection(context, images, selection, character, view);
  context.restore();
}
