import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { stylistQuiz, quizContext, quizPreferences } from '../src/utils/stylistQuiz.ts';

test('context includes all eight NepAo questions in their original order', () => {
  const source=JSON.parse(readFileSync(new URL('../../ai-service/data/quiz.json',import.meta.url),'utf8'));
  assert.deepEqual(stylistQuiz.map(q=>[q.id,q.question,q.type]),source.map(q=>[q.id,q.question,q.type]));
  assert.equal(stylistQuiz.length,8);
});

test('all answers and free text reach the recommendation context, including male gender', () => {
  const answers=Object.fromEntries(stylistQuiz.map(q=>[q.id,{value:q.type==='multi'?q.options.slice(0,3).map(o=>o.value):q.options[0].value,text:q.id==='setting'?'Chụp tại sân trường':''}]));
  answers.occasion.value='ky_yeu';answers.gender.value='nam';answers.style.value='toi_gian';
  const context=quizContext(answers);
  for(const question of stylistQuiz)assert.ok(context.includes(question.question));
  assert.ok(context.includes('Chụp tại sân trường'));
  const preferences=quizPreferences(answers,'Gọn nhẹ','Hanoi',{temperature:25});
  assert.equal(preferences.character,'male');
  assert.equal(preferences.eventCode,'GRADUATION');assert.equal(preferences.styleCode,'MINIMAL');
  assert.equal(preferences.colorCode,'RED');assert.deepEqual(preferences.answers,answers);
});
