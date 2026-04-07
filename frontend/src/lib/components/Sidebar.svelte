<script lang="ts">
  import { userStore, sidebarOpen } from "$lib/authStore";
  import { goto } from "$app/navigation";
  import { apiFetch } from "$lib/api";

  $: user = $userStore;
  $: role = user.role ? String(user.role).trim().toLowerCase() : "";

  $: isAdmin = role === "admin";
  $: isManager = role === "manager";
  $: isTeacher = role === "teacher";
  $: isStudent = role === "student";

  $: isGuest =
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
      }
      goto("/login");
    }
  }
</script>

<aside
  class="bg-white border-l border-gray-100 shadow-sm transition-all duration-300 flex flex-col h-screen {$sidebarOpen
    ? 'w-72'
    : 'w-0 overflow-hidden'}"
  dir="rtl"
>
  <div class="p-8 flex flex-col items-center border-b border-gray-50">
    {#if isGuest}
      <div class="w-20 h-20 bg-gray-50 rounded-[2rem] flex items-center justify-center mb-4 text-gray-300">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
      <h2 class="font-black text-gray-800 text-sm">وضع الزائر</h2>
      <button on:click={() => goto("/login")} class="mt-4 px-6 py-2 bg-blue-600 text-white text-xs rounded-xl font-black">
        تسجيل الدخول
      </button>
    {:else}
      <div class="relative">
        {#if user.profilePicture}
          <img
            src={user.profilePicture}
            alt="profile"
            crossorigin="use-credentials"
            class="w-24 h-24 rounded-[2rem] object-cover ring-4 {isAdmin ? 'ring-amber-400' : isManager ? 'ring-purple-400' : isTeacher ? 'ring-blue-400' : isStudent ? 'ring-emerald-400' : 'ring-blue-100'} shadow"
          />
        {:else}
          <div class="w-24 h-24 rounded-[2rem] flex items-center justify-center {isAdmin ? 'bg-amber-50' : isManager ? 'bg-purple-50' : isStudent ? 'bg-emerald-50' : 'bg-blue-50'} ring-4 {isAdmin ? 'ring-amber-400' : isManager ? 'ring-purple-400' : isTeacher ? 'ring-blue-400' : isStudent ? 'ring-emerald-400' : 'ring-blue-100'}">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 {isAdmin ? 'text-amber-500' : isManager ? 'text-purple-500' : isStudent ? 'text-emerald-500' : 'text-blue-500'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        {/if}
      </div>
      <h2 class="mt-4 font-black text-gray-800 text-lg">{user.name || "مستخدم"}</h2>
      <span class="text-xs mt-2 px-4 py-1 rounded-full border {isAdmin ? 'bg-amber-50 text-amber-600 border-amber-200' : isManager ? 'bg-purple-50 text-purple-600 border-purple-200' : isTeacher ? 'bg-blue-50 text-blue-600 border-blue-200' : isStudent ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-gray-50 text-gray-600 border-gray-200'}">
        {isAdmin ? "ادمن" : isManager ? "مدير" : isTeacher ? "أستاذ" : isStudent ? "متعلم" : "مستخدم"}
      </span>
    {/if}
  </div>

  <nav class="flex-1 p-6 space-y-3 overflow-y-auto">
    {#if isTeacher || isStudent}
      <button
        on:click={() => goto("/profile")}
        class="w-full text-right px-4 py-3 text-gray-600 hover:text-blue-600 font-black text-sm transition-colors"
      >
        صفحتي
      </button>
    {/if}

    <a href="/home" class="block px-4 py-3 text-gray-600 hover:text-blue-600 font-black text-sm transition-colors">
      الرئيسية
    </a>

    {#if isStudent}
      <a href="/my-lectures" class="block px-4 py-3 text-gray-600 hover:text-emerald-600 font-black text-sm transition-colors">
        محاضراتي
      </a>
    {/if}
    {#if isTeacher}
      <a href="/courses" class="block px-4 py-3 text-gray-600 hover:text-blue-600 font-black text-sm transition-colors">
        كورساتي
      </a>
    {/if}

    <a href="/classrooms" class="block px-4 py-3 text-gray-600 hover:text-blue-600 font-black text-sm transition-colors">
      المجالات
    </a>
  </nav>

  <div class="p-6 border-t border-gray-50 space-y-3">
    {#if isAdmin}
      <button on:click={() => goto("/admin")} class="w-full py-3 bg-amber-500 text-white rounded-xl font-black shadow-lg shadow-amber-100 active:scale-95 transition-transform">
        لوحة التحكم
      </button>
    {/if}

    {#if isManager}
      <button on:click={() => goto("/manager")} class="w-full py-3 bg-purple-600 text-white rounded-xl font-black shadow-lg shadow-purple-100 active:scale-95 transition-transform">
        لوحة المدير
      </button>
    {/if}

    {#if isTeacher}
      <button on:click={() => goto("/teacher")} class="w-full py-3 bg-blue-600 text-white rounded-xl font-black shadow-lg shadow-blue-100 active:scale-95 transition-transform">
        نشر المحاضرة
      </button>
    {/if}

    {#if !isGuest}
      <button on:click={logout} class="w-full py-3 text-red-500 border border-red-200 rounded-xl font-black text-sm hover:bg-red-50 transition-colors">
        تسجيل الخروج
      </button>
    {/if}
  </div>
</aside>

<style>
  :global(aside) {
    user-select: none;
  }
</style>