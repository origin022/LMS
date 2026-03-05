<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { apiFetch } from '$lib/api';
  import { fly } from 'svelte/transition';

  let loading: boolean = true;
  let latestLectures: any[] = [];

  async function fetchLectures() {
    try {
      loading = true;
      const res = await apiFetch('/lectures/latest');
      if (res.ok) {
        latestLectures = await res.json();
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
        <h2 class="text-4xl font-black mb-4" in:fly={{ y: 20 }}>مرحباً بك في المنصة الذكية</h2>
        <p class="text-blue-100 text-lg max-w-xl leading-relaxed font-medium">
          استمتع بتجربة تعلم فريدة مع تقنيات الذكاء الاصطناعي لتحويل المحاضرات واختبار مستواك الدراسي.
        </p>
      </div>
      <div class="absolute top-0 left-0 w-64 h-64 bg-white/10 rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl" aria-hidden="true"></div>
    </section>

    <section>
      <div class="flex justify-between items-center mb-8">
          <h3 class="text-2xl font-black text-gray-800">آخر المحاضرات المضافة</h3>
          <button on:click={() => goto('/classrooms')} class="text-blue-600 font-black text-sm hover:underline">
              الذهاب إلى الكلاسات ←
          </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {#each latestLectures as lecture}
          <button 
            on:click={() => goto(`/lectures/${lecture.lecture_id}`)}
            class="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all text-right group relative"
          >
            <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h4 class="text-lg font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">{lecture.title}</h4>
            <p class="text-gray-500 text-sm line-clamp-2 mb-4">{lecture.description || 'لا يوجد وصف متاح.'}</p>
            <div class="flex justify-between items-center text-[10px] text-gray-400 font-bold border-t pt-4">
               <span>{new Date(lecture.created_at).toLocaleDateString('ar-EG')}</span>
               <span class="text-blue-500">عرض المحاضرة ←</span>
            </div>
          </button>
        {:else}
          <div class="col-span-full py-20 text-center bg-white rounded-3xl border-2 border-dashed border-gray-100 text-gray-400 font-bold">
            لا توجد محاضرات منشورة حالياً.
          </div>
        {/each}
      </div>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-2 gap-8 pb-10">
      <div class="bg-orange-50 p-8 rounded-[2rem] border border-orange-100 shadow-sm">
        <h4 class="text-xl font-black text-orange-800 mb-3">التفريغ النصي الذكي</h4>
        <p class="text-orange-700/80 leading-relaxed text-sm font-medium">نستخدم نماذج AI متطورة لتحويل محاضراتك الفيديو إلى نصوص قابلة للقراءة والبحث.</p>
      </div>
      <div class="bg-purple-50 p-8 rounded-[2rem] border border-purple-100 shadow-sm">
        <h4 class="text-xl font-black text-purple-800 mb-3">اختبارات AI الفورية</h4>
        <p class="text-purple-700/80 leading-relaxed text-sm font-medium">بمجرد توفر المحاضرة، يمكنك توليد اختبارات تقييمية لمستوى فهمك بضغطة زر.</p>
      </div>
    </section>
  {/if}
</div>