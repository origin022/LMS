<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { apiFetch } from "$lib/api";
  import { fly, fade, scale } from "svelte/transition";
  import { cubicOut } from "svelte/easing";

  const dispatch = createEventDispatcher();
  
  export let show = false;
  
  let amount: number = 5000;
  let loading = false;
  let error = "";

  const presets = [
    { label: "كوب قهوة", value: 2000, icon: "☕" },
    { label: "كتاب مفيد", value: 10000, icon: "📚" },
    { label: "دعم سخي", value: 25000, icon: "💎" },
  ];

  async function handleDonate() {
    if (amount < 250) {
      error = "أقل مبلغ للتبرع هو 250 دينار";
      return;
    }
    
    loading = true;
    error = "";
    
    try {
      const res = await apiFetch("/donations/start", {
        method: "POST",
        body: JSON.stringify({ amount })
      });
      
      if (res.ok) {
        const data = await res.json();
        window.location.href = data.payment_url;
      } else {
        const err = await res.json().catch(() => ({}));
        error = err.detail || "فشل بدء عملية الدفع";
      }
    } catch (err) {
      error = "حدث خطأ في الاتصال بالخادم";
    } finally {
      loading = false;
    }
  }

  function close() {
    if (!loading) dispatch("close");
  }
</script>

{#if show}
  <div
    class="fixed inset-0 z-100 grid place-items-center p-4 md:p-6 bg-slate-950/40 backdrop-blur-[2px]"
    on:click={close}
    on:keydown={(e) => e.key === "Escape" && close()}
    role="button"
    tabindex="-1"
    transition:fade
  >
    <div
      class="bg-white w-full max-w-lg rounded-[2.5rem] shadow-[0_40px_80px_-20px_rgba(0,0,0,0.3)] overflow-hidden border border-white/20 relative"
      on:click|stopPropagation
      role="none"
      in:scale={{ duration: 400, start: 0.98, easing: cubicOut }}
    >
      <!-- Close Button -->
      <button 
        on:click={close}
        class="absolute top-6 left-6 z-20 w-10 h-10 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center text-white transition-all backdrop-blur-md"
        aria-label="إغلاق"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Premium Header -->
      <div class="h-48 bg-gradient-to-br from-emerald-600 via-emerald-500 to-teal-600 p-10 flex flex-col justify-end relative overflow-hidden">
        <!-- Abstract Shapes -->
        <div class="absolute top-0 right-0 w-72 h-72 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
        <div class="absolute bottom-0 left-0 w-48 h-48 bg-black/5 rounded-full blur-2xl translate-y-1/2 -translate-x-1/2"></div>
        
        <div class="relative z-10 text-white space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur-md rounded-full border border-white/20">
            <span class="w-1.5 h-1.5 bg-green-300 rounded-full animate-pulse"></span>
            <span class="text-[10px] font-black uppercase tracking-widest text-emerald-50">الدفع الآمن</span>
          </div>
          <h3 class="text-4xl font-black tracking-tight leading-tight">ادعم المنصة</h3>
          <p class="text-emerald-50 text-sm font-medium opacity-80">مساهمتك تساعدنا على التطوير والاستمرار</p>
        </div>
      </div>

      <!-- Main Content -->
      <div class="p-8 md:p-10 space-y-8">
        <!-- Preset Choice -->
        <div class="grid grid-cols-3 gap-3">
          {#each presets as preset}
            <button 
              on:click={() => amount = preset.value}
              class="flex flex-col items-center gap-2 p-5 rounded-3xl border-2 transition-all duration-400 {amount === preset.value ? 'bg-emerald-50 border-emerald-500 shadow-xl shadow-emerald-500/10 scale-105' : 'bg-slate-50 border-slate-50 hover:border-slate-200 hover:bg-slate-100'}"
            >
              <span class="text-3xl filter drop-shadow-sm">{preset.icon}</span>
              <span class="text-[11px] font-black text-gray-800 uppercase">{preset.label}</span>
            </button>
          {/each}
        </div>

        <!-- Custom Amount -->
        <div class="space-y-4">
          <div class="flex items-center justify-between px-2">
            <label class="text-[11px] font-black text-gray-400 uppercase tracking-widest" for="amount">حدد المبلغ يدوياً (IQD)</label>
            <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">ZainCash</span>
          </div>
          <div class="relative group">
            <input
              id="amount"
              type="number"
              bind:value={amount}
              min="250"
              class="w-full p-8 md:p-10 bg-slate-50 border-2 border-slate-50 focus:border-emerald-500/20 focus:bg-white rounded-[2.5rem] outline-none text-center text-5xl font-black text-gray-900 transition-all placeholder:text-slate-200"
              placeholder="000"
            />
            <div class="absolute inset-0 rounded-[2.5rem] border-2 border-emerald-500/5 pointer-events-none group-focus-within:border-emerald-500/30 transition-all pointer-events-none"></div>
          </div>
        </div>

        {#if error}
          <div in:scale class="bg-red-50 text-red-600 p-5 rounded-2xl text-xs font-bold text-center border border-red-100 flex items-center justify-center gap-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        {/if}

        <!-- Actions -->
        <div class="flex gap-4 pt-2">
          <button
            on:click={handleDonate}
            disabled={loading || !amount}
            class="flex-[2] relative h-24 bg-gray-900 text-white rounded-[2.2rem] font-black hover:bg-black disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)] active:scale-[0.98] group overflow-hidden"
          >
            {#if loading}
              <div class="flex items-center justify-center gap-4">
                <div class="w-6 h-6 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
                <span class="text-sm tracking-wide">جاري المعالجة...</span>
              </div>
            {:else}
              <div class="flex items-center justify-center gap-3">
                <span class="text-lg">تأكيد والدفع</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 group-hover:translate-x-[-6px] transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7" />
                </svg>
              </div>
              <div class="absolute inset-0 bg-white/10 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out skew-x-12"></div>
            {/if}
          </button>

          <button
            on:click={close}
            disabled={loading}
            class="flex-1 h-24 bg-slate-100 text-slate-400 rounded-[2.2rem] font-black hover:bg-slate-200 hover:text-slate-600 transition-all active:scale-95 flex items-center justify-center"
          >
            إلغاء
          </button>
        </div>
        
        <div class="flex items-center justify-center gap-4 py-2">
            <div class="h-px bg-slate-100 flex-1"></div>
            <div class="flex items-center gap-1.5 grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all cursor-default">
              <img src="/zainz.png" alt="Zain" class="h-3 w-auto" on:error={(e) => ((e.target as HTMLImageElement).src = "/zzain.png")} />
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest text-center">المعالج الآمن</span>
            </div>
            <div class="h-px bg-slate-100 flex-1"></div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type=number] {
    -moz-appearance: textfield;
    appearance: none;
  }
</style>
