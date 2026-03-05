<script lang="ts">
  import { goto } from '$app/navigation';
  import { apiFetch } from '$lib/api';

  let name = '', email = '', password = '', phone = '', roles_id = 1;
  let error = '', success = '', loading = false;

  async function handleRegister() {
    error = ''; success = ''; loading = true;
    try {
      const response = await apiFetch('/register', {
        method: 'POST',
        body: JSON.stringify({ name, email, password, phone, roles_id })
      });

      const data = await response.json();
      if (!response.ok) {
        error = data.detail || 'حدث خطأ أثناء التسجيل';
        return;
      }

      success = 'تم إنشاء الحساب بنجاح! جاري التحويل للوجن...';
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
        <input type="password" placeholder="كلمة المرور" bind:value={password} class="w-full p-2.5 border rounded-lg text-right focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" required />
        
        <div class="flex flex-col">
          <label for="roles" class="block text-xs text-gray-400 mr-1 mb-1">اختر نوع الحساب</label>
          <select id="roles" bind:value={roles_id} class="w-full p-2.5 border rounded-lg text-right bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all cursor-pointer">
            <option value={1}>طالب</option>
            <option value={2}>استاذ</option>
          </select>
        </div>
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