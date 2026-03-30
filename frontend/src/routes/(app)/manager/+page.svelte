<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { apiFetch } from "$lib/api";
  import { userStore } from "$lib/authStore";
  import { fly, fade } from "svelte/transition";
  import { Trash2, ShieldCheck, UserX, ToggleLeft, ToggleRight, MessageSquareX } from "lucide-svelte";

  // ── الصلاحيات المتاحة لهذا المدير ──────────────────────────────
  interface PermInfo {
    permission_id: number;
    name: string;
    status: string; // "active" | "blocked"
  }

  interface ManagerProfile {
    name: string;
    role_name: string;
    permissions: PermInfo[];
  }

  // ── حالة التطبيق ───────────────────────────────────────────────
  let profile: ManagerProfile | null = null;
  let loading = true;
  let message = { text: "", type: "" };

  // أسماء الصلاحيات بالضبط كما في الباكند
  const PERM = {
    VIEW_USERS:    "view users",
    ADD_TEACHER:   "Add Teacher",
    DELETE_USER:   "Delete user",
    LIMIT_PERM:    "Limiting permission",
    DELETE_COMMENT:"Delete Comment",
  };

  $: user = $userStore;
  $: isManager = user.role ? String(user.role).trim().toLowerCase() === "manager" : false;

  // الصلاحيات النشطة كـ Set للبحث السريع
  $: activePerms = new Set(
    (profile?.permissions ?? [])
      .filter(p => p.status !== "blocked")
      .map(p => p.name)
  );

  $: canViewUsers    = activePerms.has(PERM.VIEW_USERS);
  $: canUpdateStatus = activePerms.has(PERM.ADD_TEACHER);
  $: canDeleteUser   = activePerms.has(PERM.DELETE_USER);
  $: canLimitPerm    = activePerms.has(PERM.LIMIT_PERM);
  $: canDeleteComment= activePerms.has(PERM.DELETE_COMMENT);

  // الحساب الأول للتبويب النشط بعد تحميل الصلاحيات
  $: firstTab = canViewUsers    ? "users"
              : canUpdateStatus  ? "status"
              : canDeleteUser    ? "delete-user"
              : canLimitPerm     ? "permissions"
              : canDeleteComment ? "delete-comment"
              : "";

  let activeTab = "";

  // ── بيانات كل تبويب ───────────────────────────────────────────
  interface UserItem {
    user_id: number;
    name: string;
    email: string;
    roles_name: string;
    state_name: string;
  }

  interface UserPermDashboard {
    name: string;
    role_name: string;
    permissions: PermInfo[];
  }

  let users: UserItem[] = [];
  let usersLoading = false;

  let statusUserId = "";
  let targetState = "1";

  let deleteUserId = "";

  let permUserId = "";
  let permDashboard: UserPermDashboard | null = null;
  let permDashLoading = false;

  let deleteCommentId = "";

  let searchQuery = "";
  $: filteredUsers = users.filter(u =>
    u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // ── دوال مساعدة ───────────────────────────────────────────────
  function showMsg(text: string, type: "success" | "error" = "success") {
    message = { text, type };
    setTimeout(() => { message = { text: "", type: "" }; }, 4000);
  }

  // ── جلب البيانات الأولية ──────────────────────────────────────
  async function loadManagerProfile() {
    if (!user.user_id) return;
    const res = await apiFetch(`/manager/permissions-dashboard/${user.user_id}`);
    if (res.ok) {
      profile = await res.json();
      // تعيين أول تبويب متاح
      if (!activeTab) {
        activeTab = firstTab;
      }
    }
    loading = false;
  }

  async function loadUsers() {
    usersLoading = true;
    const res = await apiFetch("/admin/users");
    if (res.ok) users = await res.json();
    usersLoading = false;
  }

  $: if (activeTab === "users" && users.length === 0) {
    loadUsers();
  }

  onMount(async () => {
    if (!isManager && !user.loading) {
      goto("/home");
      return;
    }
    await loadManagerProfile();
  });

  // ── actions ───────────────────────────────────────────────────
  async function updateStatus() {
    if (!statusUserId) return showMsg("أدخل معرف المستخدم", "error");
    const res = await apiFetch("/manager/update-status", {
      method: "POST",
      body: JSON.stringify({ user_id: parseInt(statusUserId), target_state: parseInt(targetState) }),
    });
    if (res.ok) {
      showMsg("تم تحديث الحالة بنجاح");
      statusUserId = "";
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشل التحديث", "error");
    }
  }

  async function deleteUser() {
    if (!deleteUserId) return showMsg("أدخل معرف المستخدم", "error");
    if (!confirm(`هل تريد حذف المستخدم رقم ${deleteUserId}؟`)) return;
    const res = await apiFetch(`/manager/delete-user/${deleteUserId}`, { method: "DELETE" });
    if (res.ok) {
      showMsg("تم الحذف بنجاح");
      deleteUserId = "";
      if (activeTab === "users") loadUsers();
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشل الحذف", "error");
    }
  }

  async function loadUserPermissions() {
    if (!permUserId) return showMsg("أدخل معرف المستخدم", "error");
    permDashLoading = true;
    permDashboard = null;
    const res = await apiFetch(`/manager/permissions-dashboard/${permUserId}`);
    if (res.ok) permDashboard = await res.json();
    else showMsg("لم يتم العثور على المستخدم", "error");
    permDashLoading = false;
  }

  async function togglePermission(userId: number, permId: number, currentStatus: string) {
    const action = currentStatus === "blocked" ? "unblock" : "block";
    const res = await apiFetch("/manager/toggle-permission", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, permission_id: permId, action }),
    });
    if (res.ok) {
      showMsg(action === "block" ? "تم تقييد الصلاحية" : "تم رفع التقييد");
      await loadUserPermissions();
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشلت العملية", "error");
    }
  }

  async function deleteComment() {
    if (!deleteCommentId) return showMsg("أدخل معرف التعليق", "error");
    if (!confirm(`حذف التعليق رقم ${deleteCommentId}؟`)) return;
    const res = await apiFetch(`/manager/delete-comment/${deleteCommentId}`, { method: "DELETE" });
    if (res.ok) {
      showMsg("تم حذف التعليق");
      deleteCommentId = "";
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشل الحذف", "error");
    }
  }

  // قائمة التبويبات الديناميكية
  $: tabs = [
    canViewUsers    && { id: "users",          label: "المستخدمون",     icon: "👥" },
    canUpdateStatus  && { id: "status",         label: "تغيير الحالة",   icon: "🔄" },
    canDeleteUser   && { id: "delete-user",     label: "حذف مستخدم",    icon: "🗑️" },
    canLimitPerm    && { id: "permissions",     label: "صلاحيات مستخدم", icon: "🛡️" },
    canDeleteComment && { id: "delete-comment", label: "حذف تعليق",     icon: "💬" },
  ].filter(Boolean) as { id: string; label: string; icon: string }[];
