import test from 'node:test';
import assert from 'node:assert/strict';
import { recommendationRequest, resolvedPreferences, contextualAnswers } from '../src/utils/recommendationContext.ts';
import { reviewContext } from '../src/utils/outfitContext.ts';

const preferences = { prompt: 'Mình là nam, chụp kỷ yếu ngoài trời, thích tối giản', city: 'Hanoi',
  eventCode: 'TET', styleCode: 'GEN_Z', colorCode: 'ANY', character: 'female',
  weather: { city: 'Hanoi', temperature: 26.05, condition: 'CLEAR', humidity: 70 }, answers: {} };

test('shortcut prompt is sent without invented occasion, style or gender', () => {
  const request = recommendationRequest(preferences);
  assert.equal(request.prompt, preferences.prompt);
  assert.deepEqual(request.context, {});
  assert.equal(request.character, undefined);
  assert.ok(!request.prompt.includes('Tết') && !request.prompt.includes('Gen Z'));
});

test('explicit quiz choices and free text both reach the AI', () => {
  const request = recommendationRequest({ ...preferences, character: 'male', answers: {
    occasion: { value: 'dam_cuoi' }, gender: { value: 'nam' },
    setting: { value: 'trong_nha', text: 'nhà hàng bên sông' }, colors: { value: ['#39705b', '#765a94'] } } });
  assert.equal(request.context.occasion, 'dam_cuoi');
  assert.equal(request.context.setting, 'trong_nha');
  assert.equal(request.character, 'male');
  assert.ok(request.prompt.includes('nhà hàng bên sông'));
  assert.ok(request.prompt.includes('Xanh lá') && request.prompt.includes('Tím'));
});

test('interpreted context persists into mix studio scoring and resolved preferences', () => {
  const recommendation = { eventCode: 'GRADUATION', styleCode: 'MINIMAL', character: 'male',
    context: { weather: 'lanh', setting: 'ngoai_troi', role: 'nhom', timeOfDay: 'ban_ngay' },
    weather: { ...preferences.weather, temperature: 25 } };
  const result = resolvedPreferences(preferences, recommendation);
  assert.equal(result.eventCode, 'GRADUATION');
  assert.equal(result.styleCode, 'MINIMAL');
  assert.equal(result.character, 'male');
  assert.equal(result.weather.temperature, 25);
  assert.deepEqual(reviewContext(contextualAnswers(result, recommendation)), { weather: 'lanh', setting: 'ngoai_troi', timeOfDay: 'ban_ngay', role: 'nhom' });
  assert.deepEqual(result.answers, {});
  assert.deepEqual(recommendationRequest(result).context, {});
  const explicit = contextualAnswers({ ...preferences, answers: { setting: { value: 'trong_nha' } } },
    { context: { setting: 'ngoai_troi' } });
  assert.equal(explicit.setting.value, 'trong_nha');
});
