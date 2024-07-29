<script lang="ts">
    import type { Question } from '$lib/quiz_types';
  
    export let data;
    export let question: Question;
  
    const cleanTextAnswer = (answer: string) => {
      return answer.trim().replace(/\s+/g, ' ');
    };
  
    const isCorrectRange = (answer: string) => {
      const value = parseFloat(answer);
      return (
        value >= parseFloat(question.answers.min_correct) &&
        value <= parseFloat(question.answers.max_correct)
      );
    };
  </script>
  
  <div class="flex justify-center w-full px-4">
    <div class="m-auto gap-4 flex flex-col items-center">
      <h2 class="text-2xl font-bold text-center text-white mb-4 dark:text-white">Range Results</h2>
      <p class="text-lg md:text-xl lg:text-2xl text-center mb-6 text-white dark:text-gray-300 text-gray-700">{question.question}</p>
      <div class="flex flex-wrap justify-center gap-4 w-full max-w-5xl">
        {#each data as item, i}
          <div class="w-full md:w-1/2 lg:w-1/2 p-4">
            <div class="flex items-center justify-between p-4 border rounded shadow-lg gap-1 bg-gray-100 dark:bg-gray-800">
              <span class="text-lg dark:text-white">{item.answer}</span>
              <span class="text-xl font-bold" class:text-green-500={isCorrectRange(item.answer)} class:text-red-500={!isCorrectRange(item.answer)}>
                {isCorrectRange(item.answer) ? '✓' : '✗'}
              </span>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>
  