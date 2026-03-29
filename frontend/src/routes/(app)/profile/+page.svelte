<script lang="ts">
  import { onMount } from "svelte";
  import { apiFetch, BASE_URL } from "$lib/api";
  import { userStore } from "$lib/authStore";
  import { 
    User as UserIcon, Camera, Edit3, Save, X, 
    Mail, Shield, Award, Calendar, Loader2,
    CheckCircle2
  } from "lucide-svelte";
  import { fade, fly, scale } from "svelte/transition";

  interface UserProfile {
    name: string;
    bio: string;
    picture: boolean;
    role: string;
  }

  let profile: UserProfile | null = null;
  let loading = true;
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
        }
      }
    } catch (err) {
      showMsg("فشل تحميل البيانات الشخصية", "error");
    } finally {
      loading = false;
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
                    src={`${BASE_URL}/picture/me`} 
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

            <div class="flex flex-wrap justify-center md:justify-start gap-6 pt-2">
              <div class="flex items-center gap-2 text-slate-500 font-bold text-sm">
                <Award size={18} class="text-amber-500/50" />
                <span>عضو متميز</span>
              </div>
              <div class="flex items-center gap-2 text-slate-500 font-bold text-sm">
                <Calendar size={18} class="text-emerald-500/50" />
                <span>منذ ٢٠٢٤</span>
              </div>
            </div>
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

           <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="p-6 rounded-[2rem] bg-slate-50 border border-slate-200 flex items-center gap-5 group hover:bg-slate-100 transition-all cursor-pointer">
                <div class="p-4 bg-indigo-500/10 rounded-2xl text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-all">
                  <Mail size={24} />
                </div>
                <div class="space-y-1">
                  <p class="text-[10px] font-black text-slate-500 uppercase">البريد الإلكتروني</p>
                  <p class="text-sm font-bold text-slate-800 opacity-80">تم التحقق</p>
                </div>
              </div>
              <div class="p-6 rounded-[2rem] bg-slate-50 border border-slate-200 flex items-center gap-5 group hover:bg-slate-100 transition-all cursor-pointer">
                <div class="p-4 bg-purple-500/10 rounded-2xl text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-all">
                  <Shield size={24} />
                </div>
                <div class="space-y-1">
                  <p class="text-[10px] font-black text-slate-500 uppercase">حالة الحساب</p>
                  <p class="text-sm font-bold text-slate-800 opacity-80">حساب موثق</p>
                </div>
              </div>
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