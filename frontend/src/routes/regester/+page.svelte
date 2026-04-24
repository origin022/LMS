<script lang="ts">
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { apiFetch } from '$lib/api';

  let name = '', email = '', password = '', phone = '', roles_id = '';
  let departments: any[] = [];
  let selectedDepartmentId = '';
  let error = '', success = '', loading = false, showPassword = false;

  onMount(async () => {
    try {
      const res = await apiFetch('/departments');
      if (res.ok) departments = await res.json();
    } catch (e) {
      console.error('Failed to fetch departments', e);
    }
  });

  async function handleRegister() {
    if (roles_id == '3' && !selectedDepartmentId) {
      error = 'يرجى اختيار القسم التابع له أولاً';
      return;
    }
    error = ''; success = ''; loading = true;
    try {
      const response = await apiFetch('/register', {
        method: 'POST',
        body: JSON.stringify({ 
          name, 
          email, 
          password, 
          phone, 
          roles_id: parseInt(roles_id),
          department_id: roles_id == '3' ? parseInt(selectedDepartmentId) : null
        })
      });

      const data = await response.json();
      if (!response.ok) {
        error = data.detail || 'حدث خطأ أثناء التسجيل';
        return;
      }

      success = 'تم إنشاء الحساب بنجاح! جاري  تحويلك الى صقحة تسجيل الدخول...';
      setTimeout(() => goto('/login'), 2000);
    } catch (err) {
      error = 'تعذر الاتصال بالخادم';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-100 p-4" dir="rtl">
  <div class="bg-white w-full max-w-4xl flex flex-col md:flex-row rounded-2xl shadow-lg overflow-hidden border border-gray-200">
    
    <div class="md:w-1/2 bg-blue-50 flex flex-col items-center justify-center p-4 border-b md:border-b-0 md:border-l border-gray-100 overflow-hidden">
    <img src="/llogo.png" alt="Logo" class="w-full h-auto max-w-[500px] object-contain mb-4 drop-shadow-md scale-125" />
    <h2 class="text-blue-700 text-2xl font-bold hidden md:block">أهلاً بك في منصتنا</h2>
</div>

    <div class="md:w-1/2 p-8 flex flex-col justify-center">
      <h1 class="text-2xl font-bold mb-6 text-center md:text-right text-gray-800">إنشاء حساب جديد</h1>

      {#if error}
        <div class="bg-red-100 text-red-600 p-2 rounded mb-4 text-sm font-medium text-center border border-red-200">{error}</div>
      {/if}

      {#if success}
        <div class="bg-blue-100 text-blue-700 p-2 rounded mb-4 text-sm font-medium text-center border border-blue-200">{success}</div>
      {/if}

      <div class="space-y-3">
        <input type="text" placeholder="الاسم " bind:value={name} class="w-full p-2.5 border rounded-lg text-right focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" required />
        <input type="email" placeholder="البريد الإلكتروني" bind:value={email} class="w-full p-2.5 border rounded-lg text-right focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" required />
        <input type="tel" placeholder="رقم الهاتف" bind:value={phone} class="w-full p-2.5 border rounded-lg text-right focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" required />
        <div class="relative group">
          <input 
            type={showPassword ? "text" : "password"} 
            placeholder="كلمة المرور" 
            bind:value={password} 
            class="w-full p-2.5 border rounded-lg text-right focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all pl-10" 
            required 
          />
          <button
            type="button"
            class="absolute left-2 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-blue-600 transition-colors"
            on:click={() => (showPassword = !showPassword)}
          >
            {#if showPassword}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
            {/if}
          </button>
        </div>
        
        <div class="flex flex-col">
          <label for="roles" class="block text-xs text-gray-400 mr-1 mb-1">اختر نوع الحساب</label>
          <select id="roles" bind:value={roles_id} class="w-full p-2.5 border rounded-lg text-right bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all cursor-pointer">
            <option value="">-- اختر --</option>
            <option value="4">طالب</option>
            <option value="3">استاذ</option>
          </select>
        </div>

        {#if roles_id == '3'}
          <div in:fly={{ y: -10, duration: 300 }} class="flex flex-col">
            <label for="department" class="block text-xs text-blue-500 font-bold mr-1 mb-1 mt-1">اختر القسم الخاص بك</label>
            <select id="department" bind:value={selectedDepartmentId} class="w-full p-2.5 border border-blue-200 rounded-lg text-right bg-blue-50/50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all cursor-pointer font-bold">
              <option value="">-- اختر القسم --</option>
              {#each departments as dep}
                <option value={dep.department_id}>{dep.name}</option>
              {/each}
            </select>
          </div>
        {/if}
      </div>

      <button 
        on:click={handleRegister} 
        disabled={loading} 
        class="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg mt-8 transition-all font-bold shadow-md active:scale-95 disabled:opacity-50"
      >
        {loading ? 'جاري المعالجة...' : 'تأكيد التسجيل'}
      </button>

      <div class="mt-6 text-sm text-gray-600 text-center">
        لديك حساب بالفعل؟ 
        <a href="/login" class="text-blue-600 hover:underline font-bold">تسجيل الدخول</a>
      </div>
    </div>
  </div>
</div>