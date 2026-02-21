<script lang="ts">
  import { goto } from '$app/navigation';

  let email: string = '';
  let password: string = '';
  let error: string = '';
  let loading: boolean = false;

async function login() {
  error = '';
  loading = true;

  try {
    const formData = new URLSearchParams();
    formData.append('username', email); 
    formData.append('password', password);

    const response =await fetch('http://127.0.0.1:5173/api/v1/auth/login', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: formData,
  credentials: 'include'
});

    if (!response.ok) {
      error = 'بيانات الدخول غير صحيحة';
      loading = false;
      return;
    }

    const data = await response.json();

    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
    }

    goto('/classrooms');

  } catch (err) {
    error = 'فشل الاتصال بالسيرفر';
  }

  loading = false;
} 
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-100">
  <div class="bg-white w-96 p-8 rounded-2xl shadow-lg text-center">

    <img 
      src="/logo.png" 
      alt="logo" 
      class="w-24 mx-auto mb-4"
    />

    <h1 class="text-2xl font-bold mb-6">
      أهلاً بك في المنصة
    </h1>

    {#if error}
      <div class="bg-red-100 text-red-600 p-2 rounded mb-4 text-sm">
        {error}
      </div>
    {/if}

    <input
      type="email"
      placeholder="البريد الإلكتروني"
      bind:value={email}
      class="w-full p-2 mb-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
    />

    <input
      type="password"
      placeholder="كلمة المرور"
      bind:value={password}
      class="w-full p-2 mb-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
    />

    <button
      on:click={login}
      disabled={loading}
      class="w-full bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
    >
      {loading ? 'جاري الدخول...' : 'تسجيل الدخول'}
    </button>

  </div>
</div>


