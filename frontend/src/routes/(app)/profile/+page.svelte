<script lang="ts">
  import { onMount } from "svelte";
  import { apiFetch, BASE_URL, FILE_URL } from "$lib/api";
  import { userStore } from "$lib/authStore";
  import { 
    User as UserIcon, Camera, Edit3, Save, X, 
    Mail, Shield, Award, Calendar, Loader2,
    CheckCircle2, BookOpen, PlusCircle, ArrowRight
  } from "lucide-svelte";
  import { goto } from "$app/navigation";
  import { fade, fly, scale } from "svelte/transition";

  interface UserProfile {
    name: string;
    bio: string;
    picture: boolean;
    role: string;
  }

  interface Course {
    course_id: number;
    name: string;
    course_thumbnail?: string;
    teacher_name?: string;
  }

  let profile: UserProfile | null = null;
  let courses: Course[] = [];
  let loading = true;
  let coursesLoading = false;
  let editing = false;
  let saving = false;
  let message = { text: "", type: "" };

  let editName = "";
  let editBio = "";
  let fileInput: HTMLInputElement;
  let uploadLoading = false;

  async function loadProfile() {
    loading = true;
    try {
      const res = await apiFetch("/profile");
      if (res.ok) {
        profile = await res.json();
        if (profile) {
          editName = profile.name;
          editBio = profile.bio;
          loadCourses();
        }
      }
    } catch (err) {
      showMsg("فشل تحميل البيانات الشخصية", "error");
    } finally {
      loading = false;
    }
  }

  async function loadCourses() {
    if (!profile) return;
    coursesLoading = true;
    try {
      const role = (profile.role || "").toLowerCase();
      const isStudent = role.includes("student") || role.includes("طالب");
      
      const endpoint = isStudent ? "/enrollments" : "/teacher/courses";
      const res = await apiFetch(endpoint);
      
      if (res.ok) {
        const data = await res.json();
        if (isStudent) {
          // data is list of enrollments
          courses = data.map((e: any) => e.course).slice(0, 4);
        } else {
          // data is list of courses
          courses = data.slice(0, 4);
        }
      }
    } catch (err) {
      console.error("Error loading courses:", err);
    } finally {
      coursesLoading = false;
    }
  }

  function showMsg(text: string, type: "success" | "error" = "success") {
    message = { text, type };
    setTimeout(() => { message = { text: "", type: "" }; }, 4000);
  }

  async function handleSave() {
    if (!profile) return;
    saving = true;
    try {
      const res = await apiFetch("/profile", {
        method: "PATCH",
        body: JSON.stringify({
          name: editName,
          bio: editBio
        })
      });
      if (res.ok) {
    const updated = await res.json();
    
    profile.name = updated.name;
    profile.bio = updated.bio;
    profile.picture = updated.has_picture; 

    userStore.update(u => ({
        ...u,
        name: updated.name
    }));

    editing = false;
    showMsg("تم تحديث الملف الشخصي بنجاح ✅");
}
      else {
        const errData = await res.json();
        showMsg(errData.detail || "فشل تحديث البيانات", "error");
      }
    } catch (err) {
      showMsg("حدث خطأ غير متوقع", "error");
    } finally {
      saving = false;
    }
  }

  async function handleFileUpload(e: Event) {
    const target = e.target as HTMLInputElement;
    if (!target.files?.[0]) return;

    const file = target.files[0];
    if (!file.type.startsWith("image/")) {
      return showMsg("يرجى اختيار ملف صورة صحيح", "error");
    }

    uploadLoading = true;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await apiFetch("/profile/picture", {
        method: "POST",
        body: formData,
      });


      if (res.ok) {
    if (profile) profile.picture = true;
    
    const newPicUrl = `${BASE_URL}/picture/me?t=${Date.now()}`;

    userStore.update(u => ({
        ...u,
        profilePicture: newPicUrl
    }));

    showMsg("تم تغيير الصورة بنجاح ✅");
    
    const img = document.getElementById('profile-pic') as HTMLImageElement;
    if (img) img.src = newPicUrl;
}

  else {
        showMsg("فشل رفع الصورة", "error");
      }
    } catch (err) {
      showMsg("حدث خطأ أثناء الرفع", "error");
    } finally {
      uploadLoading = false;
    }
  }

  onMount(loadProfile);
</script>

