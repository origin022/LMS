<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { apiFetch, FILE_URL } from "$lib/api";

  interface Classroom {
    class_id: number;
    class_name: string;
    class_image?: string;
    department_id?: number;
  }

  interface Department {
    department_id: number;
    name: string;
  }

  let classrooms: Classroom[] = [];
  let departments: Department[] = [];
  let searchQuery: string = "";
  let selectedDeptId: number | null = null;
  let loading: boolean = true;

  $: filteredClassrooms = classrooms.filter((c) => {
    const matchesSearch = c.class_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDept = selectedDeptId ? c.department_id === selectedDeptId : true;
    return matchesSearch && matchesDept;
  });

  async function loadData(): Promise<void> {
    try {
      loading = true;
      const [cRes, dRes] = await Promise.all([
        apiFetch("/classrooms"),
        apiFetch("/admin/departments") // Note: using admin endpoint but public access might need separate endpoint later
      ]);
      
      if (cRes.ok) classrooms = await cRes.json();
      if (dRes.ok) departments = await dRes.json();
    } catch (err) {
      console.error("Load Data Error:", err);
    } finally {
      loading = false;
    }
  }

  onMount(loadData);
</script>

<div class="p-8 max-w-7xl mx-auto" dir="rtl">
  {#if loading}
    <div
      class="flex flex-col justify-center items-center h-[60vh] gap-4 text-gray-400"
    >
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
      ></div>
      <p class="text-sm font-medium">جاري تحميل المجالات...</p>
    </div>
  {:else}
    <div
      class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10"
    >
      <div>
        <h2 class="text-3xl font-black text-gray-800 tracking-tight">
          المحتوى الدراسي المتاح
        </h2>
        <p class="text-gray-500 text-sm mt-1 font-medium">
          تصفح الكورسات والمحاضرات المنشورة
        </p>
      </div>

      <div class="relative w-full md:w-80 group">
        <div
          class="absolute inset-y-0 right-4 flex items-center pointer-events-none text-gray-400 group-focus-within:text-blue-600 transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="ابحث عن مجال دراسي محدد..."
          class="w-full pr-12 pl-4 py-3.5 bg-white border border-gray-100 rounded-2xl shadow-sm focus:ring-4 focus:ring-blue-50 focus:border-blue-200 outline-none transition-all text-sm font-bold"
        />
      </div>
    </div>

    <div class="flex gap-2 overflow-x-auto no-scrollbar pb-4 mb-8">
      <button
        on:click={() => (selectedDeptId = null)}
        class="px-6 py-2.5 rounded-xl text-xs font-black transition-all shadow-sm {selectedDeptId === null
          ? 'bg-blue-600 text-white shadow-blue-200'
          : 'bg-white text-slate-400 hover:bg-slate-50'}"
      >
        الكل
      </button>
      {#each departments as dept}
        <button
          on:click={() => (selectedDeptId = dept.department_id)}
          class="px-6 py-2.5 rounded-xl text-xs font-black transition-all shadow-sm {selectedDeptId === dept.department_id
            ? 'bg-blue-600 text-white shadow-blue-200'
            : 'bg-white text-slate-400 hover:bg-slate-50'}"
        >
          {dept.name}
        </button>
      {/each}
    </div>

    {#if filteredClassrooms.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {#each filteredClassrooms as classroom}
          <button
            on:click={() => goto(`/courses?class_id=${classroom.class_id}`)}
            class="group bg-white rounded-2xl shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all text-right relative overflow-hidden flex flex-col border border-gray-100 p-0"
          >
            {#if classroom.class_image}
              <div class="h-44 w-full bg-cover bg-center transition-transform duration-500 group-hover:scale-105" style="background-image: url('{FILE_URL}{classroom.class_image}')"></div>
            {:else}
              <div
                class="h-44 w-full bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center transition-transform duration-500 group-hover:scale-105"
              >
                <div class="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-3xl font-black shadow-md">
                  {classroom.class_name?.charAt(0)}
                </div>
              </div>
            {/if}
            
            <div class="p-4 flex flex-col items-start w-full bg-white z-10 relative">
              <h3 class="text-lg font-bold text-gray-800 line-clamp-2 w-full leading-tight">
                {classroom.class_name}
              </h3>
              <div class="mt-3 flex items-center justify-between w-full opacity-0 group-hover:opacity-100 transition-opacity">
                <span class="text-xs font-black text-blue-500 bg-blue-50 px-2 py-1 rounded"> عرض المحتوى</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
              </div>
            </div>
          </button>
        {/each}
      </div>
    {:else}
      <div
        class="py-20 text-center bg-white rounded-[2.5rem] border-2 border-dashed border-gray-100 text-gray-400 font-bold"
      >
        لا توجد نتائج تطابق بحثك حالياً.
      </div>
    {/if}
  {/if}
</div>
