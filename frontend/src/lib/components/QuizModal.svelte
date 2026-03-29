<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { apiFetch } from "$lib/api";
  import { X, CheckCircle, XCircle, Award, Trophy, Zap, AlertCircle } from "lucide-svelte";
  import { fly, fade } from "svelte/transition";

  export let quizId: number;
  export let courseId: number;

  const dispatch = createEventDispatcher();

  let loading = true;
  let status = "ongoing"; 
  let question: any = null;
  let options: any[] = [];
  let selectedOptionId: number | null = null;
  let isSubmitting = false;

  let feedback: any = null; 
  let showFeedback = false;

  let rankData: any = null;

  async function fetchNextQuestion() {
    loading = true;
    showFeedback = false;
    selectedOptionId = null;
    feedback = null;
    try {
      const res = await apiFetch(`/next-question/${quizId}`);
      if (res.ok) {
        const data = await res.json();
        status = data.status || "ongoing";
        if (status === "completed") {
          await fetchRank();
        } else {
          question = data;
          options = data.options || [];
        }
      } else {
        const err = await res.json();
        console.error("Failed to fetch next question:", err);
      }
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function fetchRank() {
    try {
      const res = await apiFetch(`/course-rank/${courseId}`);
      if (res.ok) {
        rankData = await res.json();
      }
    } catch(e) {
      console.error(e);
    }
  }

  async function submitAnswer() {
    if (!selectedOptionId || isSubmitting) return;
    isSubmitting = true;
    try {
      const res = await apiFetch("/submit-answer", {
        method: "POST",
        body: JSON.stringify({
          quiz_id: quizId,
          question_id: question.question_id,
          answer_id: selectedOptionId
        })
      });
      if (res.ok) {
        const data = await res.json();
        feedback = {
          isCorrect: data.is_correct,
          points: data.points_earned,
          streak: data.current_streak,
          nextDiff: data.next_difficulty,
          msg: data.message,
          correctId: data.correct_answer_id
        };
        showFeedback = true;
      }
    } catch(e) {
      console.error(e);
    } finally {
      isSubmitting = false;
    }
  }

  onMount(() => {
    fetchNextQuestion();
  });

  function close() {
    dispatch("close");
  }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" dir="rtl">
  <!-- Backdrop -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" transition:fade={{ duration: 200 }} on:click={close}></div>

  <!-- Modal content -->
  <div 
    class="relative w-full max-w-2xl bg-white rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
    transition:fly={{ y: 20, duration: 300 }}
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-6 border-b border-slate-100 bg-white z-10">
      <h2 class="text-2xl font-black text-slate-800">
        اختبار المحاضرة
      </h2>
      <button 
        on:click={close}
        class="w-10 h-10 rounded-full bg-slate-100 text-slate-500 hover:bg-red-50 hover:text-red-500 flex items-center justify-center transition-all"
      >
        <X size={20} />
      </button>
    </div>

    <!-- Body -->
    <div class="p-6 sm:p-10 overflow-y-auto custom-scrollbar flex-1 relative bg-slate-50/50">
      {#if loading}
        <div class="flex flex-col items-center justify-center py-20 gap-4 text-indigo-500" in:fade>
          <div class="w-12 h-12 border-4 border-indigo-200 border-t-indigo-500 rounded-full animate-spin"></div>
          <p class="font-bold animate-pulse">جاري التحميل...</p>
        </div>
      {:else if status === "completed"}
        <div class="text-center py-10 space-y-6" in:fade>
          <div class="w-24 h-24 bg-amber-100 text-amber-500 rounded-[2rem] flex items-center justify-center mx-auto mb-6 shadow-xl shadow-amber-500/20 transform rotate-12">
            <Trophy size={48} />
          </div>
          <h3 class="text-3xl font-black text-slate-800">أحسنت! أتممت الاختبار</h3>
          
          {#if rankData}
            <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm max-w-sm mx-auto space-y-4">
              <div class="flex items-center justify-between p-4 bg-indigo-50 rounded-2xl text-indigo-700 font-bold">
                <span class="flex items-center gap-2"><Award size={20} /> مجموع النقاط</span>
                <span class="text-2xl font-black">{rankData.student_score}</span>
              </div>
              <div class="flex items-center justify-between p-4 bg-emerald-50 rounded-2xl text-emerald-700 font-bold">
                <span class="flex items-center gap-2"><Trophy size={20} /> ترتيبك في الكورس</span>
                <span class="text-2xl font-black">#{rankData.rank}</span>
              </div>
              <p class="text-sm font-bold text-slate-500 mt-4">{rankData.message}</p>
            </div>
          {/if}

          <button 
            on:click={close}
            class="mt-8 px-10 py-4 bg-indigo-600 text-white rounded-2xl font-black text-lg shadow-xl shadow-indigo-600/20 hover:bg-indigo-700 transition-all active:scale-95"
          >
            إغلاق ومتابعة
          </button>
        </div>
      {:else if question}
        <div class="space-y-8" in:fade>
          <!-- Metadata (Difficulty) -->
          <div class="flex items-center justify-between text-sm font-bold">
            <span class="px-3 py-1 bg-white border border-slate-200 rounded-lg text-slate-500 flex items-center gap-2 shadow-sm">
              مستوى الصعوبة: 
              <span class={question.difficulty === 1 ? 'text-emerald-500' : question.difficulty === 2 ? 'text-amber-500' : 'text-rose-500'}>
                {question.difficulty === 1 ? 'سهل' : question.difficulty === 2 ? 'متوسط' : 'صعب'}
              </span>
            </span>
          </div>

          <!-- Question Text -->
          <h3 class="text-2xl font-black text-slate-800 leading-snug">
            {question.question_text}
          </h3>

          <!-- Options -->
          <div class="grid gap-4">
            {#each options as option (option.option_id)}
              {@const isSelected = selectedOptionId === option.option_id}
              {@const isCorrectOpt = showFeedback && option.option_id === feedback.correctId}
              {@const isWrongSelected = showFeedback && isSelected && !feedback.isCorrect}
              
              <button
                disabled={showFeedback}
                on:click={() => selectedOptionId = option.option_id}
                class="relative text-right w-full p-5 rounded-2xl border-2 transition-all font-bold text-lg
                  {showFeedback 
                    ? isCorrectOpt 
                      ? 'bg-emerald-50 border-emerald-500 text-emerald-800'
                      : isWrongSelected
                        ? 'bg-rose-50 border-rose-500 text-rose-800'
                        : 'bg-white border-slate-100 text-slate-400 opacity-50'
                    : isSelected 
                      ? 'bg-indigo-50 border-indigo-500 text-indigo-700 shadow-md shadow-indigo-500/10 scale-[1.02]' 
                      : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300 hover:bg-slate-50'
                  }
                "
              >
                {option.option_text}

                {#if showFeedback}
                  <div class="absolute left-5 top-1/2 -translate-y-1/2">
                    {#if isCorrectOpt}
                      <CheckCircle class="text-emerald-500" size={24} />
                    {:else if isWrongSelected}
                      <XCircle class="text-rose-500" size={24} />
                    {/if}
                  </div>
                {/if}
              </button>
            {/each}
          </div>

          <!-- Actions & Feedback -->
          <div class="pt-6">
            {#if !showFeedback}
              <button 
                disabled={!selectedOptionId || isSubmitting}
                on:click={submitAnswer}
                class="w-full py-4 rounded-2xl font-black text-lg text-white transition-all shadow-xl active:scale-95
                  {!selectedOptionId 
                    ? 'bg-slate-300 shadow-none' 
                    : 'bg-indigo-600 shadow-indigo-600/30 hover:bg-indigo-700'}"
              >
                {isSubmitting ? 'جاري الإرسال...' : 'تأكيد الإجابة'}
              </button>
            {:else}
              <div 
                in:fly={{ y: 20 }}
                class="w-full p-6 rounded-3xl {feedback.isCorrect ? 'bg-emerald-600' : 'bg-rose-600'} text-white shadow-2xl relative overflow-hidden"
              >
                <!-- Decorative background icon -->
                <div class="absolute -left-4 -bottom-4 opacity-10">
                  {#if feedback.isCorrect}
                    <CheckCircle size={120} />
                  {:else}
                    <XCircle size={120} />
                  {/if}
                </div>
                
                <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div>
                    <h4 class="text-2xl font-black mb-2 flex items-center gap-2">
                      {#if feedback.isCorrect}
                        إجابة صحيحة! 🎉
                      {:else}
                        إجابة خاطئة
                      {/if}
                    </h4>
                    <div class="flex flex-wrap gap-4 text-sm font-bold opacity-90">
                      {#if feedback.points > 0}
                        <span class="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg">
                          <Award size={16} /> +{feedback.points} نقطة
                        </span>
                      {/if}
                      {#if feedback.streak > 1}
                        <span class="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg">
                          <Zap size={16} class="fill-current text-amber-300" /> سلسلة متتالية: {feedback.streak}
                        </span>
                      {/if}
                    </div>
                  </div>
                  
                  <button 
                    on:click={fetchNextQuestion}
                    class="bg-white text-slate-800 px-8 py-3 rounded-xl font-black shadow-lg hover:scale-105 transition-transform whitespace-nowrap"
                  >
                    السؤال التالي ←
                  </button>
                </div>
              </div>
            {/if}
          </div>
        </div>
      {:else}
        <div class="py-20 text-center text-slate-500">
          <AlertCircle size={48} class="mx-auto mb-4 opacity-50" />
          <p class="font-bold">حدث خطأ في تحميل السؤال. يرجى المحاولة لاحقاً.</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  :global(.custom-scrollbar::-webkit-scrollbar) { width: 6px; }
  :global(.custom-scrollbar::-webkit-scrollbar-track) { background: transparent; }
  :global(.custom-scrollbar::-webkit-scrollbar-thumb) {
    background: #cbd5e1;
    border-radius: 10px;
  }
</style>
