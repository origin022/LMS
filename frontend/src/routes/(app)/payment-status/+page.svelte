<script lang="ts">
  import { page } from "$app/stores";
  import { fly } from "svelte/transition";
  import { goto } from "$app/navigation";

  $: status = $page.url.searchParams.get("status");
  $: donationId = $page.url.searchParams.get("donation_id");

  const isSuccess = status === "SUCCESS";
</script>

<div class="min-h-[80vh] flex items-center justify-center p-6" dir="rtl">
  <div 
    in:fly={{ y: 20, duration: 600 }}
    class="bg-white p-12 rounded-[3rem] shadow-2xl border border-gray-100 max-w-lg w-full text-center space-y-8"
  >
    {#if isSuccess}
      <div class="w-24 h-24 bg-emerald-50 rounded-full flex items-center justify-center mx-auto text-emerald-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      
      <div class="space-y-3">
        <h2 class="text-3xl font-black text-gray-800">تم الدفع بنجاح! 🎉</h2>
        <p class="text-gray-500 font-medium leading-relaxed">نشكرك بعمق على دعمك للمنصة. مساهمتك تساعدنا على الاستمرار في تقديم محتوى تعليمي متميز.</p>
      </div>
    {:else}
      <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto text-red-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      
      <div class="space-y-3">
        <h2 class="text-3xl font-black text-gray-800">فشلت عملية الدفع 😕</h2>
        <p class="text-gray-500 font-medium leading-relaxed">نأسف، يبدو أن هناك مشكلة حدثت أثناء عملية الدفع. يرجى المحاولة مرة أخرى لاحقاً.</p>
      </div>
    {/if}

    <div class="pt-6 flex flex-col gap-4">
      <button 
        on:click={() => goto("/home")}
        class="w-full py-4 bg-gray-900 text-white rounded-3xl font-black hover:bg-black transition-all shadow-xl shadow-gray-200"
      >
        العودة للرئيسية
      </button>
      
      <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">
        رقم العملية: {donationId || 'غير متوفر'}
      </p>
    </div>
  </div>
</div>
