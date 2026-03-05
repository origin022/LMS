<script lang="ts">
  import { onMount } from 'svelte';
  import { userStore } from '$lib/authStore';
  import { apiFetch } from '$lib/api';
  import Sidebar from "$lib/components/Sidebar.svelte";
  import Navbar from "$lib/components/Navbar.svelte";

  let initialized = false;

  async function checkAuth() {
    try {
      const res = await apiFetch('/profile');

      if (!res.ok) {
        setGuest();
        return;
      }

      const data = await res.json();
      
      let imageBlobUrl = '';
      
      // جلب الصورة برمجياً لتجاوز مشكلة 401
      if (data.picture) {
        try {
          const imageRes = await apiFetch('/picture/me');
          if (imageRes.ok) {
            const blob = await imageRes.ok ? await imageRes.blob() : null;
            if (blob) {
              imageBlobUrl = URL.createObjectURL(blob);
            }
          }
        } catch (err) {
          console.error("Failed to load profile picture:", err);
        }
      }

      const userData = {
        name: data.name || '',
        // الرابط الآن محلي (Object URL) ولا يحتاج لتوثيق عند العرض
        profilePicture: imageBlobUrl,
        role: data.role || '',
        loading: false
      };

      userStore.set(userData);

      if (typeof window !== 'undefined') {
        localStorage.setItem('user_session', JSON.stringify(userData));
      }

    } catch (error) {
      console.error("Auth error:", error);
      setGuest();
    } finally {
      initialized = true;
    }
  }

  function setGuest() {
    userStore.set({
      name: '',
      profilePicture: '',
      role: '',
      loading: false
    });

    if (typeof window !== 'undefined') {
      localStorage.removeItem('user_session');
    }
  }

  onMount(() => {
    checkAuth();
  });
</script>

<div class="flex h-screen bg-slate-50 overflow-hidden" dir="rtl">
  <Sidebar />

  <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
    <Navbar />

    <main class="flex-1 overflow-y-auto bg-slate-50/50">
      {#if !initialized}
        <div class="flex h-full items-center justify-center bg-white/50 backdrop-blur-sm">
          <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600"></div>
        </div>
      {:else}
        <slot />
      {/if}
    </main>
  </div>
</div>