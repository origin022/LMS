<script lang="ts">
  import { onMount } from "svelte";
  import { userStore } from "$lib/authStore";
  import { apiFetch } from "$lib/api";
  import Sidebar from "$lib/components/Sidebar.svelte";
  import Navbar from "$lib/components/Navbar.svelte";
  import { sidebarOpen } from "$lib/authStore";

  let initialized = false;

  async function checkAuth() {
    try {
      const res = await apiFetch("/profile");

      if (!res.ok) {
        setGuest();
        return;
      }

      const data = await res.json();
      let imageBlobUrl = "";

      // Only fetch picture if profile says it exists
      if (data.picture) {
        try {
          const imageRes = await apiFetch("/picture/me");
          if (imageRes.ok) {
            const blob = await imageRes.blob();
            if (blob) {
              imageBlobUrl = URL.createObjectURL(blob);
            }
          }
        } catch (err) {
          console.error("Failed to load profile picture:", err);
        }
      }

      const userData = {
        name: data.name || "مستخدم",
        profilePicture: imageBlobUrl,
        hasPicture: !!data.picture, // Track if user has a picture
        role: data.role || "",
        user_id: data.user_id ?? null,
        loading: false,
      };

      userStore.set(userData);

      // Save only serializable data to localStorage (No blob URLs!)
      if (typeof window !== "undefined") {
        const serializableData = { ...userData, profilePicture: "" }; 
        localStorage.setItem("user_session", JSON.stringify(serializableData));
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
      name: "",
      profilePicture: "",
      role: "",
      user_id: null,
      loading: false,
    });

    if (typeof window !== "undefined") {
      localStorage.removeItem("user_session");
    }
  }

  onMount(() => {
    checkAuth();
  });
</script>

<div class="flex h-screen bg-slate-50 overflow-hidden" dir="rtl">
  <Sidebar />

  <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
    {#if $sidebarOpen}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <div 
        class="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-all duration-300"
        on:click={() => sidebarOpen.set(false)}
      ></div>
    {/if}

    <Navbar />

    <main class="flex-1 overflow-y-auto bg-slate-50/50">
      {#if !initialized}
        <div
          class="flex h-full items-center justify-center bg-white/50 backdrop-blur-sm"
        >
          <div
            class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600"
          ></div>
        </div>
      {:else}
        <slot />
      {/if}
    </main>
  </div>
</div>
