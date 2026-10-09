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
  for(const question of stylistQuiz){
    const labels=question.options.filter(o=>[].concat(answers[question.id].value).includes(o.value)).map(o=>o.label);
    for(const label of labels)assert.ok(context.includes(label),question.id+': '+label);
  }
  // Câu hỏi "(có thể bỏ qua)" từng bị hiểu nhầm là "bỏ màu": lời nhắn không được chứa các từ phủ định của câu hỏi.
  assert.ok(!/bỏ qua|chọn tối đa/.test(context));
  assert.ok(context.includes('Màu ưa thích: '));
  assert.ok(context.includes('Chụp tại sân trường'));
  const preferences=quizPreferences(answers,'Gọn nhẹ','Hanoi',{temperature:25});
  assert.equal(preferences.character,'male');
  assert.equal(preferences.eventCode,'GRADUATION');assert.equal(preferences.styleCode,'MINIMAL');
  assert.equal(preferences.colorCode,'RED');
  const green=quizPreferences({colors:{value:['#39705b','#765a94']}},'','Hanoi',{temperature:25});
  assert.equal(green.colorCode,'GREEN');
  assert.equal(quizPreferences({colors:{value:['#de91aa']}},'','Hanoi',{temperature:25}).colorCode,'PINK');
  assert.equal(quizPreferences({colors:{value:['#876044']}},'','Hanoi',{temperature:25}).colorCode,'BROWN');assert.deepEqual(preferences.answers,answers);
});
