<script lang="ts">
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/api";
  import { fly, fade } from "svelte/transition";
  import { Trash2, ToggleLeft, ToggleRight } from "lucide-svelte";

  let pendingRoles: Record<number, string> = {};

  interface UserAdmin {
    user_id: number;
    name: string;
    email: string;
    roles_id: number;
    state_id: number;
    roles_name?: string;
    state_name?: string;
    class_name?: string;
  }

  interface Role {
    roles_id: number;
    roles_name: string;
  }

  interface Permission {
    permission_id: number;
    name: string;
  }

  interface Classroom {
    class_id: number;
    class_name: string;
  }

  let activeTab: "classrooms" | "users" | "invites" | "roles" = "classrooms";
  let userSubTab: "normal" | "managers" = "normal";
  let loading = false;

  let classrooms: Classroom[] = [];
  let users: UserAdmin[] = [];
  let roles: Role[] = [];
  let permissions: Permission[] = [];

  let searchQuery = "";
  let filterRoleId = "";
  let filterStateId = "";

  let newClassName = "";
  let inviteEmail = "";
  let selectedRoleId = "";
  let newRoleName = "";
  let selectedPermissions: number[] = [];
  let message = { text: "", type: "" };

  function showMsg(text: string, type: "success" | "error" = "success") {
    message = { text, type };
    setTimeout(() => {
      message = { text: "", type: "" };
    }, 4000);
  }

  async function loadData(silent = false) {
    if (!silent) loading = true;
    try {
      if (activeTab === "classrooms") {
        const res = await apiFetch("/classrooms");
        if (res.ok) {
          classrooms = (await res.json()).sort(
            (a: any, b: any) => b.class_id - a.class_id,
          );
        }
      } else if (activeTab === "users") {
        const params = new URLSearchParams();
        if (filterRoleId) params.append("roles_id", filterRoleId.toString());
        if (filterStateId) params.append("state_id", filterStateId.toString());

        const [uRes, rRes] = await Promise.all([
          apiFetch(`/admin/users?${params.toString()}`),
          apiFetch("/admin/roles/invitable"),
        ]);
        if (uRes.ok) users = await uRes.json();
        if (rRes.ok) roles = await rRes.json();
      } else if (activeTab === "invites") {
        const res = await apiFetch("/admin/roles/invitable");
        if (res.ok) roles = await res.json();
      } else if (activeTab === "roles") {
        const res = await apiFetch("/admin/permissions");
        if (res.ok) permissions = await res.json();
      }
    } catch (e) {
      console.error(e);
    } finally {
      if (!silent) loading = false;
    }
  }

  $: filteredDisplay = users.filter((u) => {
    // Hide Admin entirely from the list (role_id 1)
    if (u.roles_id === 1) return false;

    const isManager = u.roles_id !== 1 && u.roles_id !== 4 && u.roles_id !== 3;
    const matchesSubTab = userSubTab === "managers" ? isManager : !isManager;
    const matchesSearch =
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSubTab && matchesSearch;
  });

  $: if (activeTab || filterRoleId || filterStateId) {
    // When tab changes, we might want to reset filters or keep them.
    // For now, keep them but ensure loadData uses them.
    loadData();
  }

  // Reactive helper for teacher column visibility
  $: isShowingTeachers = userSubTab === "normal" && filterRoleId === "3";

  // Default role logic for Normal users
  $: if (
    activeTab === "users" &&
    userSubTab === "normal" &&
    filterRoleId !== "3" &&
    filterRoleId !== "4"
  ) {
    filterRoleId = "4";
  }

  onMount(loadData);

  async function changeUserRole(userId: number, roleId: string) {
    if (!roleId) return;
    const res = await apiFetch(
      `/admin/users/${userId}/permissions?new_role_id=${roleId}`,
      { method: "PATCH" },
    );
    if (res.ok) {
      showMsg("تم تحديث الرتبة");
      loadData();
    }
  }
  let selectedFile: File | null = null;
  let fileInput: HTMLInputElement;

  async function createClass() {
    if (!newClassName) return showMsg("يرجى إدخال اسم المادة", "error");

    loading = true; // تفعيل حالة التحميل
    try {
      const formData = new FormData();
      formData.append("name", newClassName);
      if (selectedFile) {
        formData.append("image", selectedFile);
      }

      const res = await apiFetch("/admin/classrooms", {
        method: "POST",
        body: formData, // نرسل الـ FormData مباشرة
        // ملاحظة: لا تضع headers يدوية هنا، المتصفح سيضع Content-Type تلقائياً
      });

      if (res.ok) {
        newClassName = "";
        selectedFile = null;
        if (fileInput) fileInput.value = ""; // تصفير حقل الملف
        showMsg("تم إنشاء الكلاس بنجاح");
        loadData();
      } else {
        const err = await res.json();
        showMsg(err.detail || "فشل إنشاء الكلاس", "error");
      }
    } catch (e) {
      showMsg("حدث خطأ في الاتصال", "error");
    } finally {
      loading = false;
    }
  }

  function handleFileChange(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      selectedFile = target.files[0];
    }
  }

  async function deleteClass(id: number) {
    if (!confirm("حذف الكلاس؟")) return;
    const res = await apiFetch(`/admin/classrooms/${id}`, {
      method: "DELETE",
    });
    if (res.status === 204) {
      showMsg("تم الحذف");
      loadData();
    }
  }

  async function sendInvite() {
    if (!inviteEmail || !selectedRoleId)
      return showMsg("أكمل البيانات", "error");
    const res = await apiFetch("/admin/managers/invite", {
      method: "POST",
      body: JSON.stringify({
        email: inviteEmail,
        role_id: parseInt(selectedRoleId),
      }),
    });
    if (res.ok) {
      showMsg("تم إرسال الدعوة");
      inviteEmail = "";
      selectedRoleId = "";
    }
  }

  async function createRole() {
    if (!newRoleName || selectedPermissions.length === 0)
      return showMsg("بيانات ناقصة", "error");
    const res = await apiFetch("/admin/roles", {
      method: "POST",
      body: JSON.stringify({
        roles_name: newRoleName,
        permission_id: selectedPermissions,
      }),
    });
    if (res.ok) {
      showMsg("تم إنشاء الرتبة");
      newRoleName = "";
      selectedPermissions = [];
    }
  }

  async function toggleUserStatus(userId: number, currentState: string) {
    const nextStateId = currentState === "Active" ? 2 : 1;
    const nextStateName = nextStateId === 1 ? "Active" : "Inactive";

    const res = await apiFetch(`/admin/managers/${userId}/deactivate`, {
      method: "PATCH",
    });

    if (res.ok) {
      showMsg("تم تحديث حالة المستخدم");

      users = users.map((u) =>
        u.user_id === userId
          ? { ...u, state_id: nextStateId, state_name: nextStateName }
          : u,
      );

      // 3. اختياري: تأخير جلب البيانات لضمان تحديث قاعدة البيانات تماماً
      // أو حذف loadData(true) إذا كنت واثقاً من التحديث المحلي
      setTimeout(() => loadData(true), 500);
    } else {
      const err = await res.json().catch(() => ({}));
      showMsg(err.detail || "فشل تحديث الحالة", "error");
    }
  }
