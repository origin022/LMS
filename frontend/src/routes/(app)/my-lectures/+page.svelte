<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { apiFetch } from "$lib/api";
  import { fly } from "svelte/transition";

  interface Course {
    course_id: number;
    name: string;
    teacher_id?: number;
    teacher_name?: string;
  }

  interface Enrollment {
    enrollment_id: number;
    student_id: number;
    course: Course;
  }

  let enrollments: Enrollment[] = [];
  let loading = true;
  let searchQuery = "";
  let deletingId: number | null = null;
  let message = { text: "", type: "" };

  function showMsg(text: string, type: "success" | "error" = "success") {
    message = { text, type };
    setTimeout(() => {
      message = { text: "", type: "" };
    }, 4000);
  }

  $: filteredCourses = enrollments
    .map((e) => e.course)
    .filter(
      (c) =>
        c.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (c.teacher_name && c.teacher_name.toLowerCase().includes(searchQuery.toLowerCase()))
    );

  async function loadData() {
    loading = true;
    try {
      const res = await apiFetch("/enrollments");
      if (res.ok) {
        enrollments = await res.json();
      }
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function unenrollCourse(courseId: number, e: MouseEvent) {
    e.stopPropagation();
    if (!confirm("هل أنت متأكد من رغبتك في إلغاء الانضمام لهذا الكورس؟ لن تتمكن من متابعة دراسته إلا بعد مشاهدة إحدى محاضراته مرة أخرى.")) return;
    
    deletingId = courseId;
    try {
      const res = await apiFetch(`/enrollments/${courseId}`, { method: "DELETE" });
      if (res.ok) {
        enrollments = enrollments.filter(e => e.course.course_id !== courseId);
        showMsg("تم إلغاء الانضمام بنجاح ✅");
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg(err.detail || "حدث خطأ أثناء إلغاء الانضمام", "error");
      }
    } catch {
      showMsg("فشل الاتصال بالخادم", "error");
    } finally {
      deletingId = null;
    }
  }

  onMount(loadData);
</script>

{#if message.text}
  <div
    in:fly={{ y: -20 }}
    role="alert"
    class="fixed top-10 left-1/2 -translate-x-1/2 z-[60] px-6 py-3 rounded-2xl font-black text-sm shadow-2xl {message.type === 'error' ? 'bg-red-500' : 'bg-emerald-600'} text-white"
  >
    {message.text}
  </div>
{/if}

<svelte:head>
  <title>محاضراتي | المنصة التعليمية</title>
</svelte:head>

<div class="p-8 max-w-7xl mx-auto" dir="rtl">
  {#if loading}
    <div class="flex flex-col justify-center items-center h-[60vh] gap-4 text-gray-400">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      <p class="text-sm font-medium">جاري التحميل...</p>
    </div>
  {:else}
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
      <div class="flex items-center gap-4">
        <div>
          <h2 class="text-3xl font-black text-gray-800 tracking-tight">محاضراتي</h2>
          <p class="text-gray-500 text-sm mt-1 font-medium">جميع الكورسات التي تم التسجيل بها وبدء مشاهدتها</p>
        </div>
      </div>

      <div class="relative w-full md:w-80 group">
        <div class="absolute inset-y-0 right-4 flex items-center pointer-events-none text-gray-400 group-focus-within:text-emerald-600 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="ابحث في الكورسات..."
          class="w-full pr-12 pl-4 py-3.5 bg-white border border-gray-100 rounded-2xl shadow-sm focus:ring-4 focus:ring-emerald-50 focus:border-emerald-200 outline-none transition-all text-sm font-bold"
        />
      </div>
    </div>

    {#if filteredCourses.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {#each filteredCourses as course (course.course_id)}
          <div
            role="button"
            tabindex="0"
            on:click={() => goto(`/courses?course_id=${course.course_id}`)}
            on:keydown={(e) => e.key === "Enter" && goto(`/courses?course_id=${course.course_id}`)}
            class="group bg-white rounded-[2rem] p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all text-right relative overflow-hidden cursor-pointer"
          >
            <div class="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center mb-6 text-2xl font-black group-hover:bg-emerald-600 group-hover:text-white transition-all transform group-hover:rotate-6">
              {course.name?.charAt(0)}
            </div>
            <h3 class="text-xl font-bold text-gray-800 mb-2">
              {course.name}
            </h3>
            {#if course.teacher_name}
              <p class="text-xs text-gray-400 font-medium mb-1">
                👤 {course.teacher_name}
              </p>
            {/if}

            <div class="mt-4 pt-4 border-t border-gray-50 flex gap-2" on:click|stopPropagation role="none">
              <button
                class="flex-[2] py-2 text-xs font-black text-emerald-600 bg-emerald-50 hover:bg-emerald-100 rounded-xl transition-colors flex justify-center items-center gap-2"
                on:click={() => goto(`/courses?course_id=${course.course_id}`)}
              >
                متابعة التعلم
                <span>←</span>
              </button>
              <button
                on:click={(e) => unenrollCourse(course.course_id, e)}
                disabled={deletingId === course.course_id}
                class="flex-1 py-2 text-xs font-black text-red-500 bg-red-50 hover:bg-red-100 rounded-xl transition-colors disabled:opacity-60"
              >
                {deletingId === course.course_id ? "..." : "🗑️ إلغاء"}
              </button>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="py-20 text-center bg-white rounded-[2.5rem] border-2 border-dashed border-gray-100">
        <div class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-6 mx-auto">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.753 0-3.338.477-4.5 1.253" />
          </svg>
        </div>
        <p class="text-gray-400 font-bold mb-2">
          لم تقم بالانضمام إلى أية كورسات بعد.
        </p>
        <p class="text-sm text-gray-400 font-medium">
          شاهد أي محاضرة لأكثر من دقيقة وسيتم إضافتها هنا تلقائياً!
        </p>
      </div>
    {/if}
  {/if}
</div>
