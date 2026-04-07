<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { apiFetch } from "$lib/api";
  import { userStore } from "$lib/authStore";
  import { fly, fade } from "svelte/transition";
  import { Trash2, UserX, ToggleLeft, ToggleRight } from "lucide-svelte";

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

  let roles: { roles_id: number; roles_name: string }[] = [];

  // ── حالة التطبيق ───────────────────────────────────────────────
  let profile: ManagerProfile | null = null;
  let loading = true;
  let message = { text: "", type: "" };

  // أسماء الصلاحيات بالضبط كما في الباكند
  const PERM = {
    VIEW_USERS: "view users",
    ADD_TEACHER: "Add Teacher",
    DELETE_USER: "Delete user",
    LIMIT_PERM: "Limiting permission",
    DELETE_COMMENT: "Delete Comment",
  };

  $: user = $userStore;
  $: isManager = user.role
    ? String(user.role).trim().toLowerCase() === "manager"
    : false;

  // الصلاحيات النشطة كـ Set للبحث السريع
  $: activePerms = new Set(
    (profile?.permissions ?? [])
      .filter((p) => p.status !== "blocked")
      .map((p) => p.name),
  );

  $: canViewUsers = activePerms.has(PERM.VIEW_USERS);
  $: canUpdateStatus = activePerms.has(PERM.ADD_TEACHER);
  $: canDeleteUser = activePerms.has(PERM.DELETE_USER);
  $: canLimitPerm = activePerms.has(PERM.LIMIT_PERM);
  $: canDeleteComment = activePerms.has(PERM.DELETE_COMMENT);

  // الحساب الأول للتبويب النشط بعد تحميل الصلاحيات
  $: firstTab = canViewUsers
    ? "users"
    : canLimitPerm
      ? "permissions"
      : canDeleteComment
        ? "recent-comments"
        : "";

  let activeTab = "";

  // Set the default tab once the profile and first allowable tab are ready
  $: if (profile && !activeTab && firstTab) {
    activeTab = firstTab;
  }

  // ── بيانات كل تبويب ───────────────────────────────────────────
  interface UserItem {
    user_id: number;
    name: string;
    email: string;
    roles_id: number;
    roles_name: string;
    state_id: number;
    state_name: string;
    class_name?: string;
  }

  interface UserPermDashboard {
    user_id: number;
    name: string;
    role_name: string;
    permissions: PermInfo[];
  }

  let users: UserItem[] = [];
  let usersLoading = false;

  let statusUserId = "";
  let targetState = "1";

  let deleteUserId = "";

  let permSearchEmail = "";
  let permDashboard: UserPermDashboard | null = null;
  let permDashLoading = false;

  let recentComments: any[] = [];
  let commentsLoading = false;

  let searchQuery = "";
  let filterRoleId = "";
  let filterStateId = "";

  $: filteredUsers = users.filter((u) => {
    const roleName = (u.roles_name || "").toLowerCase();
    const isStudent = roleName.includes("student") || roleName.includes("طالب");
    const isProfessor =
      roleName.includes("professor") ||
      roleName.includes("teacher") ||
      roleName.includes("أستاذ") ||
      roleName.includes("دكتور");

    if (!isStudent && !isProfessor) return false;

    const matchesSearch =
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesRole = filterRoleId
      ? String(u.roles_id) === filterRoleId
      : true;
    const matchesState = filterStateId
      ? String(u.state_id) === filterStateId
      : true;

    return matchesSearch && matchesRole && matchesState;
  });

  // reactive helper to check if Teacher role (3) is selected
  $: isShowingTeachers = filterRoleId === "3";

  // ── دوال مساعدة ───────────────────────────────────────────────
  function showMsg(text: string, type: "success" | "error" = "success") {
    message = { text, type };
    setTimeout(() => {
      message = { text: "", type: "" };
    }, 4000);
  }

  // ── جلب البيانات الأولية ──────────────────────────────────────
  async function loadManagerProfile() {
    const res = await apiFetch(`/manager/my-dashboard`);
    if (res.ok) {
      profile = await res.json();
      console.log("Manager Profile Loaded:", profile);
      if (activeTab === "users") loadUsers();
      if (activeTab === "recent-comments") loadRecentComments();
    }
    loading = false;
  }

  // ── جلب أحدث التعليقات ─────────────────────────────────────────
  async function loadRecentComments() {
    commentsLoading = true;
    try {
      const res = await apiFetch("/manager/recent-comments");
      if (res.ok) {
        recentComments = await res.json();
      }
    } finally {
      commentsLoading = false;
    }
  }

  async function loadUsers(silent = false) {
    if (!silent) usersLoading = true;
    const [uRes, rRes] = await Promise.all([
      apiFetch("/admin/users"),
      apiFetch("/admin/roles/invitable"),
    ]);
    if (uRes.ok) {
      users = (await uRes.json()).sort(
        (a: any, b: any) => b.user_id - a.user_id,
      );
    }
    if (rRes.ok) {
      roles = await rRes.json();
    }

    // Fallback: If roles list is empty or doesn't have Student/Teacher (common for Managers),
    // derive them from the users list we just fetched.
    const uniqueRolesMap = new Map();
    users.forEach((u) => {
      const name = (u.roles_name || "").toLowerCase();
      if (
        name.includes("student") ||
        name.includes("طالب") ||
        name.includes("professor") ||
        name.includes("teacher") ||
        name.includes("أستاذ") ||
        name.includes("دكتور")
      ) {
        uniqueRolesMap.set(u.roles_id, u.roles_name);
      }
    });

    if (uniqueRolesMap.size > 0) {
      const derived = Array.from(uniqueRolesMap.entries()).map(
        ([id, name]) => ({ roles_id: id, roles_name: name }),
      );
      // Merge with existing roles, avoiding duplicates
      const existingIds = new Set(roles.map((r) => r.roles_id));
      derived.forEach((dr) => {
        if (!existingIds.has(dr.roles_id)) roles = [...roles, dr];
      });
    }

    // Default to "Student" or the first role if not set
    if (!filterRoleId && roles.length > 0) {
      const studentRole = roles.find(
        (r) =>
          r.roles_name.toLowerCase().includes("student") ||
          r.roles_name.toLowerCase().includes("طالب"),
      );
      filterRoleId = studentRole
        ? String(studentRole.roles_id)
        : String(roles[0].roles_id);
    }
    if (!silent) usersLoading = false;
  }

  $: if (activeTab === "users" && users.length === 0) loadUsers();
  $: if (activeTab === "recent-comments" && recentComments.length === 0)
    loadRecentComments();

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
      body: JSON.stringify({
        user_id: parseInt(statusUserId),
        target_state: parseInt(targetState),
      }),
    });
    if (res.ok) {
      showMsg("تم تحديث الحالة بنجاح");
      const numericId = parseInt(statusUserId);
      const stateName = targetState === "1" ? "Active" : "Inactive";
      // Immediate UI update
      users = users.map((u) =>
        u.user_id === numericId ? { ...u, state_id: parseInt(targetState), state_name: stateName } : u,
      );
      statusUserId = "";
      loadUsers(true); // Sync in background
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشل التحديث", "error");
    }
  }

  async function deleteUser() {
    if (!deleteUserId) return showMsg("أدخل معرف المستخدم", "error");
    if (!confirm(`هل تريد حذف المستخدم رقم ${deleteUserId}؟`)) return;
    const res = await apiFetch(`/manager/delete-user/${deleteUserId}`, {
      method: "DELETE",
    });
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
    if (!permSearchEmail) return showMsg("أدخل البريد الإلكتروني للمستخدم", "error");
    permDashLoading = true;
    permDashboard = null;
    const searchEmail = permSearchEmail.trim().toLowerCase();
    const res = await apiFetch(
      `/manager/permissions-dashboard/by-email/${searchEmail}`,
    );
    if (res.ok) permDashboard = await res.json();
    else showMsg("لم يتم العثور على مستخدم بهذا البريد الإلكتروني", "error");
    permDashLoading = false;
  }

  async function togglePermission(
    userId: number,
    permId: number,
    currentStatus: string,
  ) {
    const action = currentStatus === "blocked" ? "unblock" : "block";
    const res = await apiFetch("/manager/toggle-permission", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, permission_id: permId, action }),
    });
    if (res.ok) {
      showMsg(action === "block" ? "تم تقييد الصلاحية" : "تم رفع التقييد");
      // Immediate UI update for the specific permission
      if (permDashboard && permDashboard.user_id === userId) {
        permDashboard.permissions = permDashboard.permissions.map((p) =>
          p.permission_id === permId
            ? { ...p, status: action === "block" ? "blocked" : "active" }
            : p,
        );
      }
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشلت العملية", "error");
    }
  }

  async function deleteComment(idToDelete: string) {
    if (!idToDelete) return showMsg("خطأ في معرف التعليق", "error");
    if (!confirm("هل أنت متأكد من حذف هذا التعليق؟")) return;
    const res = await apiFetch(`/manager/delete-comment/${idToDelete}`, {
      method: "DELETE",
    });
    if (res.ok) {
      showMsg("تم حذف التعليق بنجاح");
      // تحديث القائمة المحلية فوراً
      recentComments = recentComments.filter(
        (c) => String(c.comment_id) !== idToDelete,
      );
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشل الحذف", "error");
    }
  }

  // قائمة التبويبات الديناميكية
  $: tabs = [
    canViewUsers && { id: "users", label: "المستخدمون", icon: "👥" },
    canLimitPerm && { id: "permissions", label: "صلاحيات مستخدم", icon: "🛡️" },
    canDeleteComment && {
      id: "recent-comments",
      label: "أحدث التعليقات",
      icon: "💬",
    },
  ].filter(Boolean) as { id: string; label: string; icon: string }[];
