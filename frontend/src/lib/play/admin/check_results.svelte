<script lang="ts">
    import type { Question } from '$lib/quiz_types';
    import { QuizQuestionType } from '$lib/quiz_types';
  
    export let data;
    export let question: Question;
  
    let quiz_answers = [];
    let answer_correct: boolean[] = [];
  
    for (const i of question.answers) {
      quiz_answers.push(i.answer);
      answer_correct.push(i.right);
    }
  
    let sorted_data = {};
    for (const i of quiz_answers) {
      sorted_data[i] = 0;
    }
  
    const cleanTextAnswer = (answer: string) => {
      return answer.trim().replace(/\s+/g, ' ');
    };
  
    for (const i of data) {
      let answer_found = false;
      for (const j of question.answers) {
        let submitted_answer = cleanTextAnswer(i.answer);
        let correct_answer = cleanTextAnswer(j.answer);
        if (!j.case_sensitive) {
          submitted_answer = submitted_answer.toLowerCase();
          correct_answer = correct_answer.toLowerCase();
        }
        if (submitted_answer === correct_answer) {
          sorted_data[j.answer] += 1;
          answer_found = true;
          break;
        }
      }
      if (!answer_found) {
        sorted_data[i.answer] += 1;
      }
    }
  
    const isCorrect = (answer) => {
      return question.answers.some(a => cleanTextAnswer(a.answer) === cleanTextAnswer(answer) && a.right);
    };
  
    const isIncorrect = (answer) => {
      return question.answers.some(a => cleanTextAnswer(a.answer) === cleanTextAnswer(answer) && !a.right);
    };
  </script>
  
  <div class="flex justify-center w-full px-4">
    <div class="m-auto gap-4 flex flex-col items-center">
      <h2 class="text-2xl font-bold text-center text-white mb-4 dark:text-white">Answers</h2>
      <p class="text-lg md:text-xl lg:text-2xl text-center mb-6 text-white dark:text-gray-300 text-gray-700">{question.question}</p>
      <div class="flex flex-wrap justify-center gap-4 w-full max-w-5xl">
        {#each quiz_answers as answer, i}
          <div class="w-full md:w-1/2 lg:w-1/3 p-4">
            <div class="flex items-center justify-between p-4 border rounded shadow-lg bg-gray-100 dark:bg-gray-800">
              <span class="text-lg dark:text-white">{answer}</span>
              <span class="text-xl font-bold" class:text-green-500={isCorrect(answer)} class:text-red-500={isIncorrect(answer)}>
                {isCorrect(answer) ? '✓' : isIncorrect(answer) ? '✗' : ''}
              </span>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>
  
  
  