<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { apiFetch, FILE_URL } from "$lib/api";
  import { fly } from "svelte/transition";
  import { userStore } from "$lib/authStore";

  interface Course {
    course_id: number;
    name: string;
    teacher_id?: number;
    teacher_name?: string;
    course_thumbnail?: string;
  }

  interface Lecture {
    [x: string]: any;
    lecture_id: number;
    title: string;
    description?: string;
    created_at: string;
    text?: string | null;
    lecture_image?: string;
    quiz?: any[];
    media?: { media_id: number; file_name: string; file_path: string; mime_type: string }[];
  }

  $: classId = $page.url.searchParams.get("class_id");
  $: courseId = $page.url.searchParams.get("course_id");
  $: mineParam = $page.url.searchParams.get("mine") === "true";

  $: mineMode = !classId && !courseId;
  $: classMode = !!classId && !courseId;
  $: lectureMode = !!courseId;
  $: ownerLectureMode = lectureMode && (mineParam || isTeacher);

  $: role = $userStore.role ? String($userStore.role).trim().toLowerCase() : "";
  $: isTeacher = role == "3" || role === "teacher";

  let courses: Course[] = [];
  let lectures: Lecture[] = [];
  let pageTitle = "";
  let pageSubtitle = "";
  let courseName = "";
  let searchQuery = "";
  let loading = true;

  let editingCourse: Course | null = null;
  let editName = "";
  let saving = false;
  let deletingId: number | null = null;

  interface LectureEdit {
    lecture_id: number;
    title: string;
    description?: string;
  }
  let editingLecture: LectureEdit | null = null;
  let editLectureTitle = "";
  let editLectureDesc = "";
  let savingLecture = false;
  let deletingLectureId: number | null = null;
  let generatingQuizId: number | null = null;
  
  let showQuizEditModal = false;
  let editingQuiz: any = null;
  let loadingQuiz = false;
  let deletingQuiz = false;

  let message = { text: "", type: "" };

  let showQuizModal = false;
  let selectedLectureForQuiz: Lecture | null = null;
  let newQuizTitle = "";
  let quizSource: "video" | "document" = "video";



  function updateDifficulty(qIdx: number, newLevel: number) {
    if (!editingQuiz) return;

    const count = editingQuiz.question.filter((q: any) => q.difficulty_level === newLevel).length;

    if (count >= 7) {
      showMsg(`لا يمكن إضافة أكثر من  7 مع التوازن بين المستويات   ${newLevel === 1 ? 'السهل' : newLevel === 2 ? 'المتوسط' : 'الصعب'}`, "error");
      return;
    }

    editingQuiz.question[qIdx].difficulty_level = newLevel;
    editingQuiz = { ...editingQuiz };
  }

  function showMsg(text: string, type: "success" | "error" = "success") {
    message = { text, type };
    setTimeout(() => {
      message = { text: "", type: "" };
    }, 4000);
  }

  $: filteredCourses = courses.filter(
    (c) =>
      c.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.teacher_name &&
        c.teacher_name.toLowerCase().includes(searchQuery.toLowerCase())),
  );

  $: filteredLectures = lectures.filter(
    (l) =>
      l.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (l.description &&
        l.description.toLowerCase().includes(searchQuery.toLowerCase())),
  );

  async function loadData() {
    loading = true;
    searchQuery = "";
    courses = [];
    lectures = [];
    try {
      if (mineMode) {
        pageTitle = "كورساتي";
        pageSubtitle = "جميع الكورسات التي أنشأتها";
        const res = await apiFetch("/teacher/courses");
        if (res.ok) courses = await res.json();
      } else if (classMode && classId) {
        const res = await apiFetch(`/courses/${classId}`);
        if (res.ok) {
          const data = await res.json();
          pageTitle = "كورسات المجال";
          pageSubtitle = "تصفح الكورسات المتاحة في هذا المجال";
          courses = data.course || [];
        }
      } else if (lectureMode && courseId) {
  const res = await apiFetch(`/users/courses/${courseId}/lectures`);
  if (res.ok) {
    const data = await res.json();

    courseName = data.course_name || "";
    pageTitle = courseName ? `كورس: ${courseName}` : "محتوى الكورس";
    pageSubtitle = "قائمة المحاضرات المتاحة في هذا الكورس";

    lectures = data.lecture || [];

    // ربط quiz_id
    const quizRes = await apiFetch(`/courses/${courseId}/lectures/quiz-map`);
    if (quizRes.ok) {
      const quizMap = await quizRes.json();

      const map = new Map(
        quizMap.map((q: any) => [q.lecture_id, q.quiz_id])
      );

      lectures = lectures.map((lec) => ({
        ...lec,
        quiz_id: map.get(lec.lecture_id) || null
      }));
    }
  }
}console.log(lectures);
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  $: classId, courseId, loadData();
  onMount(loadData);

  function startEdit(course: Course, e: MouseEvent) {
    e.stopPropagation();
    editingCourse = course;
    editName = course.name;
  }

  function cancelEdit() {
    editingCourse = null;
    editName = "";
  }

  async function saveEdit() {
    if (!editingCourse || !editName.trim()) return;
    saving = true;
    try {
      const res = await apiFetch(`/courses/${editingCourse.course_id}`, {
        method: "PATCH",
        body: JSON.stringify({ name: editName.trim() }),
      });
      if (res.ok) {
        courses = courses.map((c) =>
          c.course_id === editingCourse!.course_id
            ? { ...c, name: editName.trim() }
            : c,
        );
        showMsg("تم تعديل الكورس بنجاح ✅");
        cancelEdit();
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg(err.detail || "فشل التعديل", "error");
      }
    } catch {
      showMsg("حدث خطأ غير متوقع", "error");
    } finally {
      saving = false;
    }
  }

  async function deleteCourse(courseId: number, e: MouseEvent) {
    e.stopPropagation();
    if (!confirm("هل أنت متأكد من حذف هذا الكورس؟ سيتم حذف جميع محاضراته."))
      return;
    deletingId = courseId;
    try {
      const res = await apiFetch(`/teacher/courses/${courseId}`, {
        method: "DELETE",
      });
      if (res.ok || res.status === 204) {
        courses = courses.filter((c) => c.course_id !== courseId);
        showMsg("تم حذف الكورس بنجاح ✅");
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg(err.detail || "فشل الحذف", "error");
      }
    } catch {
      showMsg("حدث خطأ غير متوقع", "error");
    } finally {
      deletingId = null;
    }
  }

  function startLectureEdit(lecture: Lecture, e: MouseEvent) {
    e.stopPropagation();
    editingLecture = {
      lecture_id: lecture.lecture_id,
      title: lecture.title,
      description: lecture.description,
    };
    editLectureTitle = lecture.title;
    editLectureDesc = lecture.description || "";
  }

  function cancelLectureEdit() {
    editingLecture = null;
    editLectureTitle = "";
    editLectureDesc = "";
  }

  async function saveLectureEdit() {
    if (!editingLecture || !editLectureTitle.trim()) return;
    savingLecture = true;
    try {
      const res = await apiFetch(`/lectures/${editingLecture.lecture_id}`, {
        method: "PATCH",
        body: JSON.stringify({
          title: editLectureTitle.trim(),
          description: editLectureDesc.trim() || null,
        }),
      });
      if (res.ok) {
        lectures = lectures.map((l) =>
          l.lecture_id === editingLecture!.lecture_id
            ? {
                ...l,
                title: editLectureTitle.trim(),
                description: editLectureDesc.trim() || undefined,
              }
            : l,
        );
        showMsg("تم تعديل المحاضرة بنجاح ✅");
        cancelLectureEdit();
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg(err.detail || "فشل التعديل", "error");
      }
    } catch {
      showMsg("حدث خطأ غير متوقع", "error");
    } finally {
      savingLecture = false;
    }
  }

  async function deleteLecture(lectureId: number, e: MouseEvent) {
    e.stopPropagation();
    if (!confirm("هل أنت متأكد من حذف هذه المحاضرة؟")) return;
    deletingLectureId = lectureId;
    try {
      const res = await apiFetch(`/lectures/${lectureId}`, {
        method: "DELETE",
      });
      if (res.ok || res.status === 204) {
        lectures = lectures.filter((l) => l.lecture_id !== lectureId);
        showMsg("تم حذف المحاضرة بنجاح ✅");
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg(err.detail || "فشل الحذف", "error");
      }
    } catch {
      showMsg("حدث خطأ غير متوقع", "error");
    } finally {
      deletingLectureId = null;
    }
  }
function openQuizModal(lecture: Lecture, e: MouseEvent) {
    e.stopPropagation();
    
    // إذا كان هناك كويز فعلاً، نفتح واجهة التعديل مباشرة
    if (lecture.quiz_id){
      const quizId = lecture.quiz_id; 
      manageQuiz(quizId, e);
      return;
    }
    
    // إذا لم يوجد كويز، نفتح واجهة الإنشاء
    selectedLectureForQuiz = lecture;
    newQuizTitle = `كويز: ${lecture.title}`;
    
    // تحديد المصدر الافتراضي: إذا كان هناك ملف PDF، نجعله هو المختار افتراضياً
    const hasPDF = lecture.media?.some(m => m.mime_type?.includes("pdf") || m.file_path?.toLowerCase().endsWith(".pdf"));
    quizSource = hasPDF ? "document" : "video";
    
    showQuizModal = true;
  }

  async function confirmGenerateQuiz() {
    if (!selectedLectureForQuiz || generatingQuizId) return;

    generatingQuizId = selectedLectureForQuiz.lecture_id;
    
    try {
      const genRes = await apiFetch("/generate-ai", {
        method: "POST",
        body: JSON.stringify({
          lecture_id: selectedLectureForQuiz.lecture_id,
          title: newQuizTitle.trim(),
          quiz_id: 0,
          source: quizSource
        }),
      });

      if (genRes.ok) {
        showMsg("تم بدء توليد الكويز بنجاح ✅");
        showQuizModal = false;
        await loadData();
      } else {
        const err = await genRes.json().catch(() => ({ detail: "فشل توليد الأسئلة" }));
        showMsg(err.detail, "error");
      }
    } catch (error) {
      showMsg("حدث خطأ في الاتصال بالخادم", "error");
    } finally {
      generatingQuizId = null;
    }
  }

  async function manageQuiz(quizId: number, e: MouseEvent) {
    e.stopPropagation();
    loadingQuiz = true;
    showQuizEditModal = true;
    try {
      const res = await apiFetch(`/quizzes/${quizId}/questions`);
      if (res.ok) {
        editingQuiz = await res.json();
      } else {
        showMsg("فشل تحميل بيانات الكويز", "error");
        showQuizEditModal = false;
      }
    } catch {
      showMsg("حدث خطأ في الاتصال", "error");
      showQuizEditModal = false;
    } finally {
      loadingQuiz = false;
    }
  }

  async function saveAllQuizChanges() {
    if (!editingQuiz) return;
    saving = true;
    try {
      const res = await apiFetch(`/quizzes/${editingQuiz.quiz_id}/bulk`, {
        method: "PATCH",
        body: JSON.stringify({
          title: editingQuiz.title,
          questions: editingQuiz.question.map((q: any) => ({
            question_id: q.question_id,
            question_text: q.question_text,
            difficulty_level: q.difficulty_level,
            options: q.question_option.map((o: any) => ({
              option_id: o.option_id,
              option_text: o.option_text,
              is_correct: o.is_correct
            }))
          }))
        })
      });
      if (res.ok) {
        showMsg("تم حفظ جميع التغييرات بنجاح ✅");
        showQuizEditModal = false;
        await loadData();
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg(err.detail || "فشل حفظ التغييرات", "error");
      }
    } catch {
      showMsg("حدث خطأ في الاتصال", "error");
    } finally {
      saving = false;
    }
  }

  function toggleOptionCorrect(qIdx: number, oId: number) {
    if (!editingQuiz) return;
    const question = editingQuiz.question[qIdx];
    question.question_option = question.question_option.map((opt: any) => ({
      ...opt,
      is_correct: opt.option_id === oId
    }));
    editingQuiz = { ...editingQuiz };
  }

  async function deleteFullQuiz() {
    if (!editingQuiz || !confirm("هل أنت متأكد من حذف الكويز بالكامل؟ لا يمكن التراجع!")) return;
    deletingQuiz = true;
    try {
      const res = await apiFetch(`/quizzes/${editingQuiz.quiz_id}`, { method: "DELETE" });
      if (res.ok || res.status === 204) {
        showMsg("تم حذف الكويز بنجاح ✅");
        showQuizEditModal = false;
        await loadData();
      } else {
        showMsg("فشل الحذف", "error");
      }
    } catch {
      showMsg("حدث خطأ", "error");
    } finally {
      deletingQuiz = false;
    }
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString("ar-EG", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }
</script>

{#if message.text}
  <div
    in:fly={{ y: -20 }}
    role="alert"
    class="fixed top-10 left-1/2 -translate-x-1/2 z-[60] px-6 py-3 rounded-2xl font-black text-sm shadow-2xl {message.type ===
    'error'
      ? 'bg-red-500'
      : 'bg-blue-600'} text-white"
  >
    {message.text}
  </div>
{/if}

{#if editingCourse}
  <div
    class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 flex items-center justify-center"
    on:click={cancelEdit}
    on:keydown={(e) => e.key === "Escape" && cancelEdit()}
    role="button"
    tabindex="-1"
    aria-label="Close modal"
  >
    <div
      class="bg-white rounded-[2rem] p-8 w-full max-w-md shadow-2xl mx-4"
      on:click|stopPropagation
      on:keydown|stopPropagation={() => {}}
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-course-title"
      tabindex="-1"
    >
      <h3 id="edit-course-title" class="text-xl font-black text-gray-800 mb-6">
        تعديل اسم الكورس
      </h3>
      <input
        bind:value={editName}
        placeholder="اسم الكورس"
        class="w-full p-4 bg-slate-50 rounded-2xl border-none outline-none font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20 mb-6"
      />
      <div class="flex gap-3">
        <button
          on:click={saveEdit}
          disabled={saving}
          class="flex-1 py-3 bg-blue-600 text-white rounded-2xl font-black hover:bg-blue-700 disabled:opacity-60 transition-all"
        >
          {saving ? "جاري الحفظ..." : "حفظ"}
        </button>
        <button
          on:click={cancelEdit}
          class="flex-1 py-3 bg-gray-100 text-gray-600 rounded-2xl font-black hover:bg-gray-200 transition-all"
        >
          إلغاء
        </button>
      </div>
    </div>
  </div>
{/if}

{#if editingLecture}
  <div
    class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 flex items-center justify-center"
    on:click={cancelLectureEdit}
    on:keydown={(e) => e.key === "Escape" && cancelLectureEdit()}
    role="button"
    tabindex="-1"
    aria-label="Close modal"
  >
    <div
      class="bg-white rounded-[2rem] p-8 w-full max-w-md shadow-2xl mx-4"
      on:click|stopPropagation
      on:keydown|stopPropagation={() => {}}
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-lecture-title"
      tabindex="-1"
    >
      <h3 id="edit-lecture-title" class="text-xl font-black text-gray-800 mb-6">
        تعديل المحاضرة
      </h3>
      <div class="space-y-4">
        <div>
          <label
            for="lecture-title-input"
            class="text-xs font-black text-gray-400 mr-2">العنوان</label
          >
          <input
            id="lecture-title-input"
            bind:value={editLectureTitle}
            placeholder="عنوان المحاضرة"
            class="w-full p-4 bg-slate-50 rounded-2xl border-none outline-none font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
        <div>
          <label
            for="lecture-desc-input"
            class="text-xs font-black text-gray-400 mr-2">الوصف</label
          >
          <textarea
            id="lecture-desc-input"
            bind:value={editLectureDesc}
            placeholder="وصف المحاضرة"
            rows="3"
            class="w-full p-4 bg-slate-50 rounded-2xl border-none outline-none font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20 resize-none"
          ></textarea>
        </div>
      </div>
      <div class="flex gap-3 mt-8">
        <button
          on:click={saveLectureEdit}
          disabled={savingLecture}
          class="flex-1 py-3 bg-blue-600 text-white rounded-2xl font-black hover:bg-blue-700 disabled:opacity-60 transition-all"
        >
          {savingLecture ? "جاري الحفظ..." : "حفظ"}
        </button>
        <button
          on:click={cancelLectureEdit}
          class="flex-1 py-3 bg-gray-100 text-gray-600 rounded-2xl font-black hover:bg-gray-200 transition-all"
        >
          إلغاء
        </button>
      </div>
    </div>
  </div>
{/if}

{#if showQuizEditModal}
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-md z-50 flex items-center justify-center p-4"
    on:click={() => (showQuizEditModal = false)}
    on:keydown={(e) => e.key === 'Escape' && (showQuizEditModal = false)}
    role="button"
    tabindex="0"
    aria-label="إغلاق النافذة المنبثقة"
  >
    <div
      class="bg-white rounded-[2.5rem] w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col"
      on:click|stopPropagation
      on:keydown|stopPropagation
      role="dialog"
      aria-modal="true"
      tabindex="0"
    >
      <div class="p-8 border-b border-gray-50 flex justify-between items-center bg-slate-50/50">
        <div>
          <h3 class="text-2xl font-black text-gray-800">إدارة الكويز 📝</h3>
          <p class="text-gray-500 text-sm font-medium mt-1">تعديل الأسئلة والخيارات أو حذف الكويز</p>
        </div>
        <button 
          on:click={() => (showQuizEditModal = false)}
          class="w-12 h-12 rounded-2xl bg-white shadow-sm hover:bg-gray-50 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-all"
          aria-label="إغلاق"
        >
          ✕
        </button>
      </div>

      {#if loadingQuiz}
        <div class="flex-1 flex flex-col items-center justify-center py-20 gap-4">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
          <p class="text-gray-400 font-bold">جاري تحميل البيانات...</p>
        </div>
      {:else if editingQuiz}
        <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
          <div class="grid grid-cols-1 gap-4 mb-8">
            <div class="space-y-2">
              <label for="quizTitle" class="text-xs font-black text-gray-400 mr-2">عنوان الكويز</label>
              <input 
                id="quizTitle"
                bind:value={editingQuiz.title} 
                class="w-full p-4 bg-slate-50 rounded-2xl border-none outline-none font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
          </div>

          <div class="mb-6 p-4 bg-blue-50/50 rounded-2xl flex items-center justify-between text-sm font-bold border border-blue-100/50">
            <span class="text-blue-600">📊 توزيع الصعوبة الحالي:</span>
            <div class="flex gap-4">
              <span class="text-emerald-600">
                سهل: {editingQuiz.question?.filter((q: any) => q.difficulty_level === 1).length || 0}
              </span>
              <span class="text-amber-600">
                متوسط: {editingQuiz.question?.filter((q: any) => q.difficulty_level === 2).length || 0}
              </span>
              <span class="text-rose-600">
                صعب: {editingQuiz.question?.filter((q: any) => q.difficulty_level === 3).length || 0}
              </span>
            </div>
          </div>

          <div class="space-y-6">
            <h4 class="text-lg font-black text-gray-700 flex items-center gap-2">
              <span class="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center text-sm">
                {editingQuiz.question?.length || 0}
              </span>
              الأسئلة الحالية
            </h4>

            {#each editingQuiz.question || [] as q, i}
              <div class="p-6 bg-slate-50 rounded-[2rem] border border-slate-100 transition-all hover:border-blue-100 group">
                <div class="flex gap-4 mb-4">
                  <span class="flex-shrink-0 w-8 h-8 rounded-full bg-white shadow-sm flex items-center justify-center text-xs font-black text-gray-400">
                    {i + 1}
                  </span>
                  <div class="flex-1 space-y-3">
                    <textarea 
                      bind:value={q.question_text}
                      rows="2"
                      class="w-full bg-transparent border-none outline-none font-bold text-gray-700 resize-none focus:ring-0 p-0"
                    ></textarea>

                    <div class="flex items-center gap-3">
                      <span class="text-[10px] font-black text-gray-400 uppercase tracking-wider">مستوى الصعوبة:</span>
                      <div class="flex bg-white p-1 rounded-xl shadow-sm border border-gray-50 gap-1">
                        <button
                          on:click={()=> updateDifficulty(i, 1)}
                          class="px-4 py-1.5 rounded-lg text-[10px] font-black transition-all {q.difficulty_level === 1 ? 'bg-emerald-500 text-white' : 'text-gray-400 hover:bg-gray-50'}"
                          disabled={q.difficulty_level === 1}
                        >
                          سهل
                        </button>
                        <button
                          on:click={()=> updateDifficulty(i, 2)}
                          class="px-4 py-1.5 rounded-lg text-[10px] font-black transition-all {q.difficulty_level === 2 ? 'bg-amber-500 text-white shadow-lg shadow-amber-100' : 'text-gray-400 hover:bg-gray-50'}"
                          disabled={q.difficulty_level === 2}
                        >
                          متوسط
                        </button>
                        <button
                          on:click={()=> updateDifficulty(i, 3)}
                          class="px-4 py-1.5 rounded-lg text-[10px] font-black transition-all {q.difficulty_level === 3 ? 'bg-rose-500 text-white shadow-lg shadow-rose-100' : 'text-gray-400 hover:bg-gray-50'}"
                          disabled={q.difficulty_level === 3}
                        >
                          صعب
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mr-12">
                  {#each q.question_option || [] as opt}
                    <div class="flex items-center gap-2 bg-white p-3 rounded-xl shadow-sm border {opt.is_correct ? 'border-emerald-200 bg-emerald-50/20' : 'border-transparent'} focus-within:border-blue-200 transition-all">
                      <input 
                        type="radio" 
                        name="correct-opt-{q.question_id}"
                        checked={opt.is_correct}
                        on:change={() => toggleOptionCorrect(i, opt.option_id)}
                        class="w-5 h-5 rounded-full border-gray-200 text-emerald-600 focus:ring-emerald-500/20"
                      />
                      <input 
                        bind:value={opt.option_text}
                        class="flex-1 bg-transparent border-none outline-none text-sm font-bold {opt.is_correct ? 'text-emerald-700' : 'text-gray-600'} focus:ring-0 p-0"
                      />
                      {#if opt.is_correct}
                        <span class="text-[10px] font-black text-emerald-500 bg-emerald-100 px-2 py-0.5 rounded-full">الجواب الصحيح</span>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        </div>

        <div class="p-8 border-t border-gray-50 bg-slate-50/30 flex justify-between items-center">
          <button 
            on:click={deleteFullQuiz}
            disabled={deletingQuiz}
            class="px-8 py-3 bg-red-50 text-red-500 rounded-2xl font-black hover:bg-red-100 transition-all flex items-center gap-2"
          >
            {#if deletingQuiz}
              جاري الحذف...
            {:else}
              🗑️ حذف الكويز بالكامل
            {/if}
          </button>
          
          <button 
            on:click={saveAllQuizChanges}
            disabled={saving}
            class="px-10 py-3 bg-blue-600 text-white rounded-2xl font-black hover:bg-blue-700 disabled:opacity-60 transition-all shadow-lg shadow-blue-200"
          >
            {saving ? "جاري الحفظ..." : "حفظ الكل"}
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}

{#if showQuizModal}
  <div
    class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center"
    on:click={() => (showQuizModal = false)}
    on:keydown={(e) => e.key === "Escape" && (showQuizModal = false)}
    role="button"
    tabindex="-1"
    aria-label="Close modal"
  >
    <div
      class="bg-white rounded-[2rem] p-8 w-full max-w-md shadow-2xl mx-4"
      on:click|stopPropagation
      on:keydown|stopPropagation={() => {}}
      role="dialog"
      aria-modal="true"
      aria-labelledby="quiz-modal-title"
      tabindex="-1"
    >
      <h3 id="quiz-modal-title" class="text-xl font-black text-gray-800 mb-6">إعدادات الكويز الذكي ✨</h3>
      
      <div class="space-y-4">
        <div>
          <!-- svelte-ignore a11y_label_has_associated_control -->
          <label class="text-xs font-black text-gray-400 mr-2">عنوان الاختبار</label>
          <input
            bind:value={newQuizTitle}
            placeholder="مثلاً: اختبار شامل للفصل الأول"
            class="w-full p-4 bg-slate-50 rounded-2xl border-none outline-none font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        {#if selectedLectureForQuiz?.media?.some(m => m.mime_type?.includes("pdf") || m.file_path?.toLowerCase().endsWith(".pdf"))}
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
          <p class="text-[10px] font-black text-amber-600 bg-amber-50 p-3 rounded-xl border border-amber-100 italic">
            ⚠️ سيتم توليد الكويز من صوت المحاضرة لعدم وجود ملفات PDF مرفقة.
          </p>
        {/if}
      </div>

      <div class="flex gap-3 mt-8">
        <button
          on:click={confirmGenerateQuiz}
          disabled={generatingQuizId !== null || !newQuizTitle.trim()}
          class="flex-1 py-3 bg-blue-600 text-white rounded-2xl font-black hover:bg-blue-700 disabled:opacity-60 transition-all shadow-lg shadow-blue-100"
        >
          {generatingQuizId ? "جاري التوليد..." : "ابدأ الإنشاء"}
        </button>
        <button
          on:click={() => (showQuizModal = false)}
          class="flex-1 py-3 bg-gray-100 text-gray-600 rounded-2xl font-black hover:bg-gray-200 transition-all"
        >
          إلغاء
        </button>
      </div>
    </div>
  </div>
{/if}

<div class="p-8 max-w-7xl mx-auto" dir="rtl">
  {#if loading}
    <div
      class="flex flex-col justify-center items-center h-[60vh] gap-4 text-gray-400"
    >
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
      ></div>
      <p class="text-sm font-medium">جاري التحميل...</p>
    </div>
  {:else}
    <div
      class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10"
    >
      <div class="flex items-center gap-4">
        {#if lectureMode}
          <button
            on:click={() => window.history.back()}
            aria-label="Back"
            class="w-10 h-10 rounded-2xl bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        {/if}
        <div>
          <h2 class="text-3xl font-black text-gray-800 tracking-tight">
            {pageTitle}
          </h2>
          <p class="text-gray-500 text-sm mt-1 font-medium">{pageSubtitle}</p>
        </div>
      </div>

      <div class="relative w-full md:w-80 group">
        <div
          class="absolute inset-y-0 right-4 flex items-center pointer-events-none text-gray-400 group-focus-within:text-blue-600 transition-colors"
          aria-hidden="true"
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
          placeholder={lectureMode ? "ابحث عن محاضرة..." : "ابحث عن كورس..."}
          class="w-full pr-12 pl-4 py-3.5 bg-white border border-gray-100 rounded-2xl shadow-sm focus:ring-4 focus:ring-blue-50 focus:border-blue-200 outline-none transition-all text-sm font-bold"
        />
      </div>
    </div>

    {#if !lectureMode}
      {#if filteredCourses.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {#each filteredCourses as course (course.course_id)}
            <div
              role="button"
              tabindex="0"
              on:click={() =>
                goto(
                  `/courses?course_id=${course.course_id}${mineMode ? "&mine=true" : ""}`,
                )}
              on:keydown={(e) =>
                e.key === "Enter" &&
                goto(
                  `/courses?course_id=${course.course_id}${mineMode ? "&mine=true" : ""}`,
                )}
              class="group bg-white rounded-2xl shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all text-right relative overflow-hidden cursor-pointer flex flex-col border border-gray-100 p-0"
            >
              {#if course.course_thumbnail}
                <div class="h-44 w-full bg-cover bg-center transition-transform duration-500 group-hover:scale-105" style="background-image: url('{FILE_URL}{course.course_thumbnail}')"></div>
              {:else}
                <div
                  class="h-44 w-full bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center transition-transform duration-500 group-hover:scale-105"
                >
                  <div class="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-3xl font-black shadow-md">
                    {course.name?.charAt(0)}
                  </div>
                </div>
              {/if}
              
              <div class="p-4 flex flex-col items-start w-full bg-white z-10 relative">
                <h3 class="text-lg font-bold text-gray-800 line-clamp-2 leading-tight mb-2 w-full">
                  {course.name}
                </h3>
                {#if course.teacher_name && !mineMode}
                  <p class="text-[11px] text-slate-500 font-bold mb-2 flex items-center gap-1.5 opacity-90">
                    <span class="w-5 h-5 bg-slate-100 rounded-full flex items-center justify-center text-[10px]">👨‍🏫</span>
                    {course.teacher_name}
                  </p>
                {/if}

              {#if mineMode}
                <div
                  class="mt-4 pt-4 border-t border-gray-50 flex gap-2 w-full"
                  on:click|stopPropagation
                  on:keydown|stopPropagation={() => {}}
                  role="button"
                  tabindex="-1"
                >
                  <button
                    on:click={(e) => startEdit(course, e)}
                    class="flex-1 py-2 text-xs font-black text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors"
                  >
                    ✏️ تعديل
                  </button>
                  <button
                    on:click={(e) => deleteCourse(course.course_id, e)}
                    disabled={deletingId === course.course_id}
                    class="flex-1 py-2 text-xs font-black text-red-500 bg-red-50 hover:bg-red-100 rounded-xl transition-colors disabled:opacity-60"
                  >
                    {deletingId === course.course_id ? "..." : "🗑️ حذف"}
                  </button>
                </div>
              {:else}
                <div
                  class="mt-4 pt-4 border-t border-gray-50 text-blue-600 text-xs font-black flex items-center justify-between gap-2 w-full"
                >
                  استكشف المحتوى
                  <span
                    class="group-hover:translate-x-[-4px] transition-transform"
                    >←</span
                  >
                </div>
              {/if}
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div
          class="py-20 text-center bg-white rounded-[2.5rem] border-2 border-dashed border-gray-100"
        >
          <div
            class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-6 mx-auto"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-10 w-10 text-gray-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.753 0-3.338.477-4.5 1.253"
              />
            </svg>
          </div>
          <p class="text-gray-400 font-bold">
            {mineMode
              ? "لا توجد كورسات منشورة باسمك بعد."
              : "لا توجد كورسات في هذا الكلاس بعد."}
          </p>
          {#if mineMode}
            <button
              on:click={() => goto("/teacher")}
              class="mt-4 text-sm font-black text-blue-600 bg-blue-50 hover:bg-blue-100 px-6 py-2 rounded-full transition-colors"
            >
              إنشاء كورس جديد
            </button>
          {/if}
        </div>
      {/if}
    {:else if filteredLectures.length > 0}


      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6">
        {#each filteredLectures as lecture (lecture.lecture_id)}
          <div
            role="button"
            tabindex="0"
            on:click={() => goto(`/lecture/${lecture.lecture_id}`)}
            on:keydown={(e) =>
              e.key === "Enter" && goto(`/lecture/${lecture.lecture_id}`)}
            class="group bg-white rounded-2xl shadow-sm hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 text-right flex flex-col cursor-pointer relative overflow-hidden border border-gray-100 p-0"
          >
          
            <!-- Thumbnail area -->
            <div class="relative w-full h-48 bg-slate-100 overflow-hidden">
              {#if lecture.lecture_image}
                <div class="absolute inset-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-105" style="background-image: url('{FILE_URL}{lecture.lecture_image}')"></div>
              {:else}
                <div class="absolute inset-0 bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center transition-transform duration-700 group-hover:scale-105">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-20 w-20 text-blue-200"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"
                    />
                  </svg>
                </div>
              {/if}
              <!-- Duration / Date badge overlay -->
              <div class="absolute bottom-2 right-2 bg-black/70 text-white text-[10px] font-bold px-2 py-1 rounded backdrop-blur-sm">
                {formatDate(lecture.created_at)}
              </div>
            </div>

            <!-- Content Area -->
            <div class="p-4 flex flex-col flex-grow bg-white z-10 relative">
              <div class="flex gap-3 items-start w-full">
                <!-- Avatar icon -->
                <div class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <!-- Text Details -->
                <div class="flex flex-col w-full">
                  <h3 class="text-[15px] font-bold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2 leading-tight">
                    {lecture.title}
                  </h3>
                  <p class="text-gray-500 text-[12px] line-clamp-1 font-medium mt-1">
                    {lecture.description || "لا يوجد وصف لهذه المحاضرة"}
                  </p>
                </div>
              </div>

            <div class="relative z-10 space-y-2 mt-4 ml-12">
              {#if ownerLectureMode}
                <div class="grid grid-cols-2 gap-2" on:click|stopPropagation role="none">
                  <button
                    on:click={(e) => startLectureEdit(lecture, e)}
                    class="py-1.5 text-[11px] font-black text-blue-600 bg-blue-50 hover:bg-blue-600 hover:text-white rounded-lg transition-all"
                  >
                    تعديل
                  </button>
                  <button
                    on:click={(e) => deleteLecture(lecture.lecture_id, e)}
                    disabled={deletingLectureId === lecture.lecture_id}
                    class="py-1.5 text-[11px] font-black text-red-500 bg-red-50 hover:bg-red-500 hover:text-white rounded-lg transition-all disabled:opacity-50"
                  >
                    حذف
                  </button>
                </div>
                
               {#if lecture.quiz_id}
  <button
    on:click={(e) => manageQuiz(lecture.quiz_id, e)}
    class="w-full py-2 bg-white border border-slate-200 text-slate-700 text-[11px] font-black rounded-lg hover:bg-slate-50 transition-all flex items-center justify-center gap-1.5"
  >
    تعديل الكويز
  </button>
{:else}
  <button
    on:click={(e) => openQuizModal(lecture, e)}
    disabled={generatingQuizId === lecture.lecture_id}
    class="w-full py-2 bg-blue-600 text-white text-[11px] font-black rounded-lg hover:bg-blue-700 transition-all shadow-md shadow-blue-100 flex items-center justify-center gap-1.5"
  >
    {generatingQuizId === lecture.lecture_id ? "..." : "كويز"}
  </button>
{/if}
              {/if}
            </div>
            <!-- End Content Area -->
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="py-20 text-center bg-white rounded-[2.5rem] border-2 border-dashed border-gray-100">
        <p class="text-gray-400 font-bold">لا توجد محاضرات في هذا الكورس بعد.</p>
      </div>
    {/if}
  {/if}
</div>

<style>
  :global(.custom-scrollbar::-webkit-scrollbar) {
    width: 6px;
  }
  :global(.custom-scrollbar::-webkit-scrollbar-track) {
    background: transparent;
  }
  :global(.custom-scrollbar::-webkit-scrollbar-thumb) {
    background: #e2e8f0;
    border-radius: 10px;
  }
</style>