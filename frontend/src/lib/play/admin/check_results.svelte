<script lang="ts">
    import type { Question } from '$lib/quiz_types';
    import { QuizQuestionType } from '$lib/quiz_types';
    import MediaComponent from '$lib/editor/MediaComponent.svelte';
    import { get_foreground_color } from '$lib/helpers';
  
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
    const default_colors = ['#FFA800', '#00A3FF', '#FF1D38', '#00D749'];

    // Function to determine if the color is light or dark
    function isColorLight(color) {
      const hex = color.replace('#', '');
      const r = parseInt(hex.substring(0, 2), 16);
      const g = parseInt(hex.substring(2, 4), 16);
      const b = parseInt(hex.substring(4, 6), 16);
      const brightness = (r * 299 + g * 587 + b * 114) / 1000;
      return brightness > 155; // higher value means the color is light
    }

    // Function to get the appropriate text color
    function getTextColor(backgroundColor) {
      return isColorLight(backgroundColor) ? 'black' : 'white';
    }
  </script>
  
  <div class="flex justify-center w-full px-4">
    <div class="m-auto gap-4 flex flex-col items-center">
      <!-- <h2 class="text-2xl font-bold text-center text-[#003FA7] mb-4 dark:text-[#fff]">Answers</h2> -->
      <p class="text-lg md:text-xl lg:text-2xl text-center mb-6 text-[#003FA7] dark:text-[#fff] ">{question.question}</p>
      <div class="grid grid-rows-2 gap-2 w-full h-full grid-flow-col auto-cols-auto">						
        {#each quiz_answers as answer, i}
          <div 
          class="rounded-lg h-full  flex items-center justify-center disabled:opacity-60 border-4 border-white transition-all my-2"
          style="background-color: {answer.color ?? default_colors[i]}; color: {get_foreground_color(answer.color ?? default_colors[i])}"
          >
            {#if question.ansType !== "IMAGE"}
              <p class="text-lg text-[#00529B] dark:text-[#fff] break-all">{answer}</p>
            {:else}
              <MediaComponent src={answer} css_classes="w-24 h-24" />
            {/if}
            <div class="flex items-center justify-between p-0 ml-2 border rounded shadow-lg bg-gray-100 dark:bg-[#0AEDFE]/20"
               style="width: 20px; height: 20px;">
              <span class="text-xl font-bold" class:text-green-500={isCorrect(answer)} class:text-red-500={isIncorrect(answer)}>
                {isCorrect(answer) ? '✓' : isIncorrect(answer) ? '✗' : ''}
              </span>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>
  
  
  