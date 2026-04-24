<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { page } from "$app/stores";
  import { apiFetch, BASE_URL, FILE_URL, WS_URL } from "$lib/api";
  import { userStore } from "$lib/authStore";
  import QuizModal from "$lib/components/QuizModal.svelte";
  import {
    Heart,
    Clock,
    MessageCircle,
    Send,
    FileText,
    Loader2,
    PlayCircle,
    BookOpen,
    ChevronLeft,
    Maximize,
    Languages,
    Captions,
    CaptionsOff,
    Trash2,
    Edit2,
    X,
    Check,
  } from "lucide-svelte";

  interface SubtitleSegment {
    start: number;
    end: number;
    text: string;
  }
  interface Lecture {
    lecture_id: number;
    title: string;
    description?: string;
    text?: string;
    created_at: string;
    likes_count: number;
    is_liked: boolean;
    quiz_id?: number; 
    course_id?: number; 
    media?: { file_path: string; mime_type: string; file_name: string }[];
  }

  let lecture: Lecture | null = null;
  let comments: any[] = [];
  let newComment = "";
  let commentError = "";
  let loading = true;
  let currentTime = 0;
  let duration = 0;
  let videoElement: HTMLVideoElement;
  let playerContainer: HTMLElement;
  let parsedSubtitles: SubtitleSegment[] = [];
  let showSubtitles = true;
  let showQuizModal = false;  
  let submitting = false;


  $: lectureId = $page.params.lecture_id;

  $: if (lecture?.text) {
    try {
      const data = JSON.parse(lecture.text);
      parsedSubtitles = Array.isArray(data) ? data : data.segments || [];
    } catch (e) {
      parsedSubtitles = [{ start: 0, end: 9999, text: lecture.text }];
    }
  }


  async function loadData() {
    if (!lectureId) return;
    loading = true;
    try {
      const [lRes, cRes] = await Promise.all([
        apiFetch(`/lectures/${lectureId}`),
        apiFetch(`/interactions/lectures/${lectureId}/comments`),
      ]);
      if (lRes.ok) lecture = await lRes.json();
      if (cRes.ok) comments = await cRes.json();
    } finally {
      loading = false;
    }
  }

  const seekTo = (time: number) => {
    if (videoElement) videoElement.currentTime = time;
  };

  const toggleFullscreen = () => {
    if (playerContainer) {
      if (!document.fullscreenElement) {
        playerContainer.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    }
  };

  async function toggleLike() {
    if (!lecture) return;
    const original = { liked: lecture.is_liked, count: lecture.likes_count };
    lecture.is_liked = !lecture.is_liked;
    lecture.likes_count += lecture.is_liked ? 1 : -1;

    try {
      const res = await apiFetch(`/interactions/lectures/${lectureId}/like`, {
        method: "POST",
      });
      if (!res.ok) throw new Error();
    } catch (err) {
      lecture.is_liked = original.liked;
      lecture.likes_count = original.count;
    }
  }

  let enrolled = false;
  let enrolling = false;

async function handleAutoEnroll() {
    if (enrolling || enrolled || !lecture?.course_id || !$userStore.name) return;

    enrolling = true;
    try {
      const res = await apiFetch(`/enrollments/trigger/${lecture.course_id}`, {
        method: "POST"
      });

      // إذا نجح (200) أو إذا كان مسجلاً بالفعل (400) أو ليس لديه صلاحية (403)
      // في كل هذه الحالات يجب أن نتوقف عن المحاولة
      if (res.ok || res.status === 400 || res.status === 403) {
        enrolled = true; 
        if (res.ok) console.log("Successfully enrolled");
        else console.warn("Enrollment skip: Already enrolled or forbidden");
      } else {
        enrolled = true;
      }
    } catch (err) {
      console.error("Auto-enrollment error:", err);
      enrolled = true; 
    } finally {
      enrolling = false;
    }
  }

  $: if (currentTime >= 5 && !enrolled && !enrolling) {
    handleAutoEnroll();
  }

  async function submitComment() {
    if (!newComment.trim() || submitting) return;
    const id = lecture?.lecture_id;
    if (!id) return;
    commentError = "";
    submitting = true;

    // Failsafe: Reset submitting after 10 seconds
    const timeout = setTimeout(() => {
        if (submitting) {
            submitting = false;
            commentError = "استغرق الطلب وقتاً طويلاً، حاول مجدداً";
        }
    }, 10000);

    try {
      const res = await apiFetch(`/interactions/lectures/${id}/comments`, {
        method: "POST",
        body: JSON.stringify({
          text: newComment,
          lecture_id: id,
        }),
      });
      clearTimeout(timeout);
      
      if (res.ok) {
        const added = await res.json();
        if (!added.user) {
          added.user = {
            name: $userStore.name,
            profile_picture_url: null,
          };
        }
        // تجنب التكرار (لو الويب سوكت أرسله قبلي)
        if (!comments.some(c => c.comment_id === added.comment_id)) {
            comments = [added, ...comments];
        }
        newComment = "";
      } else {
        if (res.status === 429) {
          commentError = "أرسلت الكثير من التعليقات، انتظر قليلاً";
        } else if (res.status === 403) {
          commentError = "ليس لديك صلاحية لإرسال التعليقات";
        } else {
          const err = await res.json().catch(() => ({}));
          commentError = err.detail || "فشل إرسال التعليق";
        }
      }
    } catch (err) {
      clearTimeout(timeout);
      commentError = "خطأ في الاتصال بالسيرفر";
    } finally {
      submitting = false;
    }
  }

  async function deleteComment(id: number) {
    if (!confirm("هل أنت متأكد من حذف هذا التعليق؟")) return;
    try {
      const res = await apiFetch(`/manager/delete-comment/${id}`, {
        method: "DELETE",
      });
      if (res.ok) {
        comments = comments.filter((c) => c.comment_id !== id);
      }
    } catch (err) {
      console.error("Failed to delete comment", err);
    }
  }

  let editingCommentId: number | null = null;
  let editingCommentText = "";
  let updatingComment = false;

  function cancelEdit() {
    editingCommentId = null;
    editingCommentText = "";
  }

  function startEdit(comment: any) {
    editingCommentId = comment.comment_id;
    editingCommentText = comment.text;
  }

  async function updateComment(id: number) {
    if (!editingCommentText.trim() || updatingComment) return;
    updatingComment = true;
    try {
      const res = await apiFetch(`/interactions/comment/${id}`, {
        method: "PATCH",
        body: JSON.stringify({
          text: editingCommentText
        }),
      });
      if (res.ok) {
        const updated = await res.json();
        // Update local comment list (if websocket doesn't already, but ws is better ignored for self-update of edit)
        comments = comments.map(c => 
          c.comment_id === id ? { ...c, text: updated.text } : c
        );
        editingCommentId = null;
        editingCommentText = "";
      } else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || "فشل تحديث التعليق");
      }
    } catch (err) {
      console.error(err);
      alert("خطأ في الاتصال بالسيرفر");
    } finally {
      updatingComment = false;
    }
  }