</script>

<div class="w-full min-h-screen p-4 md:p-8 space-y-6 bg-slate-50/50" dir="rtl">
  <!-- Toast -->
  {#if message.text}
    <div
      in:fly={{ y: -20 }}
      class="fixed top-10 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-2xl font-black text-sm shadow-2xl
             {message.type === 'error'
        ? 'bg-red-500'
        : 'bg-purple-600'} text-white"
    >
      {message.text}
    </div>
  {/if}

  <div
    class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-4 rounded-[2.5rem] shadow-sm border border-slate-100"
  >
    <div class="flex gap-2 overflow-x-auto no-scrollbar">
      {#each tabs as tab}
        <button
          on:click={() => (activeTab = tab.id)}
          class="px-6 py-3 rounded-2xl text-xs font-black transition-all whitespace-nowrap
               {activeTab === tab.id
            ? 'bg-purple-600 text-white shadow-lg shadow-purple-200'
            : 'text-slate-400 hover:bg-slate-50'}"
        >
          {tab.label}
        </button>
      {/each}
    </div>

    {#if activeTab === "users"}
      <div class="relative w-full md:w-64">
        <input
          bind:value={searchQuery}
          placeholder="بحث عن اسم أو إيميل..."
          class="w-full pr-4 pl-4 py-2.5 bg-slate-50 border-none rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-purple-500/20 text-right"
        />
      </div>
    {/if}
  </div>

  {#if activeTab === "users"}
    <div class="flex flex-wrap gap-3 items-center" in:fade>
      <select
        bind:value={filterRoleId}
        class="bg-white border border-slate-100 px-4 py-2 rounded-xl text-[10px] font-black text-slate-500 outline-none"
      >
        {#each roles.filter((r) => {
          const name = r.roles_name.toLowerCase();
          return name.includes("student") || name.includes("professor") || name.includes("teacher") || name.includes("طالب") || name.includes("أستاذ") || name.includes("دكتور");
        }) as role}
          <option value={String(role.roles_id)}>{role.roles_name}</option>
        {/each}
      </select>

      <select
        bind:value={filterStateId}
        class="bg-white border border-slate-100 px-4 py-2 rounded-xl text-[10px] font-black text-slate-500 outline-none"
      >
        <option value="">كل الحالات</option>
        <option value="1">نشط</option>
        <option value="2">معطّل</option>
      </select>

      <button
        on:click={() => {
          // Reset to default role (Student)
          const studentRole = roles.find(
            (r) =>
              r.roles_name.toLowerCase().includes("student") ||
              r.roles_name.toLowerCase().includes("طالب"),
          );
          filterRoleId = studentRole
            ? String(studentRole.roles_id)
            : roles[0]
              ? String(roles[0].roles_id)
              : "";
          filterStateId = "";
          searchQuery = "";
        }}
        class="text-[10px] font-black text-purple-600 hover:underline"
      >
        تصفير الفلاتر
      </button>
    </div>
  {/if}

  <!-- Loading State -->
  {#if loading}
    <div class="flex justify-center py-24">
      <div
        class="animate-spin rounded-full h-10 w-10 border-[3px] border-purple-600 border-t-transparent"
      ></div>
    </div>
  {:else if tabs.length === 0}
    <!-- No Permissions -->
    <div
      class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm p-16 text-center"
      in:fade
    >
      <div class="text-6xl mb-4">🔒</div>
      <h3 class="text-xl font-black text-slate-700">لا توجد صلاحيات متاحة</h3>
      <p class="text-slate-400 font-bold mt-2 text-sm">
        تواصل مع المدير العام لتفعيل صلاحياتك
      </p>
    </div>
  {:else}
    <div in:fly={{ y: 10 }}>
      <!-- ═══ TAB: المستخدمون ═══ -->
      {#if activeTab === "users"}
        <div class="space-y-4" in:fade>
          <div
            class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden overflow-x-auto"
          >
            {#if usersLoading}
              <div class="flex justify-center py-16">
                <div
                  class="animate-spin rounded-full h-8 w-8 border-[3px] border-purple-600 border-t-transparent"
                ></div>
              </div>
            {:else}
              <table class="w-full text-right">
                <thead
                  class="bg-slate-50 text-slate-400 text-[10px] font-black uppercase tracking-widest"
                >
                  <tr>
                    <th class="px-8 py-5">البيانات الشخصية</th>
                    {#if isShowingTeachers}
                      <th class="px-8 py-5">المجال الدراسي</th>
                    {/if}
                    <th class="px-8 py-5">الرتبة</th>
                    <th class="px-8 py-5">الحالة</th>
                    {#if canLimitPerm || canDeleteUser}
                      <th class="px-8 py-5 text-center">إجراءات</th>
                    {/if}
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  {#each filteredUsers as u}
                    <tr class="hover:bg-slate-50/50 transition-colors">
                      <td class="px-8 py-5">
                        <div class="font-black text-slate-800 text-sm">
                          {u.name}
                        </div>
                        <div class="text-[10px] text-slate-400 font-bold">
                          {u.email}
                        </div>
                      </td>
                      {#if isShowingTeachers}
                        <td class="px-8 py-5">
                          {#if u.class_name}
                            <span class="px-3 py-1 bg-slate-50 text-slate-600 rounded-full text-[10px] font-black border border-slate-100">
                              {u.class_name}
                            </span>
                          {:else}
                            <span class="text-[10px] text-slate-300 font-bold">---</span>
                          {/if}
                        </td>
                      {/if}
                      <td class="px-8 py-5">
                        <span
                          class="px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[10px] font-black"
                        >
                          {u.roles_name || "—"}
                        </span>
                      </td>
                      <td class="px-8 py-5">
                        <button
                          on:click={async () => {
                            statusUserId = String(u.user_id);
                            targetState = u.state_name === "Active" ? "2" : "1";
                            await updateStatus();
                          }}
                          class="flex items-center gap-2 group/status transition-all"
                          title={u.state_name === "Active" ? "تعطيل" : "تفعيل"}
                        >
                          <span
                            class="px-3 py-1 rounded-full text-[10px] font-black transition-all
                            {u.state_name === 'Active'
                              ? 'bg-green-50 text-green-600 group-hover/status:bg-green-100'
                              : 'bg-red-50 text-red-600 group-hover/status:bg-red-100'}"
                          >
                            {u.state_name === "Active" ? "نشط" : "معطل"}
                          </span>
                          <div
                            class="text-slate-300 group-hover/status:text-purple-500 transition-colors"
                          >
                            {#if u.state_name === "Active"}
                              <ToggleRight size={20} />
                            {:else}
                              <ToggleLeft size={20} />
                            {/if}
                          </div>
                        </button>
                      </td>
                      <td class="px-8 py-5">
                        <div class="flex items-center justify-center gap-2">
                          {#if canDeleteUser}
                            <button
                              on:click={() => {
                                deleteUserId = String(u.user_id);
                                deleteUser();
                              }}
                              class="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
                              title="حذف المستخدم"
                            >
                              <Trash2 size={18} strokeWidth={2.5} />
                            </button>
                          {/if}
                        </div>
                      </td>
                    </tr>
                  {/each}
                  {#if filteredUsers.length === 0}
                    <tr>
                      <td
                        colspan={isShowingTeachers ? 5 : 4}
                        class="px-8 py-16 text-center text-slate-400 font-bold"
                        >لا يوجد بيانات</td
                      >
                    </tr>
                  {/if}
                </tbody>
              </table>
            {/if}
          </div>
        </div>
      {:else if activeTab === "permissions"}
        <div class="space-y-6" in:fade>
          <div
            class="max-w-md bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-4"
          >
            <h3 class="text-lg font-black text-slate-800">
              استعراض صلاحيات مستخدم
            </h3>
            <div class="flex gap-3">
              <input
                bind:value={permSearchEmail}
                type="text"
                placeholder="البريد الإلكتروني للمستخدم"
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
              <div
                class="animate-spin rounded-full h-8 w-8 border-[3px] border-purple-600 border-t-transparent"
              ></div>
            </div>
          {:else if permDashboard}
            <div
              class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm p-8"
              in:fly={{ y: 10 }}
            >
              <div
                class="flex items-center gap-4 mb-6 pb-6 border-b border-slate-50"
              >
                <div
                  class="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center font-black text-purple-600 text-sm"
                >
                  {permDashboard.name.charAt(0)}
                </div>
                <div>
                  <div class="font-black text-slate-800">
                    {permDashboard.name}
                  </div>
                  <div class="text-xs text-purple-500 font-bold">
                    {permDashboard.role_name}
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each permDashboard.permissions as perm}
                  {@const isBlocked = perm.status === "blocked"}
                  <div
                    class="flex items-center justify-between p-4 rounded-2xl border transition-all
                              {isBlocked
                      ? 'bg-red-50 border-red-100'
                      : 'bg-slate-50 border-slate-100'}"
                  >
                    <span
                      class="font-black text-sm {isBlocked
                        ? 'text-red-500'
                        : 'text-slate-700'}"
                    >
                      {perm.name}
                    </span>
                    <button
                      on:click={() =>
                        togglePermission(
                          permDashboard!.user_id,
                          perm.permission_id,
                          perm.status,
                        )}
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

        <!-- ═══ TAB: أحدث التعليقات ═══ -->
      {:else if activeTab === "recent-comments"}
        <div class="space-y-4" in:fade>
          <div
            class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden overflow-x-auto"
          >
            {#if commentsLoading}
              <div class="flex justify-center py-16">
                <div
                  class="animate-spin rounded-full h-8 w-8 border-[3px] border-purple-600 border-t-transparent"
                ></div>
              </div>
            {:else}
              <table class="w-full text-right min-w-[800px]">
                <thead
                  class="bg-slate-50 text-slate-400 text-[10px] font-black uppercase tracking-widest"
                >
                  <tr>
                    <th class="px-8 py-5">المستخدِم</th>
                    <th class="px-8 py-5">التعليق</th>
                    <th class="px-8 py-5">المحاضرة</th>
                    <th class="px-8 py-5">التوقيت</th>
                    <th class="px-8 py-5">حذف</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  {#each recentComments as c}
                    <tr class="hover:bg-slate-50/50 transition-colors">
                      <td class="px-8 py-5 text-sm font-black text-slate-800">
                        {c.user_name}
                      </td>
                      <td class="px-8 py-5 text-xs text-slate-600 max-w-sm">
                        <div class="line-clamp-2" title={c.text}>{c.text}</div>
                      </td>
                      <td
                        class="px-8 py-5 text-[10px] font-bold text-purple-600"
                      >
                        {c.lecture_title}
                      </td>
                      <td
                        class="px-8 py-5 text-[10px] text-slate-400 font-bold"
                      >
                        {new Date(c.submission_time).toLocaleString("ar-EG")}
                      </td>
                      <td class="px-8 py-5">
                        <button
                          on:click={() => deleteComment(String(c.comment_id))}
                          class="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
              {#if recentComments.length === 0}
                <div class="py-20 text-center text-slate-400 font-bold">
                  لا توجد تعليقات حالياً
                </div>
              {/if}
            {/if}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>
