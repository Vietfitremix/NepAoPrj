// Run from C:/PROMPTxPTIT: node frontend/tools/import-figure.cjs
// Preserve imported SVG masters and create static variants for the Spring catalog.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const figure = path.join(root, 'frontend/public/figure');
const data = path.join(root, 'ai-service/data');
const generated = path.join(figure, 'rendered');
fs.mkdirSync(generated, { recursive: true });
const colors = { RED: '#D32F2F', DARK_RED: '#8B0000', WHITE: '#FFFFFF', BLUE: '#1976D2', YELLOW: '#FBC02D', BLACK: '#000000', CREAM: '#FFFDD0' };
const garments = JSON.parse(fs.readFileSync(path.join(data, 'garments.json'), 'utf8'));
const read = name => fs.readFileSync(path.join(figure, name + '.svg'), 'utf8');
const colorize = (svg, main, bottom = '#F5F0E1') => svg.replace(/#FF0000/gi, main)
  .replace(/#00FF00/gi, '#E8D9BC').replace(/#0000FF/gi, bottom).replace(/#FF00FF/gi, '#D9A21B');
const nested = svg => svg.replace(/<\?xml[^>]*>/g, '').replace(/<svg\b/, '<svg width="400" height="800"');
const document = layers => '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">' + layers.map(nested).join('\n') + '</svg>\n';
const sql = ["-- Imported NepAoPrj SVG assets. Native cultural rules/cards remain in ai-service/data.",
  "-- No cultural scores or verified sources are invented by this migration."];
for (const garment of garments) {
  const code = garment.id.toUpperCase();
  const bottom = garment.id === 'ao_tu_than' ? 'bottom/vay_nu' : 'bottom/quan_nu';
  const bottomHex = garment.id === 'ao_ba_ba' || garment.id === 'ao_tu_than' || garment.id === 'ao_ngu_than' ? '#1E1E1E' : '#F5F0E1';
  for (const [color, hex] of Object.entries(colors)) {
    const layerName = code + '-' + color + '-layer.svg';
    const lookName = code + '-' + color + '.svg';
    const clothing = document([colorize(read(bottom), hex, bottomHex), colorize(read('garment/' + garment.id + '_nu'), hex, bottomHex)]);
    fs.writeFileSync(path.join(generated, layerName), clothing);
    fs.writeFileSync(path.join(generated, lookName), document([read('body/body_nu'), clothing]));
    for (const [type, url, order] of [['BASE_AVATAR', '/figure/body/body_nu.svg', 0], ['GARMENT', '/figure/rendered/' + layerName, 20]]) {
      sql.push("INSERT INTO outfit_assets(outfit_id,color_id,asset_type,variant_code,image_url,layer_order) SELECT o.id,c.id,'" + type + "','FRONT_NU','" + url + "'," + order + " FROM outfits o CROSS JOIN colors c WHERE o.code='" + code + "' AND c.code='" + color + "';");
    }
  }
  sql.push("UPDATE outfits SET thumbnail_url='/figure/rendered/" + code + "-RED.svg' WHERE code='" + code + "';");
}
const accessories = { NON_LA: ['non_la', 30], FAN: ['quat_giay_nu', 40], MINIMAL_BAG: ['tui_nu', 40], WHITE_SNEAKERS: ['sneaker', 10] };
for (const [code, [file, order]] of Object.entries(accessories)) {
  fs.writeFileSync(path.join(generated, code + '.svg'), colorize(read('accessory/' + file), '#E8D9BC'));
  sql.push("UPDATE accessories SET image_url='/figure/rendered/" + code + ".svg',layer_order=" + order + " WHERE code='" + code + "';");
}
fs.writeFileSync(path.join(__dirname, 'V3__figure_assets.sql'), sql.join('\n') + '\n');
console.log('Created 35 colored garment layers, 35 composed looks, 4 accessory variants and V3 migration.');