// 1. جعل فتح الاتصال مرتبط بتغير الـ ID وإغلاق القديم تلقائياً
  let ws: WebSocket | null = null;
  let reconnectTimer: any;

  function connectWebSocket() {
  if (!lectureId) return;

  // اغلق أي اتصال موجود بشكل قاطع
  if (ws) {
    ws.onclose = null;
    ws.close();
    ws = null;
  }

  const wsUrl = `${WS_URL}/interactions/ws/${lectureId}`;
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("WS connected");
  };

  ws.onmessage = (event) => {
    try {
      const incoming = JSON.parse(event.data);
      const exists = comments.some(c => c?.comment_id === incoming?.comment_id);
      if (!exists) {
        comments = [incoming, ...comments];
      }
    } catch {}
  };

  ws.onclose = () => {
    ws = null;
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(connectWebSocket, 1000);
  };

  ws.onerror = () => {
    // لا تفعل شيء
  };
}
  // مراقبة الـ ID فقط، وإغلاق الاتصال القديم قبل فتح الجديد
let prevLectureId: string;

$: if (lectureId && lectureId !== prevLectureId) {
  prevLectureId = lectureId;

  if (ws) {
    ws.close(1000);
    ws = null;
  }

  connectWebSocket();
}

  onDestroy(() => {
    clearTimeout(reconnectTimer);
    if (ws) {
      ws.onclose = null;
      ws.close(1000);
      ws = null;
    }
  });
  // 2. تحسين أداء الترجمة: البحث فقط عندما تتغير الثواني وليس الفريمات
let activeSubtitle: SubtitleSegment | undefined;

let lastTime = 0;
$: if (Math.floor(currentTime) !== lastTime) {
  lastTime = Math.floor(currentTime);
  activeSubtitle = parsedSubtitles.find(
    (s) => currentTime >= s.start && currentTime <= s.end
  );
}

  onMount(() => {
    loadData();
  });



</script>

<div
  class="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-indigo-500/30"
  dir="rtl"
