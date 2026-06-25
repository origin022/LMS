<script lang="ts">
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/api";
  import { fly } from "svelte/transition";

  interface Course {
    course_id: number;
    name: string;
  }

  interface Classroom {
    class_id: number;
    class_name: string;
  }

  interface Lecture {
    lecture_id: number;
    title: string;
    description: string | null;
    course_id: number;
    created_at: string;
    media: { media_id: number; file_name: string }[];
  }

  let activeTab: "create-course" | "create-lecture" = "create-lecture";
  let loading = false;

  let classrooms: Classroom[] = [];
  let myCourses: Course[] = [];

  let courseName = "";
  let selectedClassId = "";
  let creatingCourse = false;

  let lectureTitle = "";
  let lectureDescription = "";
  let selectedCourseId = "";
  let videoFile: File | null = null;
  let documentFile: File | null = null;
  let lectureImageFile: File | null = null;
  let courseImageFile: File | null = null;
  let publishing = false;
  let generateQuizWithAI = false;
  let quizSource: "video" | "document" = "video";

  let message = { text: "", type: "" };

  function showMsg(text: string, type: "success" | "error" = "success") {
    message = { text, type };
    setTimeout(() => {
      message = { text: "", type: "" };
    }, 4000);
  }

  async function loadData() {
    loading = true;
    try {
      const resClassrooms = await apiFetch("/teacher/classrooms");
      if (resClassrooms.ok) {
        classrooms = await resClassrooms.json();
      }

      const resCourses = await apiFetch("/teacher/courses");
      if (resCourses.ok) {
        myCourses = await resCourses.json();
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  onMount(loadData);

  async function createCourse() {
    if (!courseName.trim() || !selectedClassId) {
      return showMsg("يرجى إدخال اسم الكورس واختيار الكلاس", "error");
    }
    creatingCourse = true;
    try {
      const res = await apiFetch("/teacher/courses", {
        method: "POST",
        body: JSON.stringify({
          name: courseName.trim(),
          class_id: parseInt(selectedClassId),
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return showMsg(err.detail || "فشل إنشاء الكورس", "error");
      }
      const newCourse: Course = await res.json();

      if (courseImageFile) {
        const formData = new FormData();
        formData.append("file", courseImageFile);
        await apiFetch(`/teacher/courses/${newCourse.course_id}/thumbnail`, {
          method: "PATCH",
          body: formData,
        });
      }

      myCourses = [...myCourses, newCourse];
      showMsg("تم إنشاء الكورس بنجاح ✅");
      courseName = "";
      courseImageFile = null;
      selectedClassId = "";
    } catch (e) {
      showMsg("حدث خطأ غير متوقع", "error");
    } finally {
      creatingCourse = false;
    }
  }

  async function publishLecture() {
    if (!lectureTitle || !selectedCourseId) {
      return showMsg("يرجى إدخال عنوان المحاضرة واختيار الكورس", "error");
    }
    if (!videoFile) {
      showMsg("يجب اختيار فيديو للمحاضرة أولاً", "error");
      return;
    }
    publishing = true;
    try {
      const res = await apiFetch(
        `/teacher/courses/${selectedCourseId}/lectures`,
        {
          method: "POST",
          body: JSON.stringify({
            title: lectureTitle,
            description: lectureDescription || null,
            course_id: parseInt(selectedCourseId),
          }),
        },
      );

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return showMsg(err.detail || "فشل نشر المحاضرة", "error");
      }

      const lecture: Lecture = await res.json();

      if (lectureImageFile) {
        const formData = new FormData();
        formData.append("file", lectureImageFile);
        await apiFetch(`/teacher/lectures/${lecture.lecture_id}/thumbnail`, {
          method: "PATCH",
          body: formData,
        });
      }

      if (videoFile) {
        const formData = new FormData();
        formData.append("file", videoFile);
        const uploadRes = await apiFetch(
          `/lectures/${lecture.lecture_id}/upload-video`,
          {
            method: "POST",
            body: formData,
            headers: {},
          },
        );
        if (!uploadRes.ok) {
          showMsg("تم نشر المحاضرة لكن فشل رفع الفيديو", "error");
          return;
        }
      }

      if (documentFile) {
        const formData = new FormData();
        formData.append("file", documentFile);
        const docUploadRes = await apiFetch(
          `/lectures/${lecture.lecture_id}/upload-document`,
          {
            method: "POST",
            body: formData,
            headers: {},
          },
        );
        if (!docUploadRes.ok) {
          showMsg("تم نشر المحاضرة وفيديوها لكن فشل رفع المستند", "error");
          publishing = false;
          return;
        }
      }

      // Automatically trigger AI Quiz generation if user opted in
      if (generateQuizWithAI) {
        try {
          const quizRes = await apiFetch("/generate-ai", {
            method: "POST",
            body: JSON.stringify({
              title: `كويز: ${lectureTitle}`,
              lecture_id: lecture.lecture_id,
              quiz_id: 0,
              source: documentFile ? quizSource : "video"
            }),
          });
          
          if (!quizRes.ok) {
            const quizErr = await quizRes.json().catch(() => ({}));
            showMsg(`تم نشر المحاضرة بنجاح، لكن: ${quizErr.detail || "تعذر توليد الكويز تلقائياً"}`, "error");
            // We don't return here because the lecture itself IS published successfully
          } else {
            showMsg("تم نشر المحاضرة وتوليد الكويز بنجاح ✅");
          }
        } catch (e) {
          console.error("Quiz Gen Error:", e);
          showMsg("المحاضرة نُشرت لكن حدث خطأ أثناء طلب توليد الكويز", "error");
        }
      } else {
        showMsg("تم نشر المحاضرة بنجاح ✅");
      }
      lectureTitle = "";
      lectureDescription = "";
      selectedCourseId = "";
      videoFile = null;
      documentFile = null;
      lectureImageFile = null;
    } catch (e) {
      showMsg("حدث خطأ غير متوقع", "error");
    } finally {
      publishing = false;
    }
  }
</script>

<div
  class="w-full min-h-screen p-4 md:p-8 space-y-6 bg-slate-50/50"
  dir="rtl"
>
  {#if message.text}
    <div
      in:fly={{ y: -20 }}
      class="fixed top-10 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-2xl font-black text-sm shadow-2xl {message.type ===
      'error'
        ? 'bg-red-500'
        : 'bg-blue-600'} text-white"
    >
      {message.text}
    </div>
  {/if}

  <div class="bg-white p-6 rounded-[2.5rem] shadow-sm border border-slate-100 text-center">
    <h1 class="text-2xl font-black text-slate-800">لوحة الأستاذ</h1>
    <p class="text-slate-400 text-xs font-bold mt-1">
      إنشاء الكورسات ونشر المحاضرات
    </p> 
  </div>

  <div class="flex gap-3">
    <button
      on:click={() => (activeTab = "create-lecture")}
      class="flex-1 py-3 rounded-2xl font-black text-sm transition-all {activeTab ===
      'create-lecture'
        ? 'bg-blue-600 text-white shadow-lg'
        : 'bg-white text-slate-500 border border-slate-100'}"
    >
     نشر محاضرة
    </button>
    <button
      on:click={() => (activeTab = "create-course")}
      class="flex-1 py-3 rounded-2xl font-black text-sm transition-all {activeTab ===
      'create-course'
        ? 'bg-blue-600 text-white shadow-lg'
        : 'bg-white text-slate-500 border border-slate-100'}"
    >
     إنشاء كورس
    </button>
  </div>

  {#if loading}
    <div class="flex justify-center py-20">
      <div
        class="animate-spin rounded-full h-8 w-8 border-[3px] border-blue-600 border-t-transparent"
      ></div>
    </div>
  {:else}
    {#if activeTab === "create-course"}
      <div in:fly={{ y: 10 }}>
        <div
          class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm max-w-2xl mx-auto space-y-6"
        >
          <h2 class="text-xl font-black text-slate-800">إنشاء كورس جديد</h2>

          <div class="space-y-2">
            <label for="inp-course-name" class="text-xs font-black text-slate-500"
              >اسم الكورس</label
            >
            <input
              id="inp-course-name"
              bind:value={courseName}
              placeholder="مثال: الرياضيات للمرحلة الثانوية"
              class="w-full p-4 bg-slate-50 border-none rounded-2xl outline-none font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          <div class="space-y-2">
            <label for="sel-class" class="text-xs font-black text-slate-500">اختر الكلاس التابع لقسمك</label>
            <select id="sel-class" bind:value={selectedClassId} class="w-full p-4 bg-slate-50 border-none rounded-2xl outline-none font-bold text-slate-700 text-sm focus:ring-2 focus:ring-blue-500/20">
              <option value="">-- اختر الكلاس --</option>
              {#each classrooms as cls}
                <option value={String(cls.class_id)}>{cls.class_name}</option>
              {/each}
            </select>
          </div>

          <div class="space-y-2">
            <p class="text-xs font-black text-slate-500">الصورة المصغرة للكورس (اختياري)</p>
            <label
              for="inp-course-img"
              class="flex flex-col items-center justify-center w-full h-24 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-all"
            >
              {#if courseImageFile}
                <span class="text-sm font-black text-blue-600">{courseImageFile.name}</span>
              {:else}
                <span class="text-xl mb-1">🖼️</span>
                <span class="text-xs font-black text-slate-400">اضغط لاختيار صورة</span>
              {/if}
              <input
                id="inp-course-img"
                type="file"
                accept="image/*"
                class="hidden"
                on:change={(e) => { courseImageFile = e.currentTarget.files?.[0] ?? null; }}
              />
            </label>
            {#if courseImageFile}
              <button
                on:click={() => (courseImageFile = null)}
                class="text-[10px] font-black text-red-400 hover:underline"
              >
                إزالة الصورة
              </button>
            {/if}
          </div>

          <button
            on:click={createCourse}
            disabled={creatingCourse}
            class="w-full py-5 bg-blue-600 text-white rounded-3xl font-black shadow-xl hover:bg-blue-700 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {creatingCourse ? "جارٍ الإنشاء..." : "إنشاء الكورس"}
          </button>
        </div>
      </div>
    {/if}

    {#if activeTab === "create-lecture"}
      <div in:fly={{ y: 10 }}>
        <div
          class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm max-w-2xl mx-auto space-y-6"
        >
          <h2 class="text-xl font-black text-slate-800">نشر محاضرة جديدة</h2>

          <div class="space-y-2">
            <label for="sel-course" class="text-xs font-black text-slate-500"
              >الكورس</label
            >
            {#if myCourses.length === 0}
              <p
                class="text-xs font-bold text-amber-500 bg-amber-50 rounded-2xl p-4"
              >
                ⚠️ لا توجد كورسات مسجلة باسمك. يرجى إنشاء كورس أولاً من تبويب "إنشاء
                كورس".
              </p>
            {:else}
              <select
                id="sel-course"
                bind:value={selectedCourseId}
                class="w-full p-4 bg-slate-50 border-none rounded-2xl outline-none font-bold text-slate-700 text-sm focus:ring-2 focus:ring-blue-500/20"
              >
                <option value="">اختر الكورس</option>
                {#each myCourses as course}
                  <option value={String(course.course_id)}>{course.name}</option>
                {/each}
              </select>
            {/if}
          </div>

          <div class="space-y-2">
            <label for="inp-title" class="text-xs font-black text-slate-500"
              >عنوان المحاضرة</label
            >
            <input
              id="inp-title"
              bind:value={lectureTitle}
              placeholder="مثال: مقدمة في الجبر"
              class="w-full p-4 bg-slate-50 border-none rounded-2xl outline-none font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          <div class="space-y-2">
            <label for="inp-desc" class="text-xs font-black text-slate-500"
              >الوصف (اختياري)</label
            >
            <textarea
              id="inp-desc"
              bind:value={lectureDescription}
              placeholder="أدخل وصفاً مختصراً للمحاضرة..."
              rows="3"
              class="w-full p-4 bg-slate-50 border-none rounded-2xl outline-none font-bold text-slate-700 resize-none focus:ring-2 focus:ring-blue-500/20"
            ></textarea>
          </div>

          <div class="space-y-2">
            <p class="text-xs font-black text-slate-500">الصورة المصغرة للمحاضرة (اختياري)</p>
            <label
              for="inp-lec-img"
              class="flex flex-col items-center justify-center w-full h-24 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-all"
            >
              {#if lectureImageFile}
                <span class="text-sm font-black text-blue-600">{lectureImageFile.name}</span>
              {:else}
                <span class="text-xl mb-1">🖼️</span>
                <span class="text-xs font-black text-slate-400">اضغط لاختيار صورة</span>
              {/if}
              <input
                id="inp-lec-img"
                type="file"
                accept="image/*"
                class="hidden"
                on:change={(e) => { lectureImageFile = e.currentTarget.files?.[0] ?? null; }}
              />
            </label>
            {#if lectureImageFile}
              <button
                on:click={() => (lectureImageFile = null)}
                class="text-[10px] font-black text-red-400 hover:underline"
              >
                إزالة الصورة
              </button>
            {/if}
          </div>

          <div class="space-y-2">
            <p class="text-xs font-black text-slate-500">
              فيديو المحاضرة (إجباري)
            </p>
            <label
              for="inp-video"
              class="flex flex-col items-center justify-center w-full h-32 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-all"
            >
              {#if videoFile}
                <span class="text-sm font-black text-blue-600"
                  >{videoFile.name}</span
                >
                <span class="text-[10px] text-slate-400 mt-1"
                  >{(videoFile.size / 1024 / 1024).toFixed(2)} MB</span
                >
              {:else}
                <span class="text-2xl mb-1">🎬</span>
                <span class="text-xs font-black text-slate-400"
                  >اضغط لاختيار فيديو</span
                >
              {/if}
              <input
                id="inp-video"
                type="file"
                accept="video/*"
                class="hidden"
                on:change={(e) => {
                  videoFile = e.currentTarget.files?.[0] ?? null;
                }}
              />
            </label>
            {#if videoFile}
              <button
                on:click={() => (videoFile = null)}
                class="text-[10px] font-black text-red-400 hover:underline"
              >
                إزالة الفيديو
              </button>
            {/if}
          </div>

          <div class="space-y-2">
            <p class="text-xs font-black text-slate-500">
              ملخص أو مستند PDF (اختياري)
            </p>
            <label
              for="inp-doc"
              class="flex flex-col items-center justify-center w-full h-24 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-all"
            >
              {#if documentFile}
                <span class="text-sm font-black text-blue-600"
                  >{documentFile.name}</span
                >
              {:else}
                <span class="text-xl mb-1">📄</span>
                <span class="text-xs font-black text-slate-400"
                  >اضغط لاختيار ملف PDF</span
                >
              {/if}
              <input
                id="inp-doc"
                type="file"
                accept="application/pdf"
                class="hidden"
                on:change={(e) => {
                  documentFile = e.currentTarget.files?.[0] ?? null;
                }}
              />
            </label>
            {#if documentFile}
              <button
                on:click={() => (documentFile = null)}
                class="text-[10px] font-black text-red-400 hover:underline"
              >
                إزالة المستند
              </button>
            {/if}
          </div>

          <button
            on:click={publishLecture}
            disabled={publishing || myCourses.length === 0}
            class="w-full py-5 bg-blue-600 text-white rounded-3xl font-black shadow-xl hover:bg-blue-700 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {publishing ? "جارٍ النشر..." : "نشر المحاضرة"}
          </button>

          <div class="flex items-center gap-3 bg-white p-4 rounded-2xl border border-slate-100 shadow-sm mt-4">
            <input
              id="ai-quiz"
              type="checkbox"
              bind:checked={generateQuizWithAI}
              class="w-5 h-5 accent-blue-600 rounded-lg cursor-pointer"
            />
            <label for="ai-quiz" class="flex flex-col cursor-pointer">
              <span class="text-sm font-black text-slate-700">توليد كويز تلقائي بالذكاء الاصطناعي</span>
              <span class="text-[10px] text-slate-400 font-bold">سيتم إنشاء 15 سؤالاً فور النشر</span>
            </label>
          </div>

          {#if generateQuizWithAI && documentFile}
            <div class="p-4 bg-blue-50/50 rounded-2xl border border-blue-100 flex flex-col gap-3">
              <p class="text-[10px] font-black text-blue-600">اختر مصدر توليد الأسئلة:</p>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="source" value="video" bind:group={quizSource} class="accent-blue-600" />
                  <span class="text-xs font-bold text-slate-600">🎥 صوت المحاضرة</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="source" value="document" bind:group={quizSource} class="accent-blue-600" />
                  <span class="text-xs font-bold text-slate-600">📄 وثائق المحاضرة (PDF)</span>
                </label>
              </div>
            </div>
          {:else}
              {#if generateQuizWithAI}
                <p class="text-[10px] font-black text-amber-600 bg-amber-50 p-2 rounded-lg border border-amber-100 italic">
                  ⚠️ سيتم توليد الكويز من صوت المحاضرة تلقائياً لعدم وجود ملف PDF
                </p>
              {/if}
          {/if}
        </div>
      </div>
    {/if}
  {/if}
</div>
