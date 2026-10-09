import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {getWardrobe,selectedWardrobeItems} from '../frontend/src/utils/maleWardrobe.ts';
import {withHandForeground} from '../frontend/src/utils/sourceDirectionRenderer.ts';
import {renderMaleCharacter,characterHeadroom} from '../frontend/src/utils/renderMaleCharacter.ts';
import {patternFile} from '../frontend/src/utils/wardrobeStyles.ts';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url)),{createCanvas,loadImage}=require('@napi-rs/canvas');
globalThis.document={createElement:()=>createCanvas(1,1)};
const views=['front','left','right','back'],height=1536+characterHeadroom;
const scenes=[
 {gender:'female',selection:{shirt:'jade',pants:'long-black',shoes:'hai-theu',accessories:{headwear:'non-quai-thao',hairAccessory:'hoa-cai-toc',necklace:'kieng-bac',earrings:'bong-tai',bracelet:'vong-tay',bag:'tui-coi',fan:'quat-giay'},styles:{shirt:{color:'#b52838',pattern:'canh-dao-xuan'},pants:{color:'#24242a',pattern:null}}}},
 {gender:'male',selection:{shirt:'navy',pants:'ivory',shoes:'giay-ta',accessories:{headwear:'khan-xep',necklace:'kieng-bac',bracelet:'vong-tay',fan:'quat-giay'},styles:{shirt:{color:'#32679e',pattern:'phuong-hoang'},pants:{color:'#24242a',pattern:null},shoes:{color:'#876044',pattern:null}}}},
 {gender:'female',selection:{shirt:'ba-ba',pants:'skirt-short-navy',shoes:'guoc',accessories:{headwear:'non-la',earrings:'bong-tai',bracelet:'vong-tay',bag:'tui-coi'},styles:{shirt:{color:'#eee9dc',pattern:'hoa-cuc'},pants:{color:'#de91aa',pattern:'hoa-dao-nho'}}}},
 {gender:'female',selection:{shirt:'ba-ba',pants:'long-black',shoes:'dep-crocs',accessories:{headwear:'mu-luoi-trai',headphones:'tai-nghe',glasses:'kinh-ram',backpack:'ba-lo',gloves:'gang-tay-ho-ngon',hipChain:'day-xich-hong'},styles:{shirt:{color:'#32679e',pattern:'ke-soc'}}}},
 {gender:'male',selection:{shirt:'ba-ba',pants:'cropped-olive',shoes:'dep-le',accessories:{headwear:'mu-cao-boi',glasses:'kinh-ram',bag:'tui-deo-cheo',gloves:'gang-tay-ho-ngon',bagCharm:'moc-khoa-bong'},styles:{shirt:{color:'#876044',pattern:null}}}},
 {gender:'female',selection:{shirt:'ba-ba',pants:'skirt-short-navy',shoes:'giay-bup-be',accessories:{bag:'tui-xach-thoi-trang',bagCharm:'moc-khoa-bong',earrings:'bong-tai',bracelet:'vong-tay'},styles:{shirt:{color:'#de91aa',pattern:'hoa-dao-nho'},pants:{color:'#24242a',pattern:null}}}},
];
const sheet=createCanvas(1280,scenes.length*565),ctx=sheet.getContext('2d');ctx.fillStyle='#e8e4d8';ctx.fillRect(0,0,sheet.width,sheet.height);
for(const [row,{gender,selection}] of scenes.entries()){
 globalThis.gc?.();
 const images={},catalog=getWardrobe(gender),files=new Set([...views.map(view=>'body/'+view+'.png'),...selectedWardrobeItems(selection,gender).flatMap(item=>views.map(view=>item.file.replace('front.png',view+'.png')))]);
 for(const file of files)images[file]=await loadImage(await readFile(path.join(root,`frontend/public/figure/${gender}-layers`,file)));
 for(const style of Object.values(selection.styles)){const file=patternFile(style);if(file)images[file]=await loadImage(await readFile(path.join(root,'frontend/public/figure',file)));}
 const fitted=withHandForeground(images,gender);
 for(const [column,view] of views.entries()){const canvas=createCanvas(catalog.width,height),c=canvas.getContext('2d');renderMaleCharacter(c,fitted,selection,gender,view);ctx.drawImage(canvas,column*320,row*565+20,320,545);ctx.fillStyle='#354830';ctx.font='14px sans-serif';ctx.fillText(gender+' / '+view,column*320+8,row*565+18);}
}
await writeFile(path.join(root,'assets/previews/styled-outfits.png'),sheet.toBuffer('image/png'));
