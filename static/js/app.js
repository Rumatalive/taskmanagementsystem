const state = { tasks: [], filter: "all", query: "", editingId: null };
const $ = (selector) => document.querySelector(selector);

async function request(url, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  if (csrfToken) headers["X-CSRFToken"] = csrfToken;
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) throw new Error("The task could not be saved.");
  return response.status === 204 ? null : response.json();
}

async function loadTasks() {
  const response = await request(`/api/tasks/?search=${encodeURIComponent(state.query)}`);
  state.tasks = Array.isArray(response) ? response : response.results;
  render();
}

function visibleTasks() {
  return state.tasks.filter((task) => state.filter === "all" || task.status === state.filter);
}

function render() {
  const tasks = visibleTasks();
  $("#task-grid").innerHTML = tasks.map((task, index) => `
    <article class="task-card ${task.status === "done" ? "done" : ""}" style="animation-delay:${index * 45}ms">
      <div class="task-top"><div><h2 class="task-title">${escapeHtml(task.title)}</h2><span class="status-badge ${task.status}">${statusLabel(task.status)}</span></div><button class="task-menu" data-edit="${task.id}" aria-label="Edit ${escapeHtml(task.title)}">•••</button></div>
      ${task.description ? `<p class="task-description">${escapeHtml(task.description)}</p>` : ""}
      <div class="task-footer"><span class="tag ${task.priority}">${task.priority}</span><span class="task-date">${task.due_date ? `Due ${formatDate(task.due_date)}` : "No due date"}</span></div>
      <div class="task-actions"><button class="action-button" data-edit="${task.id}">Edit</button><button class="action-button danger" data-delete="${task.id}">Delete</button><button class="action-button complete" data-toggle-status="${task.id}">${task.status === "done" ? "Mark pending" : "Complete"}</button></div>
    </article>`).join("");
  $("#empty-state").classList.toggle("hidden", tasks.length > 0);
  const done = state.tasks.filter((task) => task.status === "done").length;
  const total = state.tasks.length;
  const percent = total ? Math.round((done / total) * 100) : 0;
  $("#total-count").textContent = total;
  $("#done-count").textContent = done;
  $("#today-count").textContent = state.tasks.filter((task) => task.status !== "done").length;
  $("#progress-label").textContent = `${percent}% done`;
  $("#progress-bar").style.width = `${percent}%`;
}

function openDialog(task = null) {
  state.editingId = task?.id ?? null;
  $("#dialog-title").textContent = task ? "Edit task" : "New task";
  $("#task-title").value = task?.title ?? "";
  $("#task-description").value = task?.description ?? "";
  $("#task-status").value = task?.status ?? "todo";
  $("#task-priority").value = task?.priority ?? "medium";
  $("#task-due-date").value = task?.due_date ?? "";
  $("#task-dialog").showModal();
  $("#task-title").focus();
}

$("#new-task").addEventListener("click", () => openDialog());
$("#empty-new-task").addEventListener("click", () => openDialog());
$("#close-dialog").addEventListener("click", () => $("#task-dialog").close());
$("#cancel-task").addEventListener("click", () => $("#task-dialog").close());
$("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.currentTarget));
  if (!payload.due_date) payload.due_date = null;
  await request(state.editingId ? `/api/tasks/${state.editingId}/` : "/api/tasks/", { method: state.editingId ? "PUT" : "POST", body: JSON.stringify(payload) });
  $("#task-dialog").close();
  await loadTasks();
});

$("#task-grid").addEventListener("click", async (event) => {
  const editId = event.target.dataset.edit;
  const deleteId = event.target.dataset.delete;
  if (editId) openDialog(state.tasks.find((task) => task.id === Number(editId)));
    const toggleId = event.target.dataset.toggleStatus;
  if (deleteId && confirm("Delete this task?")) { await request(`/api/tasks/${deleteId}/`, { method: "DELETE" }); await loadTasks(); }
    if (toggleId) { const task = state.tasks.find((item) => item.id === Number(toggleId)); await request(`/api/tasks/${toggleId}/`, { method: "PATCH", body: JSON.stringify({ status: task.status === "done" ? "todo" : "done" }) }); await loadTasks(); }
});
document.querySelectorAll(".filter-tab").forEach((tab) => tab.addEventListener("click", () => { document.querySelector(".filter-tab.active").classList.remove("active"); tab.classList.add("active"); state.filter = tab.dataset.filter; render(); }));
$("#search-input").addEventListener("input", (event) => { state.query = event.target.value; clearTimeout(window.searchTimer); window.searchTimer = setTimeout(loadTasks, 250); });

function escapeHtml(value) { return value.replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character])); }
function formatDate(value) { return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(`${value}T00:00:00`)); }
function statusLabel(value) { return { todo: "Pending", in_progress: "In progress", done: "Completed" }[value] ?? value; }
loadTasks().catch(() => { $("#empty-state").classList.remove("hidden"); });