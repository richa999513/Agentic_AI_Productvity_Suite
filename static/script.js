// API Configuration
const API_BASE = 'http://localhost:8000/api';
let currentUserId = null;

// Load user ID on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadUserId();
    setupEventListeners();
    loadDashboardData();
});

// Load or create user ID
async function loadUserId() {
    let userId = localStorage.getItem('userId');
    
    if (!userId) {
        // Create new user
        try {
            const response = await fetch(`${API_BASE}/users/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: `User ${Date.now()}`,
                    email: `user${Date.now()}@example.com`
                })
            });
            const data = await response.json();
            userId = data.user_id;
            localStorage.setItem('userId', userId);
        } catch (error) {
            console.error('Error creating user:', error);
            showToast('Error creating user', 'error');
            return;
        }
    }
    
    currentUserId = userId;
    document.getElementById('user-id-display').textContent = `User: ${userId.substring(0, 8)}...`;
}

// Setup event listeners
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', switchTab);
    });

    // Task form
    document.getElementById('add-task-btn').addEventListener('click', () => {
        toggleForm('task-form');
    });
    document.getElementById('cancel-task-btn').addEventListener('click', () => {
        toggleForm('task-form');
    });
    document.getElementById('task-form').addEventListener('submit', createTask);

    // Event form
    document.getElementById('add-event-btn').addEventListener('click', () => {
        toggleForm('event-form');
    });
    document.getElementById('cancel-event-btn').addEventListener('click', () => {
        toggleForm('event-form');
    });
    document.getElementById('event-form').addEventListener('submit', createEvent);

    // Email form
    document.getElementById('compose-email-btn').addEventListener('click', () => {
        toggleForm('email-form');
    });
    document.getElementById('cancel-email-btn').addEventListener('click', () => {
        toggleForm('email-form');
    });
    document.getElementById('email-form').addEventListener('submit', sendEmail);

    // Note form
    document.getElementById('add-note-btn').addEventListener('click', () => {
        toggleForm('note-form');
    });
    document.getElementById('cancel-note-btn').addEventListener('click', () => {
        toggleForm('note-form');
    });
    document.getElementById('note-form').addEventListener('submit', createNote);

    // Analytics
    document.getElementById('daily-summary-btn').addEventListener('click', getDailySummary);
    document.getElementById('weekly-report-btn').addEventListener('click', getWeeklyReport);
}

// Tab switching
function switchTab(e) {
    const tabId = e.target.dataset.tab;
    
    // Remove active class from all nav items and tab contents
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to clicked nav item and corresponding tab
    e.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
    document.getElementById('page-title').textContent = e.target.textContent;
    
    // Load tab data
    if (tabId === 'tasks') loadTasks();
    if (tabId === 'calendar') loadEvents();
    if (tabId === 'emails') loadEmails();
    if (tabId === 'notes') loadNotes();
}

// Toggle form visibility
function toggleForm(formId) {
    const form = document.getElementById(formId);
    form.classList.toggle('hidden');
    if (!form.classList.contains('hidden')) {
        form.scrollIntoView({ behavior: 'smooth' });
    }
}

// Load dashboard data
async function loadDashboardData() {
    if (!currentUserId) return;
    
    try {
        // Load tasks count
        const tasksRes = await fetch(`${API_BASE}/tasks/${currentUserId}`);
        const tasksData = await tasksRes.json();
        const activeTasks = tasksData.tasks.filter(t => t.status !== 'completed').length;
        document.getElementById('total-tasks').textContent = activeTasks;

        // Load events count
        const eventsRes = await fetch(`${API_BASE}/calendar/${currentUserId}`);
        const eventsData = await eventsRes.json();
        document.getElementById('total-events').textContent = eventsData.events.length;

        // Load emails count (placeholder)
        document.getElementById('total-emails').textContent = '0';

        // Load notes count (placeholder)
        document.getElementById('total-notes').textContent = '0';
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// TASK OPERATIONS
async function createTask(e) {
    e.preventDefault();
    
    const task = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-description').value,
        priority: document.getElementById('task-priority').value,
        status: document.getElementById('task-status').value,
        due_date: document.getElementById('task-due-date').value || null,
        tags: []
    };

    try {
        const response = await fetch(`${API_BASE}/tasks/create/${currentUserId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(task)
        });
        
        if (response.ok) {
            showToast('Task created successfully!');
            resetForm('task-form');
            toggleForm('task-form');
            loadTasks();
            loadDashboardData();
        } else {
            showToast('Error creating task', 'error');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showToast('Error creating task', 'error');
    }
}

async function loadTasks() {
    if (!currentUserId) return;
    
    try {
        const response = await fetch(`${API_BASE}/tasks/${currentUserId}`);
        const data = await response.json();
        const tasksList = document.getElementById('tasks-list');
        
        if (data.tasks.length === 0) {
            tasksList.innerHTML = '<p class="empty-state">No tasks yet. Create your first task!</p>';
            return;
        }

        tasksList.innerHTML = data.tasks.map(task => `
            <div class="task-item">
                <div class="task-header">
                    <span class="task-title">${task.title}</span>
                    <span class="task-priority priority-${task.priority}">${task.priority}</span>
                </div>
                <p class="task-description">${task.description || 'No description'}</p>
                <div>
                    <span class="task-status status-${task.status}">${task.status.replace('_', ' ')}</span>
                </div>
                ${task.due_date ? `<div class="task-meta"><span>📅 Due: ${new Date(task.due_date).toLocaleDateString()}</span></div>` : ''}
                <div class="item-actions">
                    <button class="btn-secondary" onclick="updateTaskStatus('${task.task_id}', 'completed')">✓ Complete</button>
                    <button class="btn-danger" onclick="deleteTask('${task.task_id}')">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading tasks:', error);
        showToast('Error loading tasks', 'error');
    }
}

async function updateTaskStatus(taskId, status) {
    try {
        const response = await fetch(`${API_BASE}/tasks/update/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        
        if (response.ok) {
            showToast('Task updated!');
            loadTasks();
            loadDashboardData();
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showToast('Error updating task', 'error');
    }
}

async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            await fetch(`${API_BASE}/tasks/${taskId}`, { method: 'DELETE' });
            showToast('Task deleted!');
            loadTasks();
            loadDashboardData();
        } catch (error) {
            console.error('Error deleting task:', error);
            showToast('Error deleting task', 'error');
        }
    }
}

// CALENDAR OPERATIONS
async function createEvent(e) {
    e.preventDefault();
    
    const event = {
        title: document.getElementById('event-title').value,
        start_time: document.getElementById('event-start').value,
        end_time: document.getElementById('event-end').value,
        event_type: document.getElementById('event-type').value
    };

    try {
        const response = await fetch(`${API_BASE}/calendar/create/${currentUserId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event)
        });
        
        if (response.ok) {
            showToast('Event created successfully!');
            resetForm('event-form');
            toggleForm('event-form');
            loadEvents();
            loadDashboardData();
        } else {
            showToast('Error creating event', 'error');
        }
    } catch (error) {
        console.error('Error creating event:', error);
        showToast('Error creating event', 'error');
    }
}

async function loadEvents() {
    if (!currentUserId) return;
    
    try {
        const response = await fetch(`${API_BASE}/calendar/${currentUserId}`);
        const data = await response.json();
        const eventsList = document.getElementById('events-list');
        
        if (data.events.length === 0) {
            eventsList.innerHTML = '<p class="empty-state">No events yet. Create your first event!</p>';
            return;
        }

        eventsList.innerHTML = data.events.map(event => `
            <div class="event-item">
                <div class="task-header">
                    <span class="task-title">${event.title}</span>
                    <span class="task-priority priority-${event.event_type}">${event.event_type}</span>
                </div>
                <div class="task-meta">
                    <span>📅 ${new Date(event.start_time).toLocaleDateString()}</span>
                    <span>⏰ ${new Date(event.start_time).toLocaleTimeString()}</span>
                </div>
                <div class="item-actions">
                    <button class="btn-danger" onclick="deleteEvent('${event.event_id}')">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading events:', error);
        showToast('Error loading events', 'error');
    }
}

async function deleteEvent(eventId) {
    if (confirm('Are you sure you want to delete this event?')) {
        try {
            await fetch(`${API_BASE}/calendar/${eventId}`, { method: 'DELETE' });
            showToast('Event deleted!');
            loadEvents();
            loadDashboardData();
        } catch (error) {
            console.error('Error deleting event:', error);
            showToast('Error deleting event', 'error');
        }
    }
}

// EMAIL OPERATIONS
async function sendEmail(e) {
    e.preventDefault();
    
    const emailTo = document.getElementById('email-to').value;
    if (!emailTo) {
        showToast('Recipient email address cannot be empty.', 'error');
        return;
    }

    console.log('DEBUG (frontend): Type of emailTo before array:', typeof emailTo, emailTo);
    const recipients = [emailTo];
    console.log('DEBUG (frontend): Type of recipients array:', typeof recipients, recipients);

    const email = {
        to: recipients,
        subject: document.getElementById('email-subject').value,
        body: document.getElementById('email-body').value,
        cc: [], // Explicitly send empty array if no CC
        attachments: [] // Explicitly send empty array if no attachments
    };

    console.log('DEBUG: Sending email payload:', email);

    try {
        const response = await fetch(`${API_BASE}/emails/send/${currentUserId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(email)
        });
        
        if (response.ok) {
            showToast('Email sent successfully!');
            resetForm('email-form');
            toggleForm('email-form');
            loadEmails();
        } else {
            showToast('Error sending email', 'error');
        }
    } catch (error) {
        console.error('Error sending email:', error);
        showToast('Error sending email', 'error');
    }
}

async function loadEmails() {
    if (!currentUserId) return;
    
    try {
        const response = await fetch(`${API_BASE}/emails/${currentUserId}`);
        const data = await response.json();
        const emailsList = document.getElementById('emails-list');
        
        if (!data.emails || data.emails.length === 0) {
            emailsList.innerHTML = '<p class="empty-state">No emails yet.</p>';
            return;
        }

        emailsList.innerHTML = data.emails.map(email => `
            <div class="email-item">
                <div class="task-header">
                    <span class="task-title">${email.subject}</span>
                </div>
                <p class="task-description">From: ${email.sender || 'Unknown'}</p>
                <div class="item-actions">
                    <button class="btn-danger" onclick="deleteEmail('${email.email_id}')">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading emails:', error);
        showToast('Error loading emails', 'error');
    }
}

async function deleteEmail(emailId) {
    if (confirm('Are you sure you want to delete this email?')) {
        try {
            await fetch(`${API_BASE}/emails/${emailId}`, { method: 'DELETE' });
            showToast('Email deleted!');
            loadEmails();
        } catch (error) {
            console.error('Error deleting email:', error);
            showToast('Error deleting email', 'error');
        }
    }
}

// NOTE OPERATIONS
async function createNote(e) {
    e.preventDefault();
    
    const note = {
        title: document.getElementById('note-title').value,
        content: document.getElementById('note-content').value
    };

    try {
        const response = await fetch(`${API_BASE}/notes/create/${currentUserId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(note)
        });
        
        if (response.ok) {
            showToast('Note created successfully!');
            resetForm('note-form');
            toggleForm('note-form');
            loadNotes();
        } else {
            showToast('Error creating note', 'error');
        }
    } catch (error) {
        console.error('Error creating note:', error);
        showToast('Error creating note', 'error');
    }
}

async function loadNotes() {
    if (!currentUserId) return;
    
    try {
        const response = await fetch(`${API_BASE}/notes/${currentUserId}`);
        const data = await response.json();
        const notesList = document.getElementById('notes-list');
        
        if (!data.notes || data.notes.length === 0) {
            notesList.innerHTML = '<p class="empty-state">No notes yet. Create your first note!</p>';
            return;
        }

        notesList.innerHTML = data.notes.map(note => `
            <div class="note-item">
                <div class="task-header">
                    <span class="task-title">${note.title}</span>
                </div>
                <p class="task-description">${note.content}</p>
                <div class="item-actions">
                    <button class="btn-danger" onclick="deleteNote('${note.note_id}')">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading notes:', error);
        showToast('Error loading notes', 'error');
    }
}

async function deleteNote(noteId) {
    if (confirm('Are you sure you want to delete this note?')) {
        try {
            await fetch(`${API_BASE}/notes/${noteId}`, { method: 'DELETE' });
            showToast('Note deleted!');
            loadNotes();
        } catch (error) {
            console.error('Error deleting note:', error);
            showToast('Error deleting note', 'error');
        }
    }
}

// ANALYTICS OPERATIONS
// Dummy comment to force reload
async function getDailySummary() {
    if (!currentUserId) return;
    
    try {
        const url = `${API_BASE}/analytics/${currentUserId}/summary`;
        console.log('DEBUG: Fetching daily summary from:', url);
        const response = await fetch(url);
        const data = await response.json();
        const summaryDiv = document.getElementById('daily-summary');
        summaryDiv.textContent = data.summary || 'No data available';
    } catch (error) {
        console.error('Error getting daily summary:', error);
        showToast('Error getting daily summary', 'error');
    }
}

async function getWeeklyReport() {
    if (!currentUserId) return;
    
    try {
        const url = `${API_BASE}/analytics/${currentUserId}/weekly`;
        console.log('DEBUG: Fetching weekly report from:', url);
        const response = await fetch(url);
        const data = await response.json();
        const reportDiv = document.getElementById('weekly-report');
        reportDiv.textContent = data.report || 'No data available';
    } catch (error) {
        console.error('Error getting weekly report:', error);
        showToast('Error getting weekly report', 'error');
    }
}

// UTILITY FUNCTIONS
function resetForm(formId) {
    document.getElementById(formId).reset();
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
