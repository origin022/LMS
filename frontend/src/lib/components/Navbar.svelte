<script lang="ts">
  import { sidebarOpen, userStore } from '$lib/authStore';
  import DonationButton from './DonationButton.svelte';
  import { apiFetch } from "$lib/api";

  $: user = $userStore;
  $: isGuest =
    user.loading ||
    (!user.name && !user.role) ||
    (user.name && user.name.toLowerCase() === "guest");

  async function logout() {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch (e) {
      console.error("Logout failed:", e);
    } finally {
      userStore.set({ name: "", profilePicture: "", role: "", user_id: null, loading: false });
      if (typeof window !== "undefined") {
        localStorage.removeItem("user_session");
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }
  }
</script>

<header class="h-16 bg-white/80 backdrop-blur-md border-b border-gray-100 flex items-center justify-between px-4 md:px-8 sticky top-0 z-40 transition-colors">
  <div class="flex items-center gap-4 md:gap-6">
    <button 
      on:click={() => sidebarOpen.update(n => !n)} 
      class="p-2 bg-gray-50 hover:bg-blue-50 hover:text-blue-600 rounded-xl text-gray-500 transition-all active:scale-95 border border-transparent hover:border-blue-100"
      aria-label="تبديل القائمة الجانبية"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h12m-12 6h16" />
      </svg>
    </button>

    {#if !isGuest}
      <button 
        on:click={logout} 
        class="lg:hidden p-2 bg-red-50 hover:bg-red-100 text-red-500 rounded-xl transition-all active:scale-95 border border-transparent hover:border-red-200 flex items-center"
        aria-label="تسجيل الخروج"
        title="تسجيل الخروج"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 md:h-6 md:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
      </button>
    {/if}

    <a href="/home" class="hidden md:block text-right hover:opacity-80 transition-opacity">
        <h1 class="text-lg font-black text-gray-900 tracking-tight">منصة الجاحظ</h1>
        <p class="text-[9px] text-gray-400 font-bold uppercase tracking-widest -mt-1">نظام التعلم الذكي</p>
    </a>

    <nav class="hidden lg:flex items-center gap-6 mr-4 border-r border-gray-100 pr-6">
      <a href="/home" class="text-sm font-black text-gray-500 hover:text-blue-600 transition-colors">الرئيسية</a>
      <a href="/classrooms" class="text-sm font-black text-gray-500 hover:text-blue-600 transition-colors">المجالات الدراسية</a>
    </nav>
  </div>

  <div class="flex items-center gap-6">
    <DonationButton />
    <div class="h-8 w-px bg-gray-100 hidden sm:block"></div>
    <a href="/home">
      <img 
        src="/llogo.png" 
        alt="Logo" 
        class="h-14 w-auto object-contain hover:scale-105 transition-transform" 
      />
    </a>
  </div>
</header>