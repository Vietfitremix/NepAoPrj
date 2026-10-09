const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');
const source = path.join(root, 'NepAoPrj');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const records = [];
function walk(dir) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    if (item.name === '.git') continue;
    const file = path.join(dir, item.name);
    if (item.isDirectory()) { walk(file); continue; }
    const relative = path.relative(source, file).replaceAll('\\', '/');
    let target;
    if (relative.startsWith('data/')) target = 'ai-service/' + relative;
    else if (relative.startsWith('frontend/src/assets/figure/')) target = relative.replace('frontend/src/assets/figure/', 'frontend/public/figure/');
    else if (relative.startsWith('tools/')) target = 'frontend/' + relative;
    else if (relative === '.gitignore') target = 'frontend/tools/imported.gitignore';
    else throw new Error('Unmigrated file: ' + relative);
    const original = fs.readFileSync(file);
    let expected = original;
    if (relative.startsWith('tools/') && relative.endsWith('.py')) {
      expected = Buffer.from(original.toString('utf8').replaceAll('frontend/src/assets/figure', 'public/figure')
        .replaceAll('ROOT / "frontend" / "src" / "assets" / "figure"', 'ROOT / "public" / "figure"')
        .replaceAll('ROOT / "data" / "palettes.json"', 'ROOT.parent / "ai-service" / "data" / "palettes.json"')
        .replaceAll('Path(__file__).resolve().parents[1] / "data/patterns.json"', 'Path(__file__).resolve().parents[2] / "ai-service/data/patterns.json"'));
    }
    const actual = fs.readFileSync(path.join(root, target));
    assert.equal(hash(actual), hash(expected), 'Transfer mismatch: ' + target);
    records.push({ source: relative, target, sourceSha256: hash(original), targetSha256: hash(actual) });
  }
}
walk(source);
const garments = JSON.parse(fs.readFileSync(path.join(root, 'ai-service/data/garments.json'), 'utf8'));
for (const garment of garments) for (const gender of garment.genders) for (const angle of ['', '_trai', '_phai', '_sau']) {
  assert.ok(fs.existsSync(path.join(root, 'frontend/public/figure/garment', garment.id + '_' + gender + angle + '.svg')));
}
fs.writeFileSync(path.join(__dirname, 'import-manifest.json'), JSON.stringify({ copiedFiles: records.length, ignored: ['.git (source repository metadata)'], files: records }, null, 2));
console.log('PASS: all ' + records.length + ' source files migrated; hashes and all garment/gender/view combinations verified.');
