<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";

  onMount(() => {
    const courseId = ($page.params as Record<string, string>).course_id;
    goto(`/courses?course_id=${courseId}`, { replaceState: true });
  });
</script>
