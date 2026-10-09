const ts = require('../../frontend/node_modules/typescript');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const config = ts.readConfigFile('frontend/tsconfig.json', ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, path.resolve('frontend'));
const host = ts.createCompilerHost(parsed.options);
const read = host.readFile;
host.readFile = file => {
  const preview = path.join('ai-service/integration/preview', path.relative(process.cwd(), file));
  return fs.existsSync(preview) ? fs.readFileSync(preview, 'utf8') : read(file);
};
const exists = host.fileExists;
host.fileExists = file => exists(file) || exists(path.join('ai-service/integration/preview', path.relative(process.cwd(), file)));
const program = ts.createProgram(parsed.fileNames, { ...parsed.options, noEmit: true }, host);
const diagnostics = ts.getPreEmitDiagnostics(program);
if (diagnostics.length) {
  console.log(ts.formatDiagnosticsWithColorAndContext(diagnostics, {
    getCurrentDirectory: () => process.cwd(), getCanonicalFileName: f => f, getNewLine: () => '\n'
  }));
  process.exitCode = 1;
} else console.log('PASS: patched frontend typechecks without modifying protected files.');
const source = fs.readFileSync('ai-service/integration/preview/frontend/src/services/backendContract.ts', 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText;
const exported = {};
new Function('exports', compiled)(exported);
const mix = { conceptId: 'ui-only', outfitCode: 'AO_DAI', colorCode: 'RED', styleCode: 'GEN_Z', eventCode: 'TET', accessoryCodes: ['NON_LA'] };
assert.deepEqual(exported.selection(mix), { outfitCode: 'AO_DAI', colorCode: 'RED', styleCode: 'GEN_Z', eventCode: 'TET', accessories: ['NON_LA'] });
const detail = { outfit: { code: 'AO_DAI', name: 'Áo dài', thumbnailUrl: null },
  colors: [{ code: 'RED', name: 'Đỏ', hexCode: '#D32F2F' }], assets: [], accessories: [] };
const refs = { outfits: [detail], colors: detail.colors, styles: [{ code: 'GEN_Z', name: 'Gen Z' }], events: [{ code: 'TET', name: 'Tết' }] };
assert.equal(exported.outfitView(detail, refs.styles).colors[0].hex, '#D32F2F');
assert.equal(exported.outfitView(detail, refs.styles).baseAvatarUrl, '');
const saved = exported.lookView({ id: 7, ...exported.selection(mix), styleMatchScore: null, culturalScore: null, colorHarmonyScore: null, previewImageUrl: null }, refs);
assert.equal(saved.id, '7');
assert.equal(saved.outfitName, 'Áo dài');
assert.equal(saved.culturalScore, null);
assert.deepEqual(saved.config.accessoryCodes, ['NON_LA']);
console.log('PASS: selection JSON, outfit mapping, saved-look IDs and null scores.');
