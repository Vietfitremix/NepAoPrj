import test from 'node:test';
import assert from 'node:assert/strict';
import { culturalKnowledge } from '../src/utils/culturalKnowledge.ts';

test('all cultural sections and paragraphs survive the API mapping, with their own citations', () => {
  const categories = ['PRESERVATION', 'CONTEXT', 'WEARING', 'MEANING', 'CHARACTERISTICS', 'ORIGIN', 'REGIONAL'];
  const rows = categories.map(category => ({ category, title: category,
    content: `${category} paragraph 1\n\n${category} paragraph 2`,
    sourceName: 'Cultural institution', sourceUrl: 'https://example.org/article' }));
  const result = culturalKnowledge(rows, { name: 'Áo dài' });
  assert.deepEqual(result.sections.map(section => section.category),
    ['ORIGIN', 'CHARACTERISTICS', 'MEANING', 'WEARING', 'CONTEXT', 'PRESERVATION', 'REGIONAL']);
  for (const section of result.sections) {
    assert.equal(section.paragraphs.length, 2);
    assert.equal(section.source.url, 'https://example.org/article');
  }
  assert.equal(result.sources.length, 1);
  assert.equal(result.origin, 'ORIGIN paragraph 1\n\nORIGIN paragraph 2');
});

test('missing content falls back to the outfit and unsafe citations are excluded', () => {
  const result = culturalKnowledge([
    { category: 'MEANING', title: 'Meaning', content: 'Culture', sourceName: null, sourceUrl: 'javascript:alert(1)' },
    { category: 'CONTEXT', title: 'Empty', content: '  ', sourceName: null, sourceUrl: 'https://example.org/empty' }
  ], { name: 'Áo dài', origin: 'Outfit history' });
  assert.equal(result.origin, 'Outfit history');
  assert.equal(result.meaning, 'Culture');
  assert.equal(result.sections.length, 1);
  assert.equal(result.sections[0].source, undefined);
  assert.deepEqual(result.sources, []);
});
