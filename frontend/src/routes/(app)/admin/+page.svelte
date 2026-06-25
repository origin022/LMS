<script lang="ts">
  import { onMount } from "svelte";
  import { apiFetch, FILE_URL } from "$lib/api";
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
    class_image?: string;
    department_id?: number;
    department_name?: string;
  }

  interface Department {
    department_id: number;
    name: string;
  }

  let activeTab: "departments" | "classrooms" | "users" | "invites" | "roles" =
    "departments";
  let userSubTab: "normal" | "managers" = "normal";
  let loading = false;

  let classrooms: Classroom[] = [];
  let departments: Department[] = [];
  let users: UserAdmin[] = [];
  let roles: Role[] = [];
  let permissions: Permission[] = [];

  let searchQuery = "";
  let filterRoleId = "";
  let filterStateId = "";
  let filterClassDeptId = "";

  let newClassName = "";
  let selectedDeptId: string = "";
  let newDeptName = "";
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
      if (activeTab === "departments") {
        const res = await apiFetch("/admin/departments");
        if (res.ok) departments = await res.json();
      } else if (activeTab === "classrooms") {
        const [cRes, dRes] = await Promise.all([
          apiFetch("/admin/classrooms/all"),
          apiFetch("/admin/departments"),
        ]);
        if (cRes.ok) {
          classrooms = (await cRes.json()).sort(
            (a: any, b: any) => b.class_id - a.class_id,
          );
        }
        if (dRes.ok) departments = await dRes.json();
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
        if (res.ok) {
          const data = await res.json();
          const unique = new Map();
          for (const item of data) {
            if (!unique.has(item.name)) {
              unique.set(item.name, item);
            }
          }
          permissions = Array.from(unique.values());
        }
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

  $: filteredClassrooms = classrooms.filter((cls) => {
    if (filterClassDeptId && cls.department_id !== parseInt(filterClassDeptId))
      return false;
    return true;
  });

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
    loading = true;
    try {
      const formData = new FormData();
      formData.append("name", newClassName);
      if (selectedDeptId) {
        formData.append("department_id", selectedDeptId);
      }
      if (selectedFile) {
        formData.append("image", selectedFile);
      }

      const res = await apiFetch("/admin/classrooms", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        newClassName = "";
        selectedDeptId = "";
        selectedFile = null;
        if (fileInput) fileInput.value = "";
        showMsg("تم إنشاء المجال بنجاح");
        loadData();
      } else {
        const err = await res.json();
        showMsg(err.detail || "فشل إنشاء المجال", "error");
      }
    } catch (e) {
      showMsg("حدث خطأ في الاتصال", "error");
    } finally {
      loading = false;
    }
  }

  async function createDept() {
    if (!newDeptName) return showMsg("يرجى إدخال اسم القسم", "error");
    try {
      const res = await apiFetch("/admin/departments", {
        method: "POST",
        body: JSON.stringify({ name: newDeptName }),
      });
      if (res.ok) {
        newDeptName = "";
        showMsg("تم إنشاء القسم بنجاح");
        loadData();
      }
    } catch (e) {
      showMsg("فشل إنشاء القسم", "error");
    }
  }

  async function deleteDept(id: number) {
    if (!confirm("هل أنت متأكد من حذف القسم؟ سيتم فك ارتباطه بالمجالات."))
      return;
    const res = await apiFetch(`/admin/departments/${id}`, {
      method: "DELETE",
    });
    if (res.status === 204) {
      showMsg("تم حذف القسم");
      loadData();
    }
  }

  function handleFileChange(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      selectedFile = target.files[0];
    }
  }

  async function deleteClass(id: number) {
    if (!confirm("حذف المجال؟")) return;
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
    <div
      class="flex gap-3 overflow-x-auto no-scrollbar w-full pb-2 px-2 scroll-smooth"
    >
      {#each [["departments", "الأقسام"], ["classrooms", "المجالات الدراسية"], ["users", "المستخدمين"], ["invites", "الدعوات"], ["roles", "إدارة الرتب"]] as [id, label]}
        <button
          on:click={() => (activeTab = id as any)}
          class="whitespace-nowrap px-6 py-3 rounded-2xl text-[11px] md:text-xs font-black transition-all flex-shrink-0 {activeTab ===
          id
            ? 'bg-blue-600 text-white shadow-lg shadow-blue-200'
            : 'text-slate-400 hover:bg-slate-50 border border-transparent hover:border-slate-100'}"
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
      {#if activeTab === "departments"}
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8" in:fade>
          <!-- Create Dept Card -->
          <div class="lg:col-span-5">
            <div
              class="bg-white p-8 md:p-12 rounded-[3.5rem] border border-slate-100 shadow-xl shadow-blue-500/5 sticky top-8"
            >
              <div
                class="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mb-6"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="text-blue-600"
                  ><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle
                    cx="9"
                    cy="7"
                    r="4"
                  /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path
                    d="M16 3.13a4 4 0 0 1 0 7.75"
                  /></svg
                >
              </div>
              <h3 class="text-2xl font-black text-slate-800 mb-2">
                إضافة قسم جديد
              </h3>
              <p class="text-xs font-bold text-slate-400 mb-8 leading-relaxed">
                قم بإنشاء الأقسام الرئيسية لتنظيم المجالات الدراسية بداخلها.
              </p>

              <div class="space-y-4">
                <div class="relative group">
                  <input
                    bind:value={newDeptName}
                    placeholder="اسم القسم (مثال: الفرع العلمي)"
                    class="w-full p-5 bg-slate-50 border-2 border-transparent rounded-3xl outline-none font-bold transition-all focus:bg-white focus:border-blue-500/20 text-slate-700"
                  />
                </div>
                <button
                  on:click={createDept}
                  class="w-full py-5 bg-blue-600 text-white rounded-3xl font-black shadow-xl shadow-blue-600/20 hover:bg-blue-700 hover:scale-[1.02] transition-all active:scale-95 flex items-center justify-center gap-3"
                >
                  <span>تأكيد الإضافة</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    ><path d="M5 12h14" /><path d="M12 5v14" /></svg
                  >
                </button>
              </div>
            </div>
          </div>

          <!-- Dept List -->
          <div class="lg:col-span-7 space-y-4">
            <div class="flex items-center justify-between px-4 mb-2">
              <h4
                class="text-xs font-black text-slate-400 uppercase tracking-widest"
              >
                الأقسام المتاحة حالياً
              </h4>
              <span
                class="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-[10px] font-black"
                >{departments.length} أقسام</span
              >
            </div>

            <div class="grid grid-cols-1 gap-4">
              {#each departments as dept}
                <div
                  in:fly={{ y: 10, delay: 50 }}
                  class="bg-white p-6 rounded-[2.5rem] border border-slate-100 flex justify-between items-center group hover:border-blue-200 transition-all shadow-sm hover:shadow-md"
                >
                  <div class="flex items-center gap-5">
                    <div
                      class="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-2xl flex items-center justify-center font-black text-xl shadow-lg shadow-blue-500/20"
                    >
                      {dept.name[0]}
                    </div>
                    <div class="flex flex-col">
                      <span
                        class="font-black text-slate-800 text-lg leading-none"
                        >{dept.name}</span
                      >
                    </div>
                  </div>

                  <button
                    on:click={() => deleteDept(dept.department_id)}
                    class="w-12 h-12 flex items-center justify-center bg-slate-50 text-slate-300 hover:bg-red-50 hover:text-red-500 rounded-2xl transition-all active:scale-90"
                    title="حذف القسم"
                  >
                    <Trash2 size={20} strokeWidth={2.5} />
                  </button>
                </div>
              {:else}
                <div
                  class="py-20 text-center bg-white rounded-[3.5rem] border border-dashed border-slate-200"
                >
                  <div
                    class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="32"
                      height="32"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="text-slate-300"
                      ><path
                        d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
                      /><circle cx="9" cy="7" r="4" /><path
                        d="m16 11 5 5"
                      /><path d="m11 16 5 5" /></svg
                    >
                  </div>
                  <p class="text-slate-400 font-bold">
                    لا يوجد أقسام مضافة بعد
                  </p>
                </div>
              {/each}
            </div>
          </div>
        </div>
      {:else if activeTab === "classrooms"}
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8" in:fade>
          <!-- Create Classroom Card -->
          <div class="lg:col-span-5">
            <div
              class="bg-white p-8 md:p-12 rounded-[3.5rem] border border-slate-100 shadow-xl shadow-blue-500/5 sticky top-8"
            >
              <div
                class="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mb-6"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="text-blue-600"
                  ><rect
                    x="3"
                    y="3"
                    width="18"
                    height="18"
                    rx="2"
                    ry="2"
                  /><line x1="3" y1="9" x2="21" y2="9" /><line
                    x1="9"
                    y1="21"
                    x2="9"
                    y2="9"
                  /></svg
                >
              </div>
              <h3 class="text-2xl font-black text-slate-800 mb-2">
                إضافة مجال دراسي
              </h3>
              <p class="text-xs font-bold text-slate-400 mb-8 leading-relaxed">
                قم بإنشاء مجال دراسي جديد (مثل مادة الرياضيات) وربطه بقسم معين.
              </p>

              <div class="space-y-5">
                <div class="space-y-2">
                  <label
                    class="text-[10px] font-black text-slate-400 mr-2 uppercase tracking-widest"
                    >اسم المادة</label
                  >
                  <input
                    bind:value={newClassName}
                    placeholder="مثال: اللغة العربية"
                    class="w-full p-5 bg-slate-50 border-2 border-transparent rounded-3xl outline-none font-bold transition-all focus:bg-white focus:border-blue-500/20 text-slate-700"
                  />
                </div>

                <div class="space-y-2">
                  <label
                    class="text-[10px] font-black text-slate-400 mr-2 uppercase tracking-widest"
                    >القسم التابع له</label
                  >
                  <select
                    bind:value={selectedDeptId}
                    class="w-full p-5 bg-slate-50 border-2 border-transparent rounded-3xl outline-none font-bold transition-all focus:bg-white focus:border-blue-500/20 text-slate-500 appearance-none cursor-pointer"
                  >
                    <option value="">غير مرتبط بقسم</option>
                    {#each departments as dept}
                      <option value={String(dept.department_id)}
                        >{dept.name}</option
                      >
                    {/each}
                  </select>
                </div>

                <div class="space-y-2">
                  <label
                    class="text-[10px] font-black text-slate-400 mr-2 uppercase tracking-widest"
                    >صورة الغلاف</label
                  >
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
                    class="flex items-center justify-between w-full p-5 bg-slate-50 rounded-3xl cursor-pointer hover:bg-slate-100 transition-all border-2 border-dashed border-slate-200 group/file"
                  >
                    <span
                      class="text-xs font-bold text-slate-500 truncate max-w-[200px]"
                    >
                      {selectedFile
                        ? selectedFile.name
                        : "اختر صورة جذابة للمجال"}
                    </span>
                    <div
                      class="bg-white p-2 rounded-xl shadow-sm group-hover/file:scale-110 transition-transform"
                    >
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
                  class="w-full py-5 bg-blue-600 text-white rounded-3xl font-black shadow-xl shadow-blue-600/20 hover:bg-blue-700 hover:scale-[1.02] transition-all active:scale-95 flex items-center justify-center gap-3 mt-4"
                >
                  {#if loading}
                    <div
                      class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"
                    ></div>
                    <span>جاري الإنشاء...</span>
                  {:else}
                    <span>تأكيد الحفظ</span>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"><path d="M5 13l4 4L19 7" /></svg
                    >
                  {/if}
                </button>
              </div>
            </div>
          </div>

          <!-- Classroom List -->
          <div class="lg:col-span-7 space-y-6">
            <div
              class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-4 bg-white/50 p-6 rounded-[2.5rem] border border-slate-100"
            >
              <div class="flex flex-col">
                <h4 class="text-sm font-black text-slate-800">
                  تصفية المجالات
                </h4>
                <p class="text-[10px] font-bold text-slate-400">
                  عرض المجالات حسب القسم المختار
                </p>
              </div>
              <select
                bind:value={filterClassDeptId}
                class="bg-white border-none shadow-sm px-6 py-3 rounded-2xl text-xs font-black text-blue-600 outline-none focus:ring-2 ring-blue-500/10"
              >
                <option value="">جميع المجالات</option>
                {#each departments as dept}
                  <option value={String(dept.department_id)}>{dept.name}</option
                  >
                {/each}
              </select>
            </div>

            <div class="grid grid-cols-1 gap-4">
              {#each filteredClassrooms as cls}
                <div
                  in:fly={{ y: 20, delay: 100 }}
                  class="bg-white p-5 rounded-[2.5rem] border border-slate-100 flex items-center gap-5 group hover:border-blue-200 transition-all shadow-sm hover:shadow-xl hover:shadow-blue-500/5"
                >
                  <div
                    class="w-20 h-20 bg-blue-50 rounded-[1.75rem] overflow-hidden flex-shrink-0 border border-slate-50 relative group-hover:scale-105 transition-transform duration-500"
                  >
                    {#if cls.class_image}
                      <img
                        src={cls.class_image.startsWith('http') ? cls.class_image : FILE_URL + cls.class_image}
                        alt={cls.class_name}
                        class="w-full h-full object-cover"
                      />
                    {:else}
                      <div
                        class="w-full h-full flex items-center justify-center text-blue-300"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="32"
                          height="32"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="1.5"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          class="opacity-40"
                          ><path
                            d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"
                          /><path d="M8 7h6" /><path d="M8 11h8" /></svg
                        >
                      </div>
                    {/if}
                    <div
                      class="absolute inset-0 bg-blue-600/0 group-hover:bg-blue-600/10 transition-colors"
                    ></div>
                  </div>

                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span
                        class="font-black text-slate-800 text-lg leading-tight"
                        >{cls.class_name}</span
                      >
                    </div>
                  </div>

                  <button
                    on:click={() => deleteClass(cls.class_id)}
                    class="w-12 h-12 flex items-center justify-center text-slate-200 hover:bg-red-50 hover:text-red-500 rounded-2xl transition-all group-hover:text-slate-300"
                    title="حذف المجال"
                  >
                    <Trash2 size={22} strokeWidth={2.5} />
                  </button>
                </div>
              {:else}
                <div
                  class="py-24 text-center bg-white rounded-[3.5rem] border border-dashed border-slate-200"
                >
                  <div
                    class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="32"
                      height="32"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="text-slate-300"
                      ><circle cx="12" cy="12" r="10" /><path
                        d="M12 8v8"
                      /><path d="M8 12h8" /></svg
                    >
                  </div>
                  <p class="text-slate-500 font-bold">
                    لا يوجد مجالات دراسية في هذا القسم حالياً
                  </p>
                  <button
                    on:click={() => (filterClassDeptId = "")}
                    class="mt-4 text-xs font-black text-blue-600 hover:underline"
                    >عرض كل المجالات</button
                  >
                </div>
              {/each}
            </div>
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
                  <th class="px-8 py-5 text-right">المجال الدراسي</th>
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
              placeholder="اسم الرتبة (مثال: مشرف مجال)"
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
