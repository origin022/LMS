<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { apiFetch, FILE_URL } from '$lib/api';
  import { fly } from 'svelte/transition';

  let loading: boolean = true;
  let latestLectures: any[] = [];

  async function fetchLectures() {
    try {
      loading = true;
      const res = await apiFetch('/lectures/latest');
      if (res.ok) {
        latestLectures = (await res.json()).sort((a: any, b: any) => b.lecture_id - a.lecture_id);
      }
    } catch (e) {
      console.error("Lectures fetch error:", e);
    } finally {
      loading = false;
    }
  }

  onMount(fetchLectures);
</script>

<div class="p-6 md:p-10 max-w-7xl mx-auto space-y-12" dir="rtl">
  {#if loading}
    <div class="flex flex-col justify-center items-center h-[60vh] text-gray-400 gap-4">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      <p class="font-bold text-sm">جاري جلب آخر التحديثات...</p>
    </div>
  {:else}
    <section class="bg-blue-600 rounded-[2.5rem] p-12 text-white shadow-2xl shadow-blue-200 relative overflow-hidden">
      <div class="relative z-10">
        <h2 class="text-4xl font-black mb-4" in:fly={{ y: 20 }}>مرحباً بك في منصة الجاحظ التعليمة</h2>
        <p class="text-blue-100 text-lg max-w-xl leading-relaxed font-medium">
          وَالعَقلُ عِندي هُوَ النورُ الَّذي سَطَعت ... بِهِ الحَقيقَةُ في آفاقِ مَن نَظَرافَلا تَقُل بِما قالَ الرُواتُ بِلا ... عَقْلٍ يُبَيِّنُ هَل ذا قَولُ مَن بَصَرا؟
        </p>
      </div>
      <div class="absolute top-0 left-0 w-64 h-64 bg-white/10 rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl" aria-hidden="true"></div>
    </section>

    <section>
      <div class="flex justify-between items-center mb-8">
          <h3 class="text-2xl font-black text-gray-800">آخر المحاضرات المضافة</h3>
          <button on:click={() => goto('/classrooms')} class="text-blue-600 font-black text-sm hover:underline">
              الذهاب إلى المجالات الدراسية ←
          </button>
      </div>

     <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
  {#each latestLectures as lecture}
    <button 
      on:click={() => goto(`/lecture/${lecture.lecture_id}`)}
      class="bg-white rounded-[2rem] overflow-hidden shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all text-right group flex flex-col"
    >
      <div class="relative h-48 w-full bg-gray-100 overflow-hidden">
        {#if lecture.lecture_image}
          <img 
            src="{FILE_URL}{lecture.lecture_image}" 
            alt={lecture.title}
            class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          />
        {:else}
          <div class="w-full h-full flex items-center justify-center bg-blue-50 text-blue-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        {/if}
        
        <div class="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md text-white text-[10px] px-3 py-1 rounded-lg font-bold">
           {new Date(lecture.created_at).toLocaleDateString('ar-EG', { day: 'numeric', month: 'long', year: 'numeric' })}
        </div>
      </div>

      <div class="p-6 flex flex-col flex-1">
        <h4 class="text-lg font-black text-gray-800 mb-2 group-hover:text-blue-600 transition-colors line-clamp-1">
            {lecture.title}
        </h4>

        <p class="text-gray-500 text-sm line-clamp-2 mb-4 font-medium leading-relaxed">
            {lecture.description || 'لا يوجد وصف متاح لهذه المحاضرة حالياً.'}
        </p>

        <div class="mt-auto pt-4 border-t border-gray-50 flex items-center justify-end">
            <span class="text-blue-600 font-black text-xs flex items-center gap-2">
                عرض المحاضرة 
                <div class="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition-all">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7" />
                    </svg>
                </div>
            </span>
        </div>
      </div>
    </button>
  {/each}
</div>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-2 gap-8 pb-10">
      <div class="bg-orange-50 p-8 rounded-[2rem] border border-orange-100 shadow-sm">
        <h4 class="text-xl font-black text-orange-800 mb-3">محرك "الجاحظ" للتدوين الآلي</h4>
        <p class="text-orange-700/80 leading-relaxed text-sm font-medium">استخرج المعرفة من محاضراتك المرئية فوراً. نستخدم تقنيات Whisper المتقدمة لتحويل الفيديو إلى نصوص دقيقة قابلة للبحث والاقتباس.</p>
      </div>
      <div class="bg-purple-50 p-8 rounded-[2rem] border border-purple-100 shadow-sm">
        <h4 class="text-xl font-black text-purple-800 mb-3">تحدَّ فهمك في لحظتها</h4>
        <p class="text-purple-700/80 leading-relaxed text-sm font-medium">مجرد انتهاء الشرح، يجهز لك النظام اختباراً ذكياً مبنياً على محتوى المحاضرة الفعلي، ليضمن تحويل المشاهدة السلبية إلى تعلم نشط ومثمر.</p>
      </div>
    </section>
  {/if}
</div>