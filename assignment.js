const STORAGE_KEY = "burnout_assignments";

document.addEventListener("DOMContentLoaded", loadAssignments);

function loadAssignments() {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {
        pending: [],
        completed: []
    };

    data.pending.forEach(a => renderAssignment(a, false));
    data.completed.forEach(a => renderAssignment(a, true));

    updateStats();
}

function saveAssignments() {
    const pending = [];
    const completed = [];

    document.querySelectorAll("#pendingList li").forEach(li => pending.push(li.data));
    document.querySelectorAll("#completedList li").forEach(li => completed.push(li.data));

    localStorage.setItem(STORAGE_KEY, JSON.stringify({ pending, completed }));
    updateStats();
}

function addAssignment() {
    const title = assignmentInput.value.trim();
    const dueDate = dueDateInput.value;
    const priority = priorityInput.value;

    if (!title || !dueDate) return;

    const data = { title, dueDate, priority };
    renderAssignment(data, false);

    assignmentInput.value = "";
    dueDateInput.value = "";

    saveAssignments();
}

function renderAssignment(data, completed) {
    const li = document.createElement("li");
    li.data = data;

    const today = new Date().toISOString().split("T")[0];
    const overdue = !completed && data.dueDate < today;

    li.className = `
        task 
        ${data.priority.toLowerCase()} 
        ${overdue ? "overdue-task" : ""}
    `;

    li.innerHTML = `
        <b>${data.title}</b>
        <small>📅 ${data.dueDate} · ⚡ ${data.priority}</small>
    `;

    li.onclick = () => toggleTask(li, completed);

    (completed ? completedList : pendingList).appendChild(li);
}

function toggleTask(li, completed) {
    li.remove();
    renderAssignment(li.data, !completed);
    saveAssignments();
}

function updateStats() {
    const pending = document.querySelectorAll("#pendingList li");
    const completed = document.querySelectorAll("#completedList li");

    const today = new Date().toISOString().split("T")[0];
    let overdue = 0;

    pending.forEach(li => {
        if (li.data.dueDate < today) overdue++;
    });

    document.getElementById("upcomingCount").textContent = pending.length - overdue;
    document.getElementById("overdueCount").textContent = overdue;
    document.getElementById("completedCount").textContent = completed.length;
}