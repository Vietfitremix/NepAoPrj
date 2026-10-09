import test from 'node:test';
import assert from 'node:assert/strict';
import { reviewContext } from '../src/utils/outfitContext.ts';

test('same supported quiz context reaches score, review and remix', () => {
  const answer = value => ({ questionId: 'unused', value });
  assert.deepEqual(reviewContext({weather:answer('mua'),setting:answer('ngoai_troi'),role:answer('be_trap'),timeOfDay:answer('buoi_toi')}),
    {weather:'mua',setting:'ngoai_troi',timeOfDay:'buoi_toi',role:'be_trap'});
});
test('missing, stale and multi-select context answers remain unknown', () => {
  assert.deepEqual(reviewContext(), {});
  assert.deepEqual(reviewContext({weather:{value:'unknown'},role:{value:['khach']},setting:{value:''}}), {});
});
