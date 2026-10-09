import test from 'node:test';
import assert from 'node:assert/strict';
import { applyChanges } from '../src/utils/mix.ts';

const config = Object.freeze({
  conceptId: 'concept-1', outfitCode: 'AO_DAI', colorCode: 'RED',
  styleCode: 'TRADITIONAL', eventCode: 'TET',
  accessoryCodes: Object.freeze(['NON_LA', 'FAN']),
});

test('remix applies partial backend changes while preserving concept and event', () => {
  const result = applyChanges(config, {
    styleCode: 'GEN_Z', removeAccessories: ['NON_LA'], addAccessories: ['MINIMAL_BAG'],
  });
  assert.deepEqual(result, {
    conceptId: 'concept-1', outfitCode: 'AO_DAI', colorCode: 'RED',
    styleCode: 'GEN_Z', eventCode: 'TET', accessoryCodes: ['FAN', 'MINIMAL_BAG'],
  });
  assert.deepEqual(config.accessoryCodes, ['NON_LA', 'FAN']);
});

test('repeated cultural suggestions are idempotent and do not duplicate accessories', () => {
  const changes = { colorCode: 'DARK_RED', addAccessories: ['FAN', 'BAG', 'BAG'] };
  const result = applyChanges(config, changes);
  assert.deepEqual(applyChanges(result, changes), result);
  assert.deepEqual(result.accessoryCodes, ['NON_LA', 'FAN', 'BAG']);
});

test('an explanation-only response preserves selections without sharing mutable arrays', () => {
  const result = applyChanges(config, {});
  assert.deepEqual(result, config);
  assert.notEqual(result, config);
  assert.notEqual(result.accessoryCodes, config.accessoryCodes);
});

test('removal of a missing accessory is safe; explicit additions take precedence', () => {
  const result = applyChanges(config, { removeAccessories: ['MISSING', 'FAN'], addAccessories: ['FAN'] });
  assert.deepEqual(result.accessoryCodes, ['NON_LA', 'FAN']);
});
