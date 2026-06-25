<script lang="ts">
  import { goto } from "$app/navigation";
  import { apiFetch, extractErrorMessage } from "$lib/api";
  import { userStore } from "$lib/authStore";

  let email = "",
    password = "",
    showPassword = false,
    error = "",
    loading = false;

  async function login(): Promise<void> {
    error = "";
    loading = true;
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await apiFetch("/auth/login", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        error = extractErrorMessage(data.detail) || "فشل تسجيل الدخول";
        loading = false;
        return;
      }

      const userData = {
        name: data.name,
        profilePicture: data.profile_picture || "/default-avatar.png",
        role: data.roles_name || data.role,
        user_id: data.user_id,
        loading: false,
      };

      userStore.set(userData);

      if (typeof window !== "undefined") {
        localStorage.setItem("user_session", JSON.stringify(userData));
        if (data.access_token) {
          localStorage.setItem("token", data.access_token);
        }
      }

      const normalizedRole = (userData.role || "").toLowerCase().trim();
      const isAdmin = normalizedRole === "admin";
      const targetPath = isAdmin ? "/admin" : "/home";

      await goto(targetPath, {
        invalidateAll: true,
        replaceState: true,
      });
    } catch (err) {
      error = "فشل الاتصال بالخادم";
      loading = false;
    }
  }

  async function guestLogin(): Promise<void> {
    // Clear any existing session data first
    if (typeof window !== "undefined") {
      localStorage.removeItem("user_session");
      localStorage.removeItem("token");
    }

    userStore.set({
      name: "Guest",
      profilePicture: "",
      role: "",
      user_id: null,
      loading: false,
    });
    
    // Direct navigation, (app) layout will see no cookies and treat as guest
    await goto("/home", { invalidateAll: true });
  }
</script>

<div
  class="min-h-screen flex items-center justify-center bg-gray-50/50"
  dir="rtl"
>
  <div
    class="bg-white w-[27rem] py-8 px-9 rounded-[2.5rem] shadow-2xl shadow-gray-200/50 text-center border border-gray-100"
  >
    <div class="mb-0 relative">
      <div class="h-24 flex items-center justify-center -mt-6">
        <img
          src="/llogo.png"
          alt="Logo"
          class="w-48 h-48 object-contain transform scale-150 drop-shadow-sm"
        />
      </div>

      <h1
        class="text-3xl font-black text-gray-800 font-sans tracking-tight mt-8"
      >
        مرحباً بك مجدداً
      </h1>
      <p class="text-gray-500 text-base mt-2 font-bold">سجل دخولك للمتابعة</p>
    </div>

    {#if typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('verified') === 'true'}
      <div class="bg-green-50 text-green-600 p-5 rounded-2xl mb-6 text-sm font-black border border-green-100 mt-6">
        {#if new URLSearchParams(window.location.search).get('role') === '4'}
          تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.
        {:else}
          تم تأكيد هويتك، يرجى انتظار تفعيل الحساب من قبل الإدارة.
        {/if}
      </div>
    {/if}

    {#if error}
      <div
        class="bg-red-50 text-red-600 p-4 rounded-2xl mb-6 text-sm font-black border border-red-100 flex items-center justify-center gap-2 mt-4"
      >
        {error}
      </div>
    {/if}

    <form on:submit|preventDefault={login} class="space-y-4 mt-6">
      <div class="space-y-2">
        <input
          type="email"
          placeholder="البريد الإلكتروني"
          bind:value={email}
          class="w-full p-4.5 bg-gray-50 border border-gray-100 rounded-2xl text-right focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all font-bold text-base shadow-inner"
          required
        />
      </div>

      <div class="space-y-2 relative group">
        <input
          type={showPassword ? "text" : "password"}
          placeholder="كلمة المرور"
          bind:value={password}
          class="w-full p-4.5 bg-gray-50 border border-gray-100 rounded-2xl text-right focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all font-bold text-base shadow-inner pl-14"
          required
        />
        <button
          type="button"
          class="absolute left-3 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-blue-600 transition-colors bg-white/50 rounded-xl hover:bg-white"
          on:click={() => (showPassword = !showPassword)}
        >
          {#if showPassword}
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
          {/if}
        </button>
      </div>

      <div class="pt-4 space-y-3">
        <button
          type="submit"
          disabled={loading}
          class="w-full bg-blue-600 hover:bg-blue-700 text-white py-4.5 rounded-2xl transition-all font-black disabled:bg-blue-300 shadow-lg shadow-blue-100 active:scale-[0.98] text-lg"
        >
          {#if loading}
            <span class="flex items-center justify-center gap-2 text-base">
              <div
                class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"
              ></div>
              جاري التحقق...
            </span>
          {:else}
            تسجيل الدخول
          {/if}
        </button>

        <button
          type="button"
          on:click={guestLogin}
          class="w-full bg-white border border-gray-200 text-gray-400 py-4 rounded-2xl transition-all hover:bg-gray-50 font-black text-sm active:scale-[0.98]"
        >
          دخول كزائر
        </button>
      </div>
    </form>

    <div class="mt-8 pt-6 border-t border-gray-50">
      <p class="text-sm text-gray-500 font-bold">
        ليس لديك حساب؟
        <a
          href="/regester"
          class="text-blue-600 hover:text-blue-700 font-black transition-colors underline-offset-4 hover:underline"
        >
          ابدأ الآن مجاناً
        </a>
      </p>
    </div>
  </div>
</div>
