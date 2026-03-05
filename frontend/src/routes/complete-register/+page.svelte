<script lang="ts">
  import { page } from '$app/stores';
  import { apiFetch } from '$lib/api';
  import { goto } from '$app/navigation';
  import { fly, fade } from 'svelte/transition';

  let token = $page.url.searchParams.get('token');
  
  let name = '';
  let password = '';
  let phone = '';
  let loading = false;
  let errorMessage = '';

  async function completeRegistration(): Promise<void> {
    if (!name || !password || !phone) {
      errorMessage = "جميع الحقول مطلوبة";
      return;
    }

    loading = true;
    errorMessage = '';

    try {
      const res = await apiFetch('/register-by-token', {
        method: 'POST',
        body: JSON.stringify({ name, password, phone, token })
      });

      if (res.ok) {
        await goto('/login?msg=success');
      } else {
        const err = await res.json();
        errorMessage = err.detail || "فشلت عملية التسجيل، قد يكون الرابط منتهياً";
      }
    } catch (e) {
      errorMessage = "خطأ في الاتصال بالخادم، يرجى المحاولة لاحقاً";
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-6" dir="rtl">
  
  <div class="mb-8 flex flex-col items-center" in:fly={{ y: -20, duration: 800 }}>
    <div class="w-20 h-20 bg-blue-600 rounded-[2rem] flex items-center justify-center shadow-xl shadow-blue-200 mb-4">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A10.003 10.003 0 0012 3a10.003 10.003 0 00-6.912 2.747l-.054.09M12 11a10.003 10.003 0 005.462-1.547l.054-.09M12 11V3m0 8c0 3.517 1.009 6.799 2.753 9.571m3.44-2.04l-.054-.09A10.003 10.003 0 0112 21" />
      </svg>
    </div>
    <h1 class="text-2xl font-black text-slate-900 tracking-tight">نظام الإدارة المركزية</h1>
  </div>

  <div class="max-w-md w-full bg-white rounded-[3rem] p-10 shadow-2xl shadow-slate-200/50 border border-slate-100" in:fly={{ y: 20, duration: 800, delay: 200 }}>
    <div class="text-right mb-10">
      <h2 class="text-xl font-black text-slate-800">تفعيل حساب المسؤول</h2>
      <p class="text-slate-400 text-xs font-bold mt-2 leading-relaxed">أهلاً بك في الفريق الإداري، يرجى استكمال بياناتك الشخصية لبدء العمل.</p>
    </div>

    {#if errorMessage}
      <div class="bg-red-50 text-red-600 p-4 rounded-2xl text-[11px] font-black mb-6 text-center border border-red-100" in:fade>
        {errorMessage}
      </div>
    {/if}

    <div class="space-y-5">
      <div class="relative group">
        <label for="name" class="text-[10px] font-black text-slate-400 mr-4 mb-1 block uppercase tracking-wider cursor-pointer">الاسم الكامل</label>
        <input 
          id="name"
          bind:value={name} 
          type="text" 
          placeholder="أدخل اسمك الثلاثي" 
          class="w-full p-5 bg-slate-50 border-2 border-transparent rounded-[1.5rem] outline-none font-bold text-slate-700 transition-all focus:bg-white focus:border-blue-600/20 focus:ring-4 focus:ring-blue-50" 
        />
      </div>

      <div class="relative group">
        <label for="phone" class="text-[10px] font-black text-slate-400 mr-4 mb-1 block uppercase tracking-wider cursor-pointer">رقم الهاتف الرسمي</label>
        <input 
          id="phone"
          bind:value={phone} 
          type="text" 
          placeholder="07XXXXXXXX" 
          class="w-full p-5 bg-slate-50 border-2 border-transparent rounded-[1.5rem] outline-none font-bold text-slate-700 transition-all focus:bg-white focus:border-blue-600/20 focus:ring-4 focus:ring-blue-50" 
        />
      </div>

      <div class="relative group">
        <label for="password" class="text-[10px] font-black text-slate-400 mr-4 mb-1 block uppercase tracking-wider cursor-pointer">كلمة المرور</label>
        <input 
          id="password"
          bind:value={password} 
          type="password" 
          placeholder="••••••••" 
          class="w-full p-5 bg-slate-50 border-2 border-transparent rounded-[1.5rem] outline-none font-bold text-slate-700 transition-all focus:bg-white focus:border-blue-600/20 focus:ring-4 focus:ring-blue-50" 
        />
      </div>

      <button 
        on:click={completeRegistration} 
        disabled={loading}
        class="w-full py-5 bg-slate-900 text-white rounded-[1.5rem] font-black text-sm shadow-xl shadow-slate-200 hover:bg-blue-600 active:scale-[0.98] transition-all disabled:opacity-50 mt-6 relative overflow-hidden"
      >
        {#if loading}
          <span class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            جاري المعالجة...
          </span>
        {:else}
          إكمال التسجيل والدخول
        {/if}
      </button>
    </div>

    <div class="mt-8 text-center">
      <p class="text-[10px] font-bold text-slate-400">جميع البيانات مشفرة وفق معايير الأمان الدولية</p>
    </div>
  </div>
</div>

<style>
  :global(body) {
    background-color: #F8FAFC;
    font-family: 'Inter', 'Noto Sans Arabic', sans-serif;
  }
</style>