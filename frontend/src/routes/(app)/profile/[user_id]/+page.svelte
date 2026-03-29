<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { apiFetch, BASE_URL } from "$lib/api";
  import { 
    User as UserIcon, Mail, Shield, Award, Calendar, Loader2
  } from "lucide-svelte";
  import { fade } from "svelte/transition";

  interface UserProfilePublic {
    user_id: number;
    name: string;
    bio: string;
    profile_picture_url: string | null;
  }

  let profile: UserProfilePublic | null = null;
  let loading = true;
  let errorMsg = "";

  $: userId = ($page.params as any).user_id;

  async function loadProfile() {
    if (!userId) return;
    loading = true;
    errorMsg = "";
    try {
      const res = await apiFetch(`/users/${userId}`);
      if (res.ok) {
        profile = await res.json();
      } else {
        errorMsg = "المستخدم غير موجود";
      }
    } catch (err) {
      errorMsg = "فشل تحميل البيانات الشخصية";
    } finally {
      loading = false;
    }
  }

  onMount(loadProfile);
</script>

<div class="min-h-screen bg-slate-50 text-slate-800 font-sans p-4 lg:p-12" dir="rtl">
  
  {#if loading}
    <div class="flex h-[60vh] items-center justify-center">
      <div class="relative flex items-center justify-center">
        <div class="absolute w-24 h-24 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
        <UserIcon class="w-10 h-10 text-indigo-500/50" />
      </div>
    </div>
  {:else if errorMsg}
    <div class="flex h-[60vh] items-center justify-center flex-col gap-4 text-slate-500">
      <UserIcon size={64} class="opacity-20" />
      <h2 class="text-2xl font-black italic">{errorMsg}</h2>
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
                {#if profile.profile_picture_url}
                  <img 
                    src={profile.profile_picture_url} 
                    alt="Profile" 
                    class="w-full h-full object-cover"
                  />
                {:else}
                  <UserIcon size={64} class="text-slate-400" />
                {/if}
              </div>
            </div>
          </div>

          <div class="flex-1 text-center md:text-right space-y-4">
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-black uppercase tracking-widest italic">
              <Shield size={14} />
              طالب المنصة
            </div>
            
            <h1 class="text-4xl md:text-5xl font-black text-slate-900 leading-tight italic drop-shadow-sm">
              {profile.name}
            </h1>

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
        </div>
      </section>

      <div class="grid grid-cols-1 gap-8">
        <section class="bg-white border border-slate-200 rounded-[2.5rem] p-8 md:p-12 space-y-8 shadow-sm">
           <div class="space-y-4">
              <h3 class="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-500 italic">نبذة شخصية</h3>
              <p class="text-slate-600 text-lg leading-relaxed whitespace-pre-wrap">
                {profile.bio || "لا يوجد نبذة شخصية متوفرة حالياً."}
              </p>
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