<div class="min-h-screen bg-slate-50 text-slate-800 font-sans p-4 lg:p-12" dir="rtl">
  
  {#if message.text}
    <div 
      in:fly={{ y: -20 }} 
      out:fade
      class="fixed top-8 left-1/2 -translate-x-1/2 z-[1000] px-6 py-4 rounded-2xl font-black text-sm shadow-2xl flex items-center gap-3 {message.type === 'error' ? 'bg-red-500/90' : 'bg-indigo-600/90'} backdrop-blur-xl text-white border border-white/10"
    >
      {#if message.type === 'success'}
        <CheckCircle2 size={20} />
      {/if}
      {message.text}
    </div>
  {/if}

  {#if loading}
    <div class="flex h-[60vh] items-center justify-center">
      <div class="relative flex items-center justify-center">
        <div class="absolute w-24 h-24 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
        <UserIcon class="w-10 h-10 text-indigo-500/50" />
      </div>
    </div>
  {:else if profile}
    <main class="max-w-4xl mx-auto space-y-8" in:fade>
      
      <section class="relative bg-white border border-slate-200 rounded-[3rem] p-8 md:p-12 shadow-sm overflow-hidden group">
        <div class="absolute -top-24 -right-24 w-64 h-64 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px] pointer-events-none"></div>

        <div class="relative flex flex-col md:flex-row items-center gap-10">
          <div class="relative group/avatar">
            <div class="w-40 h-40 md:w-48 md:h-48 rounded-[2.5rem] bg-slate-100 p-1 shadow-sm overflow-hidden">
              <div class="w-full h-full rounded-[2.3rem] overflow-hidden bg-white flex items-center justify-center border border-slate-200 relative">
                {#if profile.picture}
                  <img 
                    id="profile-pic"
                    src={$userStore.profilePicture || `${BASE_URL}/picture/me`} 
                    alt="Profile" 
                    class="w-full h-full object-cover"
                  />
                {:else}
                  <UserIcon size={64} class="text-slate-400" />
                {/if}
                
                {#if uploadLoading}
                   <div class="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center">
                     <Loader2 size={32} class="animate-spin text-indigo-500" />
                   </div>
                {/if}
              </div>
            </div>
            
            <button 
              on:click={() => fileInput.click()}
              class="absolute -bottom-2 -left-2 p-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl shadow-xl transition-all active:scale-90 border border-white/20 group-hover:scale-110"
              title="تغيير الصورة"
            >
              <Camera size={20} />
            </button>
            <input 
              type="file" 
              bind:this={fileInput} 
              on:change={handleFileUpload} 
              class="hidden" 
              accept="image/*"
            />
          </div>

          <div class="flex-1 text-center md:text-right space-y-4">
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-black uppercase tracking-widest italic">
              <Shield size={14} />
              {profile.role || 'طالب المنصة'}
            </div>
            
            {#if !editing}
              <h1 class="text-4xl md:text-5xl font-black text-slate-900 leading-tight italic drop-shadow-sm">
                {profile.name}
              </h1>
            {:else}
              <input 
                bind:value={editName}
                class="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 text-3xl font-black text-slate-900 italic outline-none focus:ring-2 ring-indigo-500/50 transition-all"
                placeholder="الاسم الكامل"
              />
            {/if}

            
          </div>

          <div class="flex flex-col gap-3">
             {#if !editing}
               <button 
                 on:click={() => editing = true}
                 class="px-8 py-4 bg-white hover:bg-slate-50 border border-slate-200 rounded-3xl text-slate-700 font-bold transition-all active:scale-95 flex items-center gap-3 shadow-sm"
               >
                 <Edit3 size={18} />
                 تعديل الملف
               </button>
             {:else}
               <div class="flex gap-2" in:scale>
                  <button 
                    on:click={handleSave}
                    disabled={saving}
                    class="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 rounded-3xl text-white font-bold transition-all active:scale-95 flex items-center gap-3 shadow-xl disabled:opacity-50"
                  >
                    {#if saving}
                      <Loader2 size={18} class="animate-spin" />
                    {:else}
                      <Save size={18} />
                    {/if}
                    حفظ
                  </button>
                  <button 
                  on:click={() => {
                    editing = false;
                    if (profile) {
                      editName = profile.name;
                      editBio = profile.bio;
                    }
                  }}
                    class="p-4 bg-white hover:bg-red-50 border border-slate-200 rounded-2xl text-slate-500 hover:text-red-600 transition-all shadow-sm"
                  >
                    <X size={20} />
                  </button>
               </div>
             {/if}
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 gap-8">
        <section class="bg-white border border-slate-200 rounded-[2.5rem] p-8 md:p-12 space-y-8 shadow-sm">
           <div class="space-y-4">
              <h3 class="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500 italic">نبذة شخصية</h3>
              {#if !editing}
                <p class="text-slate-600 text-lg leading-relaxed whitespace-pre-wrap">
                  {profile.bio || "لا يوجد نبذة شخصية متوفرة حالياً. أضف بعض المعلومات عن نفسك!"}
                </p>
              {:else}
                <textarea 
                  bind:value={editBio}
                  rows="6"
                  class="w-full bg-slate-50 border border-slate-200 rounded-2xl p-6 text-slate-700 text-lg outline-none focus:ring-2 ring-indigo-500/50 transition-all resize-none"
                  placeholder="اكتب شيئاً عن نفسك..."
                ></textarea>
              {/if}
           </div>

           <div class="space-y-6 pt-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="p-2 bg-indigo-500/10 rounded-lg text-indigo-500">
                    <BookOpen size={18} />
                  </div>
                  <h3 class="text-sm font-black text-slate-800 uppercase tracking-wider italic">
                    {profile.role?.toLowerCase().includes("student") || profile.role?.includes("طالب") ? "آخر الكورسات المسجل بها" : "آخر الكورسات المضافة"}
                  </h3>
                </div>
                
                {#if courses.length > 0}
                  <button 
                    on:click={() => profile && goto(profile.role?.toLowerCase().includes("student") || profile.role?.includes("طالب") ? "/my-lectures" : "/teacher")}
                    class="text-[10px] font-black text-indigo-500 hover:text-indigo-600 transition-colors flex items-center gap-1 group/all"
                  >
                    عرض الكل
                    <ArrowRight size={12} class="group-hover/all:translate-x-[-2px] transition-transform" />
                  </button>
                {/if}
              </div>

              {#if coursesLoading}
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {#each Array(4) as _}
                    <div class="h-64 bg-slate-50 border border-slate-100 rounded-[2rem] animate-pulse"></div>
                  {/each}
                </div>
              {:else if courses.length > 0}
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {#each courses as course}
                    <button 
                      on:click={() => goto(`/courses?course_id=${course.course_id}`)}
                      class="flex flex-col group bg-white border border-slate-100 rounded-[2rem] overflow-hidden transition-all hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-1 hover:border-indigo-100"
                    >
                      <div class="h-32 w-full overflow-hidden bg-slate-50 border-b border-slate-100 relative">
                        {#if course.course_thumbnail}
                          <img 
                            src={FILE_URL + course.course_thumbnail} 
                            alt={course.name} 
                            class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
                          />
                        {:else}
                          <div class="w-full h-full flex items-center justify-center bg-indigo-50 text-indigo-500 font-black text-2xl italic">
                            {course.name.charAt(0)}
                          </div>
                        {/if}
                        <div class="absolute bottom-2 left-2 p-2 bg-white/80 backdrop-blur-sm rounded-xl text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity">
                          <ArrowRight size={14} />
                        </div>
                      </div>
                      
                      <div class="p-4 flex-1 flex flex-col justify-between text-right">
                        <h4 class="text-xs font-black text-slate-800 line-clamp-2 leading-snug group-hover:text-indigo-600 transition-colors">
                          {course.name}
                        </h4>
                      </div>
                    </button>
                  {/each}
                </div>
              {:else}
                <div class="p-8 rounded-[2rem] bg-slate-50 border-2 border-dashed border-slate-200 text-center space-y-3">
                  <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mx-auto shadow-sm">
                    <PlusCircle size={24} class="text-slate-300" />
                  </div>
                  <p class="text-xs font-bold text-slate-400 italic">
                    {profile.role?.toLowerCase().includes("student") || profile.role?.includes("طالب") ? "لم تشارك في أي كورس بعد" : "لم تقم بإنشاء أي كورسات بعد"}
                  </p>
                </div>
              {/if}
           </div>
        </section>
      </div>
    </main>
  {/if}
</div>

<style>
  :global(body) {
    background-color: #f8fafc;
  }
</style>