>
  {#if loading}
    <div class="flex h-screen items-center justify-center">
      <div class="relative flex items-center justify-center">
        <div
          class="absolute w-20 h-20 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"
        ></div>
        <Loader2 class="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    </div>
  {:else if lecture}
    <main class="max-w-[1600px] mx-auto p-4 lg:p-8 space-y-8">
      <section
        bind:this={playerContainer}
        class="relative aspect-video bg-black rounded-[2rem] overflow-hidden border border-white/5 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)] group"
      >
        {#if lecture.media?.[0]}
          {#key lecture.media[0].file_path}
            <video
              bind:this={videoElement}
              bind:currentTime
              bind:duration
              controls
              class="w-full h-full object-contain"
            >
              <source
                src={`${FILE_URL}${lecture.media[0].file_path}`}
                type={lecture.media[0].mime_type}
              />
            </video>
          {/key}

          <div
            class="absolute top-2 right-2 md:top-6 md:right-6 flex items-center gap-2 md:gap-3 opacity-100 md:opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-50"
          >
            <button
              on:click={() => (showSubtitles = !showSubtitles)}
              class="p-2 md:p-3 rounded-xl md:rounded-2xl bg-black/50 md:bg-black/40 backdrop-blur-xl border border-white/10 text-white hover:bg-indigo-500 transition-all shadow-lg pointer-events-auto"
            >
              {#if showSubtitles}
                <Captions size={20} />
              {:else}
                <CaptionsOff size={20} />
              {/if}
            </button>

            <button
              on:click={toggleFullscreen}
              class="p-2 md:p-3 rounded-xl md:rounded-2xl bg-black/50 md:bg-black/40 backdrop-blur-xl border border-white/10 text-white hover:bg-indigo-500 transition-all shadow-lg pointer-events-auto"
            >
              <Maximize size={20} />
            </button>
          </div>

          {#if activeSubtitle && showSubtitles}
            <div
              class="absolute bottom-24 md:bottom-16 left-0 right-0 flex justify-center px-4 md:px-8 pointer-events-none transition-all duration-300 z-40"
            >
              <div
                class="bg-black/70 backdrop-blur-lg border border-white/10 px-3 py-1.5 md:px-6 md:py-3 rounded-xl md:rounded-2xl shadow-2xl max-w-[90%]"
              >
                <p
                  class="text-white text-sm md:text-2xl font-bold text-center leading-relaxed drop-shadow-lg"
                >
                  {activeSubtitle.text}
                </p>
              </div>
            </div>
          {/if}
        {:else}
          <div
            class="flex flex-col items-center justify-center h-full text-slate-700 bg-slate-100"
          >
            <PlayCircle size={80} strokeWidth={1} class="animate-pulse" />
            <p
              class="mt-4 font-bold tracking-widest uppercase text-xs opacity-50"
            >
              Waiting for Media Content
            </p>
          </div>
        {/if}
      </section>

      <div
        class="bg-white border border-slate-200 rounded-[2.5rem] p-8 space-y-6 shadow-sm"
      >
        <div class="flex flex-col md:flex-row justify-between gap-6">
          <div class="space-y-4">
            <h1
              class="text-3xl md:text-4xl font-black text-slate-900 leading-tight italic"
            >
              {lecture.title}
            </h1>
            <div class="flex items-center gap-6">
              <div class="flex items-center gap-2 text-slate-400">
                <div class="p-2 bg-indigo-500/10 rounded-lg">
                  <Clock size={16} class="text-indigo-400" />
                </div>
                <span class="text-sm font-semibold"
                  >{new Date(lecture.created_at).toLocaleDateString(
                    "ar-EG",
                  )}</span
                >
              </div>

            </div>
          </div>

          <button
            on:click={toggleLike}
            disabled={!$userStore.name}
            class="self-start group flex items-center gap-4 bg-slate-50 hover:bg-slate-100 border border-slate-200 px-6 py-4 rounded-3xl transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="flex flex-col items-end">
              <span
                class="text-[10px] font-black uppercase tracking-widest text-slate-500"
                >Appreciations</span
              >
              <span class="text-lg font-bold text-slate-900"
                >{lecture.likes_count}</span
              >
            </div>
            <div
              class="w-12 h-12 rounded-2xl flex items-center justify-center transition-all {lecture.is_liked
                ? 'bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.4)]'
                : 'bg-slate-100 text-slate-400'}"
            >
              <Heart
                size={24}
                class={lecture.is_liked
                  ? "fill-current"
                  : "group-hover:scale-110 transition-transform"}
              />
            </div>
          </button>
          {#if lecture?.quiz_id != null && $userStore.role?.toString().toLowerCase() === "student"}
  <button
    on:click={() => (showQuizModal = true)}
    class="self-start group flex items-center gap-4 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-4 rounded-3xl transition-all active:scale-95 shadow-lg shadow-indigo-600/20"
  >
    <BookOpen size={20} />
    <span class="font-black text-sm">اختبار</span>
  </button>
{/if}
          
          {#each lecture.media?.filter(m => m.mime_type === 'application/pdf' || m.file_path.endsWith('.pdf')) || [] as doc}
            <a
              href={`${FILE_URL}${doc.file_path}`}
              target="_blank"
              class="self-start group flex items-center gap-4 bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-4 rounded-3xl transition-all active:scale-95 shadow-lg shadow-emerald-600/20"
            >
              <FileText size={20} />
              <div class="flex flex-col items-start text-right">
                <span class="font-black text-sm">تحميل الملف</span>
                <span class="text-[10px] opacity-70 truncate max-w-[150px]">{doc.file_name}</span>
              </div>
            </a>
          {/each}
        </div>

        <div
          class="h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent w-full"
        ></div>

        <div class="space-y-4">
          <h3
            class="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500"
          >
            الوصف
          </h3>
          <p class="text-slate-600 text-lg leading-relaxed max-w-4xl">
            {lecture.description || "لا يوجد وصف متوفر لهذه المحاضرة حالياً."}
          </p>
        </div>
      </div>

      <section class="space-y-6">
        <div class="flex items-center gap-4 px-2">
          <div
            class="p-3 bg-indigo-500 rounded-2xl shadow-lg shadow-indigo-500/20"
          >
            <MessageCircle class="text-white" size={24} />
          </div>
          <h2 class="text-2xl font-black text-slate-900 italic">ساحة النقاش</h2>
        </div>

        <div
          class="bg-white border border-slate-200 p-6 rounded-[2rem] shadow-sm focus-within:ring-2 ring-indigo-500/20 transition-all"
        >
          <img
            src={$userStore.profilePicture || "/default-avatar.png"}
            alt="My Profile"
            class="w-10 h-10 rounded-xl object-cover border border-slate-200"
          />
          <textarea
            bind:value={newComment}
            disabled={!$userStore.name}
            placeholder={$userStore.name ? "لديك سؤال؟ اطرحه هنا ليجيبك المحاضر..." : "الرجاء تسجيل الدخول للمشاركة في النقاش"}
            class="w-full bg-transparent border-none outline-none text-slate-800 placeholder:text-slate-400 resize-none min-h-[120px] p-2 text-lg disabled:bg-transparent disabled:cursor-not-allowed"
          ></textarea>
          <div
            class="flex justify-end items-center gap-4 pt-4 border-t border-slate-100"
          >
            {#if commentError}
              <p class="text-red-500 font-bold text-xs animate-pulse flex-1 text-right">
                {commentError}
              </p>
            {:else}
              <p class="text-[10px] text-slate-500 font-bold uppercase">
                تذكر أن تلتزم بقواعد المجتمع التعليمي
              </p>
            {/if}
            <button
              on:click={submitComment}
              disabled={!newComment.trim() || !$userStore.name || submitting}
              class="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-20 disabled:cursor-not-allowed disabled:hover:bg-indigo-600 text-white px-10 py-3 rounded-2xl font-bold text-sm transition-all active:scale-95 flex items-center gap-2"
            >
              <span>{submitting ? 'جاري الإرسال...' : 'إرسال'}</span>
              <Send size={16} />
            </button>
          </div>
        </div>

        <div class="grid gap-4">
          {#each comments as comment (comment.comment_id)}
            <div
              class="bg-slate-50 border border-slate-200 p-6 rounded-[1.5rem] hover:bg-slate-100 transition-all group"
            >
              <div class="flex gap-5">
                <a
                  href={$userStore.name && comment.user?.name?.trim().toLowerCase() === $userStore.name.trim().toLowerCase() ? '/profile' : `/profile/${comment.user_id}`}
                  class="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-black text-xl shadow-lg shadow-indigo-500/10 overflow-hidden hover:ring-2 hover:ring-indigo-400 transition-all cursor-pointer flex-shrink-0"
                >
                  {#if $userStore.name && comment.user?.name?.trim().toLowerCase() === $userStore.name.trim().toLowerCase()}
                    <img
                      src={$userStore.profilePicture}
                      alt="Me"
                      class="w-full h-full object-cover"
                    />
                  {:else if comment.user?.profile_picture_url}
                    <img
                      src={comment.user.profile_picture_url}
                      alt={comment.user.name}
                      class="w-full h-full object-cover"
                    />
                  {:else}
                    <span class="uppercase">
                      {comment.user?.name?.[0] || "U"}
                    </span>
                  {/if}
                </a>
                <div class="flex-1 space-y-2">
                  <div class="flex justify-between items-center">
                    <a 
                      href={$userStore.user_id && comment.user_id === $userStore.user_id ? '/profile' : `/profile/${comment.user_id}`} 
                      class="text-indigo-400 font-bold text-sm hover:underline cursor-pointer"
                    >
                      {comment.user?.name || "طالب مجهول"}
                    </a>
                    <span
                      class="text-[10px] text-slate-600 font-bold tracking-tighter uppercase"
                    >
                      {new Date(comment.submission_time).toLocaleTimeString(
                        "ar-EG",
                      )}
                    </span>
                  </div>
                  
                  {#if editingCommentId === comment.comment_id}
                    <div class="mt-2 flex flex-col gap-2">
                      <textarea
                        bind:value={editingCommentText}
                        class="w-full bg-white border border-slate-200 rounded-xl p-3 text-slate-800 resize-none outline-none focus:ring-2 ring-indigo-500/20"
                        rows="3"
                      ></textarea>
                      <div class="flex justify-end gap-2">
                        <button 
                          on:click={cancelEdit}
                          class="p-2 text-slate-500 hover:bg-slate-200 rounded-lg transition-all"
                          title="إلغاء"
                        >
                          <X size={16} />
                        </button>
                        <button 
                          on:click={() => updateComment(comment.comment_id)}
                          disabled={updatingComment}
                          class="p-2 bg-indigo-500 text-white hover:bg-indigo-600 rounded-lg transition-all disabled:opacity-50"
                          title="حفظ"
                        >
                          {#if updatingComment}
                            <Loader2 size={16} class="animate-spin" />
                          {:else}
                            <Check size={16} />
                          {/if}
                        </button>
                      </div>
                    </div>
                  {:else}
                    <p class="text-slate-700 leading-relaxed text-base">
                      {comment.text}
                    </p>
                  {/if}
                </div>

                <div class="flex flex-col gap-2">
                  {#if $userStore.role?.toString().toLowerCase() === "manager"}
                    <button
                      on:click={() => deleteComment(comment.comment_id)}
                      class="text-slate-300 hover:text-red-500 p-2 hover:bg-red-50 rounded-xl transition-all self-start"
                      title="حذف التعليق"
                    >
                      <Trash2 size={16} />
                    </button>
                  {/if}
                  {#if $userStore.user_id === comment.user_id && editingCommentId !== comment.comment_id}
                    <button
                      on:click={() => startEdit(comment)}
                      class="text-slate-300 hover:text-indigo-500 p-2 hover:bg-indigo-50 rounded-xl transition-all self-start"
                      title="تعديل التعليق"
                    >
                      <Edit2 size={16} />
                    </button>
                  {/if}
                </div>
              </div>
            </div>
          {:else}
            <div
              class="py-20 text-center bg-slate-50 border border-dashed border-slate-200 rounded-[2rem]"
            >
              <MessageCircle size={48} class="mx-auto text-slate-800 mb-4" />
              <p
                class="text-xs font-black uppercase tracking-widest text-slate-600"
              >
                كن أول من يفتح باب النقاش
              </p>
            </div>
          {/each}
        </div>
      </section>
    </main>
  {:else}
    <div
      class="flex flex-col items-center justify-center h-screen gap-6 opacity-40 grayscale"
    >
      <PlayCircle size={100} strokeWidth={0.5} />
      <p class="font-black tracking-[0.5em] uppercase text-sm">
        404 Content Not Accessible
      </p>
    </div>
  {/if}
  {#if showQuizModal && lecture?.quiz_id && lecture?.course_id}
  <QuizModal
    quizId={lecture.quiz_id}
    courseId={lecture.course_id}
    on:close={() => (showQuizModal = false)}
  />
{/if}
</div>

<style>
  :global(.custom-scrollbar::-webkit-scrollbar) {
    width: 4px;
  }
  :global(.custom-scrollbar::-webkit-scrollbar-track) {
    background: transparent;
  }
  :global(.custom-scrollbar::-webkit-scrollbar-thumb) {
    background: rgba(99, 102, 241, 0.1);
    border-radius: 20px;
  }
  :global(.custom-scrollbar:hover::-webkit-scrollbar-thumb) {
    background: rgba(99, 102, 241, 0.3);
  }
</style>
