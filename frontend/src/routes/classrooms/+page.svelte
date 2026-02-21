<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let classrooms: any[] = [];
  let userName: string = '';
  let profilePicture: string = '/static/1.png'; // مؤقت
  let loading = true;
  let sidebarOpen = true;

  const BASE_URL = 'http://127.0.0.1:5173/api/v1/classrooms';

  async function loadData() {
    try {
      const [profileRes, classRes] = await Promise.all([
        fetch(`${BASE_URL}/profile`, { credentials: 'include' }),
        fetch(`${BASE_URL}/classrooms`, { credentials: 'include' })
      ]);

      if (profileRes.status === 401 || classRes.status === 401) {
        goto('/');
        return;
      }

      if (profileRes.ok) {
        const profile = await profileRes.json();
        userName = profile.name;
      }

      if (classRes.ok) {
        classrooms = await classRes.json();
      }

    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  async function logout() {
    await fetch(`${BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });
    goto('/');
  }

  onMount(loadData);
</script>

<div class="h-screen flex bg-gray-100" dir="rtl">

  <!-- Sidebar -->
  <div class={`bg-white shadow-xl transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'}`}>
    <div class="flex flex-col h-full p-6">

      <!-- Profile -->
      <div class="flex flex-col items-center mb-8">
        <img src={profilePicture}
             class="w-24 h-24 rounded-full object-cover border-4 border-blue-500" />
        <h2 class="mt-4 font-bold text-lg">{userName}</h2>
      </div>

      <!-- Menu -->
      <div class="flex flex-col gap-3 flex-1">
        <button class="bg-gray-100 py-2 rounded-lg font-semibold">
          بروفايل
        </button>

        <button class="bg-blue-600 text-white py-2 rounded-lg font-semibold">
          كورساتي
        </button>
      </div>

      <button on:click={logout}
              class="bg-red-500 text-white py-2 rounded-lg font-semibold">
        تسجيل خروج
      </button>
    </div>
  </div>

  <!-- Main -->
  <div class="flex-1 p-10 overflow-y-auto">

    <!-- Toggle Button -->
    <button
      on:click={() => sidebarOpen = !sidebarOpen}
      class="mb-6 bg-blue-600 text-white px-4 py-2 rounded-lg">
      ☰
    </button>

    {#if loading}
      <div>جاري التحميل...</div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each classrooms as classroom}
          <div class="bg-white rounded-2xl shadow-lg p-6 hover:shadow-2xl transition">
            <h3 class="text-xl font-bold mb-2">
              {classroom.class_name}
            </h3>
            <p class="text-gray-500">
              ID: {classroom.class_id}
            </p>
          </div>
        {/each}
      </div>
    {/if}

  </div>

</div>