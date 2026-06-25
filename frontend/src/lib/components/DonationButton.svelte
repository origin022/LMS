<script lang="ts">
  import DonationModal from "./DonationModal.svelte";
  import { fade } from "svelte/transition";
  
  let showModal = false;
</script>

<div class="flex items-center">
  <button
    on:click={() => showModal = true}
    class="group relative flex items-center gap-3 px-3 py-2 text-gray-700 hover:text-gray-900 transition-all duration-300 active:scale-95"
  >
    <div class="flex flex-col items-start leading-none relative z-10">
      <span class="text-sm font-black tracking-tight">ادعمنا</span>
      <span class="text-[10px] font-bold uppercase opacity-50 tracking-widest -mt-0.5">Support Us</span>
    </div>
    
    <div class="w-11 h-18 flex items-center justify-center relative z-10 group-hover:scale-110 transition-transform overflow-hidden">
      <img 
        src="/zainz.png" 
        alt="Z" 
        class="w-full h-full object-contain" 
        on:error={(e) => ((e.target as HTMLImageElement).src = "/zain.png")}
      />
    </div>
  </button>
</div>

<DonationModal show={showModal} on:close={() => showModal = false} />