</script>

<div class="w-full min-h-screen p-4 md:p-8 space-y-6 bg-slate-50/50" dir="rtl">

  <!-- Toast -->
  {#if message.text}
    <div
      in:fly={{ y: -20 }}
      class="fixed top-10 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-2xl font-black text-sm shadow-2xl
             {message.type === 'error' ? 'bg-red-500' : 'bg-purple-600'} text-white"
    >
      {message.text}
    </div>
  {/if}

  <!-- Header -->
  <div class="bg-white p-6 rounded-[2.5rem] shadow-sm border border-slate-100">
    <div class="flex items-center gap-4 mb-2">
      <div class="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center">
        <ShieldCheck size={24} class="text-purple-600" />
      </div>
      <div>
        <h1 class="text-xl font-black text-slate-800">لوحة المدير</h1>
        {#if profile}
          <p class="text-xs text-slate-400 font-bold mt-0.5">
            {profile.name} — <span class="text-purple-500">{profile.role_name}</span>
          </p>
        {/if}
      </div>
    </div>

    {#if !loading && tabs.length > 0}
      <div class="flex gap-2 overflow-x-auto no-scrollbar mt-4" in:fade>
        {#each tabs as tab}
          <button
            on:click={() => (activeTab = tab.id)}
            class="px-5 py-3 rounded-2xl text-xs font-black transition-all whitespace-nowrap
                   {activeTab === tab.id
                     ? 'bg-purple-600 text-white shadow-lg shadow-purple-200'
                     : 'text-slate-400 hover:bg-slate-50'}"
          >
            {tab.icon} {tab.label}
          </button>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Loading State -->
  {#if loading}
    <div class="flex justify-center py-24">
      <div class="animate-spin rounded-full h-10 w-10 border-[3px] border-purple-600 border-t-transparent"></div>
    </div>

  {:else if tabs.length === 0}
    <!-- No Permissions -->
    <div class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm p-16 text-center" in:fade>
      <div class="text-6xl mb-4">🔒</div>
      <h3 class="text-xl font-black text-slate-700">لا توجد صلاحيات متاحة</h3>
      <p class="text-slate-400 font-bold mt-2 text-sm">تواصل مع المدير العام لتفعيل صلاحياتك</p>
    </div>

  {:else}
    <div in:fly={{ y: 10 }}>

      <!-- ═══ TAB: المستخدمون ═══ -->
      {#if activeTab === "users"}
        <div class="space-y-4" in:fade>
          <div class="flex items-center gap-3">
            <input
              bind:value={searchQuery}
              placeholder="بحث عن اسم أو إيميل..."
              class="flex-1 max-w-sm px-5 py-3 bg-white border border-slate-100 rounded-2xl text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500/20"
            />
          </div>

          <div class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden overflow-x-auto">
            {#if usersLoading}
              <div class="flex justify-center py-16">
                <div class="animate-spin rounded-full h-8 w-8 border-[3px] border-purple-600 border-t-transparent"></div>
              </div>
            {:else}
              <table class="w-full text-right">
                <thead class="bg-slate-50 text-slate-400 text-[10px] font-black uppercase tracking-widest">
                  <tr>
                    <th class="px-8 py-5">البيانات الشخصية</th>
                    <th class="px-8 py-5">الرتبة</th>
                    <th class="px-8 py-5">الحالة</th>
                    {#if canDeleteUser}
                      <th class="px-8 py-5">إجراء</th>
                    {/if}
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  {#each filteredUsers as u}
                    <tr class="hover:bg-slate-50/50 transition-colors">
                      <td class="px-8 py-5">
                        <div class="font-black text-slate-800 text-sm">{u.name}</div>
                        <div class="text-[10px] text-slate-400 font-bold">{u.email}</div>
                      </td>
                      <td class="px-8 py-5">
                        <span class="px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[10px] font-black">
                          {u.roles_name || "—"}
                        </span>
                      </td>
                      <td class="px-8 py-5">
                        <span class="px-3 py-1 rounded-full text-[10px] font-black
                          {u.state_name === 'Active' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}">
                          {u.state_name === 'Active' ? 'نشط' : 'معطل'}
                        </span>
                      </td>
                      {#if canDeleteUser}
                        <td class="px-8 py-5">
                          <button
                            on:click={() => { deleteUserId = String(u.user_id); deleteUser(); }}
                            class="text-slate-300 hover:text-red-500 p-2 hover:bg-red-50 rounded-xl transition-all"
                          >
                            <Trash2 size={18} strokeWidth={2.5} />
                          </button>
                        </td>
                      {/if}
                    </tr>
                  {/each}
                  {#if filteredUsers.length === 0}
                    <tr>
                      <td colspan="4" class="px-8 py-16 text-center text-slate-400 font-bold">لا يوجد بيانات</td>
                    </tr>
                  {/if}
                </tbody>
              </table>
            {/if}
          </div>
        </div>

      <!-- ═══ TAB: تغيير الحالة ═══ -->
      {:else if activeTab === "status"}
        <div class="max-w-md mx-auto" in:fade>
          <div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm space-y-5">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                <UserX size={20} class="text-purple-600" />
              </div>
              <h3 class="text-lg font-black text-slate-800">تغيير حالة مستخدم</h3>
            </div>

            <input
              bind:value={statusUserId}
              type="number"
              placeholder="معرف المستخدم (user_id)"
              class="w-full p-5 bg-slate-50 border-none rounded-3xl outline-none font-bold focus:ring-2 focus:ring-purple-500/20"
            />

            <div class="flex gap-3">
              <button
                on:click={() => (targetState = "1")}
                class="flex-1 py-4 rounded-2xl text-sm font-black transition-all
                       {targetState === '1' ? 'bg-green-500 text-white shadow-lg shadow-green-100' : 'bg-slate-50 text-slate-400'}"
              >
                ✅ تفعيل
              </button>
              <button
                on:click={() => (targetState = "2")}
                class="flex-1 py-4 rounded-2xl text-sm font-black transition-all
                       {targetState === '2' ? 'bg-red-500 text-white shadow-lg shadow-red-100' : 'bg-slate-50 text-slate-400'}"
              >
                🚫 تعطيل
              </button>
            </div>

            <button
              on:click={updateStatus}
              class="w-full py-5 bg-purple-600 text-white rounded-3xl font-black shadow-xl hover:bg-purple-700 transition-all"
            >
              تأكيد التغيير
            </button>
          </div>
        </div>

      <!-- ═══ TAB: حذف مستخدم ═══ -->
      {:else if activeTab === "delete-user"}
        <div class="max-w-md mx-auto" in:fade>
          <div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm space-y-5">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
                <Trash2 size={20} class="text-red-500" />
              </div>
              <h3 class="text-lg font-black text-slate-800">حذف مستخدم</h3>
            </div>

            <div class="p-4 bg-red-50 rounded-2xl border border-red-100">
              <p class="text-xs text-red-600 font-bold">⚠️ هذه العملية لا يمكن التراجع عنها</p>
            </div>

            <input
              bind:value={deleteUserId}
              type="number"
              placeholder="معرف المستخدم (user_id)"
              class="w-full p-5 bg-slate-50 border-none rounded-3xl outline-none font-bold focus:ring-2 focus:ring-red-500/20"
            />

            <button
              on:click={deleteUser}
              class="w-full py-5 bg-red-500 text-white rounded-3xl font-black shadow-xl hover:bg-red-600 transition-all"
            >
              حذف المستخدم
            </button>
          </div>
        </div>

      <!-- ═══ TAB: صلاحيات مستخدم ═══ -->
      {:else if activeTab === "permissions"}
        <div class="space-y-6" in:fade>
          <div class="max-w-md bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-4">
            <h3 class="text-lg font-black text-slate-800">استعراض صلاحيات مستخدم</h3>
            <div class="flex gap-3">
              <input
                bind:value={permUserId}
                type="number"
                placeholder="معرف المستخدم (user_id)"
                class="flex-1 p-4 bg-slate-50 border-none rounded-2xl outline-none font-bold focus:ring-2 focus:ring-purple-500/20"
              />
              <button
                on:click={loadUserPermissions}
                class="px-6 py-4 bg-purple-600 text-white rounded-2xl font-black text-sm hover:bg-purple-700 transition-all"
              >
                بحث
              </button>
            </div>
          </div>

          {#if permDashLoading}
            <div class="flex justify-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-[3px] border-purple-600 border-t-transparent"></div>
            </div>
          {:else if permDashboard}
            <div class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm p-8" in:fly={{ y: 10 }}>
              <div class="flex items-center gap-4 mb-6 pb-6 border-b border-slate-50">
                <div class="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center font-black text-purple-600 text-sm">
                  {permDashboard.name.charAt(0)}
                </div>
                <div>
                  <div class="font-black text-slate-800">{permDashboard.name}</div>
                  <div class="text-xs text-purple-500 font-bold">{permDashboard.role_name}</div>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each permDashboard.permissions as perm}
                  {@const isBlocked = perm.status === "blocked"}
                  <div class="flex items-center justify-between p-4 rounded-2xl border transition-all
                              {isBlocked ? 'bg-red-50 border-red-100' : 'bg-slate-50 border-slate-100'}">
                    <span class="font-black text-sm {isBlocked ? 'text-red-500' : 'text-slate-700'}">
                      {perm.name}
                    </span>
                    <button
                      on:click={() => togglePermission(parseInt(permUserId), perm.permission_id, perm.status)}
                      class="transition-all hover:scale-110 active:scale-95"
                      title={isBlocked ? "رفع التقييد" : "تقييد الصلاحية"}
                    >
                      {#if isBlocked}
                        <ToggleLeft size={28} class="text-red-400" />
                      {:else}
                        <ToggleRight size={28} class="text-green-500" />
                      {/if}
                    </button>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>

      <!-- ═══ TAB: حذف تعليق ═══ -->
      {:else if activeTab === "delete-comment"}
        <div class="max-w-md mx-auto" in:fade>
          <div class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm space-y-5">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
                <MessageSquareX size={20} class="text-orange-500" />
              </div>
              <h3 class="text-lg font-black text-slate-800">حذف تعليق</h3>
            </div>

            <input
              bind:value={deleteCommentId}
              type="number"
              placeholder="معرف التعليق (comment_id)"
              class="w-full p-5 bg-slate-50 border-none rounded-3xl outline-none font-bold focus:ring-2 focus:ring-orange-500/20"
            />

            <button
              on:click={deleteComment}
              class="w-full py-5 bg-orange-500 text-white rounded-3xl font-black shadow-xl hover:bg-orange-600 transition-all"
            >
              حذف التعليق
            </button>
          </div>
        </div>
      {/if}

    </div>
  {/if}
</div>

<style>
  .no-scrollbar::-webkit-scrollbar { display: none; }
  .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