</script>

<div class="w-full min-h-screen p-4 md:p-8 space-y-6 bg-slate-50/50" dir="rtl">
  {#if message.text}
    <div
      in:fly={{ y: -20 }}
      class="fixed top-10 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-2xl font-black text-sm shadow-2xl {message.type ===
      'error'
        ? 'bg-red-500'
        : 'bg-blue-600'} text-white"
    >
      {message.text}
    </div>
  {/if}

  <div
    class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-4 rounded-[2.5rem] shadow-sm border border-slate-100"
  >
    <div class="flex gap-2 overflow-x-auto no-scrollbar">
      {#each [["classrooms", "الكلاسات"], ["users", "المستخدمين"], ["invites", "الدعوات"], ["roles", "إنشاء رتبة"]] as [id, label]}
        <button
          on:click={() => (activeTab = id as any)}
          class="px-6 py-3 rounded-2xl text-xs font-black transition-all {activeTab ===
          id
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-200'
            : 'text-slate-400 hover:bg-slate-50'}"
        >
          {label}
        </button>
      {/each}
    </div>

    {#if activeTab === "users"}
      <div class="relative w-full md:w-64">
        <input
          bind:value={searchQuery}
          placeholder="بحث عن اسم أو إيميل..."
          class="w-full pr-10 pl-4 py-2.5 bg-slate-50 border-none rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-blue-500/20"
        />
      </div>
    {/if}
  </div>

  {#if activeTab === "users"}
    <div class="flex flex-wrap gap-3 items-center" in:fade>
      {#if userSubTab === "normal"}
        <select
          bind:value={filterRoleId}
          class="bg-white border border-slate-100 px-4 py-2 rounded-xl text-[10px] font-black text-slate-500 outline-none"
        >
          <option value="4">الطلاب</option>
          <option value="3">الأساتذة</option>
        </select>
      {/if}

      <select
        bind:value={filterStateId}
        class="bg-white border border-slate-100 px-4 py-2 rounded-xl text-[10px] font-black text-slate-500 outline-none"
      >
        <option value="">كل الحالات</option>
        <option value="1">نشط</option>
        <option value="2">معطل</option>
      </select>

      <button
        on:click={() => {
          filterRoleId = "";
          filterStateId = "";
          searchQuery = "";
        }}
        class="text-[10px] font-black text-blue-600 hover:underline"
      >
        تصفير الفلاتر
      </button>
    </div>

    <div
      class="flex gap-4 bg-white/50 p-2 rounded-3xl border border-slate-100 w-fit"
    >
      <button
        on:click={() => (userSubTab = "normal")}
        class="px-8 py-3 rounded-2xl text-[11px] font-black transition-all {userSubTab ===
        'normal'
          ? 'bg-white shadow-sm text-blue-600'
          : 'text-slate-400'}"
      >
        المستخدمين
      </button>
      <button
        on:click={() => (userSubTab = "managers")}
        class="px-8 py-3 rounded-2xl text-[11px] font-black transition-all {userSubTab ===
        'managers'
          ? 'bg-white shadow-sm text-blue-600'
          : 'text-slate-400'}"
      >
        المدراء
      </button>
    </div>
  {/if}

  {#if loading}
    <div class="flex justify-center py-20">
      <div
        class="animate-spin rounded-full h-8 w-8 border-[3px] border-blue-600 border-t-transparent"
      ></div>
    </div>
  {:else}
    <div in:fly={{ y: 10 }}>
      {#if activeTab === "classrooms"}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div
            class="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm h-fit"
          >
            <h3 class="text-xl font-black mb-8 text-slate-800">
              إضافة كلاس جديد
            </h3>

            <div class="space-y-4">
              <input
                bind:value={newClassName}
                placeholder="اسم المادة"
                class="w-full p-5 bg-slate-50 border-none rounded-3xl outline-none font-bold focus:ring-2 focus:ring-blue-500/20"
              />

              <div class="relative">
                <input
                  type="file"
                  accept="image/*"
                  on:change={handleFileChange}
                  bind:this={fileInput}
                  class="hidden"
                  id="class-image"
                />
                <label
                  for="class-image"
                  class="flex items-center justify-between w-full p-5 bg-slate-50 rounded-3xl cursor-pointer hover:bg-slate-100 transition-colors border-2 border-dashed border-slate-200"
                >
                  <span class="text-xs font-black text-slate-500">
                    {selectedFile
                      ? selectedFile.name
                      : "اختر صورة مصغرة (اختياري)"}
                  </span>
                  <div class="bg-white p-2 rounded-xl shadow-sm">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="text-blue-600"
                      ><rect
                        width="18"
                        height="18"
                        x="3"
                        y="3"
                        rx="2"
                        ry="2"
                      /><circle cx="9" cy="9" r="2" /><path
                        d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"
                      /></svg
                    >
                  </div>
                </label>
              </div>

              <button
                on:click={createClass}
                disabled={loading}
                class="w-full py-5 bg-blue-600 text-white rounded-3xl font-black shadow-xl hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {#if loading}
                  جاري الحفظ...
                {:else}
                  تأكيد الحفظ
                {/if}
              </button>
            </div>
          </div>

          <div class="space-y-4">
            {#each classrooms as cls}
              <div
                class="bg-white p-6 rounded-[2.5rem] border border-slate-100 flex justify-between items-center group hover:border-blue-200 transition-all shadow-sm"
              >
                <div class="flex items-center gap-5">
                  <div
                    class="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center font-black uppercase text-[10px]"
                  >
                    ID
                  </div>
                  <span class="font-black text-slate-700">{cls.class_name}</span
                  >
                </div>

                <button
                  on:click={() => deleteClass(cls.class_id)}
                  class="text-slate-300 hover:text-red-500 p-2 hover:bg-red-50 rounded-xl transition-all"
                >
                  <Trash2 size={20} strokeWidth={2.5} />
                </button>
              </div>
            {/each}
          </div>
        </div>
      {:else if activeTab === "users"}
        <div
          class="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden overflow-x-auto"
        >
          <table class="w-full text-right">
            <thead
              class="bg-slate-50 text-slate-400 text-[10px] font-black uppercase tracking-widest"
            >
              <tr>
                <th class="px-8 py-5 text-right">البيانات الشخصية</th>
                {#if isShowingTeachers}
                  <th class="px-8 py-5 text-right">الكلاس / المادة</th>
                {/if}
                <th class="px-8 py-5 text-right">الرتبة الحالية</th>
                <th class="px-8 py-5 text-right">الحالة</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              {#each filteredDisplay as user}
                <tr class="hover:bg-slate-50/50 transition-colors">
                  <td class="px-8 py-6">
                    <div class="font-black text-slate-800 text-sm">
                      {user.name}
                    </div>
                    <div class="text-[10px] text-slate-400 font-bold">
                      {user.email}
                    </div>
                  </td>

                  {#if isShowingTeachers}
                    <td class="px-8 py-6">
                      {#if user.class_name}
                        <span
                          class="px-3 py-1 bg-slate-50 text-slate-600 rounded-full text-[10px] font-black border border-slate-100"
                        >
                          {user.class_name}
                        </span>
                      {:else}
                        <span class="text-[10px] text-slate-300 font-bold"
                          >---</span
                        >
                      {/if}
                    </td>
                  {/if}

                  <td class="px-8 py-6">
                    {#if userSubTab === "managers"}
                      <div class="flex items-center gap-2">
                        <select
                          value={pendingRoles[user.user_id] ??
                            String(user.roles_id)}
                          on:change={(e) => {
                            pendingRoles = {
                              ...pendingRoles,
                              [user.user_id]: e.currentTarget.value,
                            };
                          }}
                          class="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-xl text-[10px] font-black border-none outline-none focus:ring-2 focus:ring-blue-100 cursor-pointer"
                        >
                          {#each roles as role}
                            <option value={String(role.roles_id)}
                              >{role.roles_name}</option
                            >
                          {/each}
                        </select>
                        {#if pendingRoles[user.user_id] && pendingRoles[user.user_id] !== String(user.roles_id)}
                          <button
                            on:click={() =>
                              changeUserRole(
                                user.user_id,
                                pendingRoles[user.user_id],
                              )}
                            class="px-3 py-1.5 bg-blue-600 text-white rounded-xl text-[10px] font-black hover:bg-blue-700 transition-all"
                          >
                            حفظ
                          </button>
                        {/if}
                      </div>
                    {:else}
                      <span
                        class="px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[10px] font-black"
                      >
                        {user.roles_name || "مستخدم"}
                      </span>
                    {/if}
                  </td>

                  <td class="px-8 py-6">
                    {#if userSubTab === "managers"}
                      <button
                        on:click={() =>
                          toggleUserStatus(user.user_id, user.state_name || "")}
                        class="flex items-center gap-2 group/status transition-all"
                        title={user.state_name === "Active" ? "تعطيل" : "تفعيل"}
                      >
                        <span
                          class="px-3 py-1 rounded-full text-[10px] font-black transition-all {user.state_name ===
                          'Active'
                            ? 'bg-green-50 text-green-600 group-hover/status:bg-green-100'
                            : 'bg-red-50 text-red-600 group-hover/status:bg-red-100'}"
                        >
                          {user.state_name === "Active" ? "نشط" : "معطل"}
                        </span>
                        <div
                          class="text-slate-300 group-hover/status:text-blue-500 transition-colors"
                        >
                          {#if user.state_name === "Active"}
                            <ToggleRight size={20} />
                          {:else}
                            <ToggleLeft size={20} />
                          {/if}
                        </div>
                      </button>
                    {:else}
                      <span
                        class="px-3 py-1 rounded-full text-[10px] font-black transition-all
                    {user.state_id === 1
                          ? 'bg-green-50 text-green-600'
                          : 'bg-red-50 text-red-600'}"
                      >
                        {user.state_id === 1 ? "نشط" : "معطل"}
                      </span>
                    {/if}
                  </td>
                </tr>
              {/each}

              {#if filteredDisplay.length === 0}
                <tr>
                  <td
                    colspan={isShowingTeachers ? 4 : 3}
                    class="px-8 py-20 text-center text-slate-400 font-bold"
                  >
                    لا يوجد بيانات لعرضها
                  </td>
                </tr>
              {/if}
            </tbody>
          </table>
        </div>
      {:else if activeTab === "invites"}
        <div
          class="max-w-xl mx-auto bg-white p-12 rounded-[3.5rem] border border-slate-100 shadow-sm text-center"
        >
          <h3 class="text-2xl font-black text-slate-800">دعوة مدير جديد</h3>
          <div class="space-y-4 mt-8">
            <input
              bind:value={inviteEmail}
              placeholder="البريد الإلكتروني"
              class="w-full p-5 bg-slate-50 border-none rounded-3xl outline-none font-bold focus:ring-2 focus:ring-blue-500/20"
            />
            <select
              bind:value={selectedRoleId}
              class="w-full p-5 bg-slate-50 border-none rounded-3xl outline-none font-black text-slate-500"
            >
              <option value="">اختر رتبة المدير</option>
              {#each roles as role}
                <option value={role.roles_id.toString()}
                  >{role.roles_name}</option
                >
              {/each}
            </select>
            <button
              on:click={sendInvite}
              class="w-full py-5 bg-slate-900 text-white rounded-3xl font-black hover:bg-black shadow-2xl transition-all"
            >
              إرسال رابط الدعوة
            </button>
          </div>
        </div>
      {:else if activeTab === "roles"}
        <div
          class="max-w-3xl mx-auto bg-white p-12 rounded-[3.5rem] border border-slate-100 shadow-sm"
        >
          <h3 class="text-2xl font-black text-slate-800 text-center">
            تخصيص رتبة جديدة
          </h3>
          <div class="space-y-8 mt-8">
            <input
              bind:value={newRoleName}
              placeholder="اسم الرتبة (مثال: مشرف كلاس)"
              class="w-full p-5 bg-slate-50 border-none rounded-3xl outline-none font-black text-blue-600"
            />

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              {#each permissions as perm}
                <label
                  class="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl cursor-pointer hover:bg-blue-50 border border-transparent hover:border-blue-200 transition-all"
                >
                  <input
                    type="checkbox"
                    value={perm.permission_id}
                    bind:group={selectedPermissions}
                    class="w-5 h-5 accent-blue-600 rounded-lg"
                  />
                  <span class="font-black text-slate-700 text-xs"
                    >{perm.name}</span
                  >
                </label>
              {/each}
            </div>

            <button
              on:click={createRole}
              class="w-full py-5 bg-blue-600 text-white rounded-3xl font-black hover:bg-blue-700 shadow-2xl transition-all"
            >
              حفظ وتفعيل الرتبة
            </button>
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
