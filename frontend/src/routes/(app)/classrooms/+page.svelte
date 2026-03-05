<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { apiFetch } from '$lib/api';

  interface Classroom {
    class_id: number;
    class_name: string;
  }

  let classrooms: Classroom[] = [];
  let searchQuery: string = '';
  let loading: boolean = true;

  $: filteredClassrooms = classrooms.filter(c => 
    c.class_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  async function loadClassrooms(): Promise<void> {
    try {
      loading = true;
      const res = await apiFetch('/classrooms');
      if (res.ok) {
        classrooms = await res.json();
      }
    } catch (err) {
      console.error("Load Classrooms Error:", err);
    } finally {
      loading = false;
    }
  }

  onMount(loadClassrooms);
</script>

<div class="p-8 max-w-7xl mx-auto" dir="rtl">
  {#if loading}
    <div class="flex flex-col justify-center items-center h-[60vh] gap-4 text-gray-400">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="text-sm font-medium">جاري تحميل الكلاسات...</p>
    </div>
  {:else}
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
      <div>
        <h2 class="text-3xl font-black text-gray-800 tracking-tight">المحتوى الدراسي المتاح</h2>
        <p class="text-gray-500 text-sm mt-1 font-medium">تصفح الكورسات والمحاضرات المنشورة</p>
      </div>

      <div class="relative w-full md:w-80 group">
        <div class="absolute inset-y-0 right-4 flex items-center pointer-events-none text-gray-400 group-focus-within:text-blue-600 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input 
          type="text" 
          bind:value={searchQuery}
          placeholder="ابحث عن كلاس محدد..."
          class="w-full pr-12 pl-4 py-3.5 bg-white border border-gray-100 rounded-2xl shadow-sm focus:ring-4 focus:ring-blue-50 focus:border-blue-200 outline-none transition-all text-sm font-bold"
        />
      </div>
    </div>

    {#if filteredClassrooms.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {#each filteredClassrooms as classroom}
          <button 
            on:click={() => goto(`/courses/${classroom.class_id}`)} 
            class="group bg-white rounded-[2rem] p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all text-right relative overflow-hidden"
          >
            <div class="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-6 text-2xl font-black group-hover:bg-blue-600 group-hover:text-white transition-all transform group-hover:rotate-6">
              {classroom.class_name?.charAt(0)}
            </div>
            <h3 class="text-xl font-bold text-gray-800 mb-2">{classroom.class_name}</h3>
            <div class="mt-4 pt-4 border-t border-gray-50 text-blue-600 text-xs font-black flex items-center gap-2">
              استكشف المحتوى 
              <span class="group-hover:translate-x-[-4px] transition-transform">←</span>
            </div>
          </button>
        {/each}
      </div>
    {:else}
      <div class="py-20 text-center bg-white rounded-[2.5rem] border-2 border-dashed border-gray-100 text-gray-400 font-bold">
        لا توجد نتائج تطابق بحثك حالياً.
      </div>
    {/if}
  {/if}
</div>