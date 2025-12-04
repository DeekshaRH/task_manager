// DOM Elements
const taskForm = document.getElementById('taskForm');
const editTaskForm = document.getElementById('editTaskForm');
const editModal = document.getElementById('editModal');
const closeModal = document.querySelector('.close');
const filterButtons = document.querySelectorAll('.filter-btn');

// Add Task Form Submission
taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value || null,
        priority: document.getElementById('priority').value,
        status: document.getElementById('status').value,
        due_date: document.getElementById('due_date').value || null
    };
    
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('Task added successfully!');
            taskForm.reset();
            location.reload(); // Reload to show new task
        } else {
            const error = await response.json();
            alert('Error adding task: ' + error.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding task. Please try again.');
    }
});

// Edit Task Function
async function editTask(taskId) {
    try {
        const response = await fetch(`/api/tasks`);
        const tasks = await response.json();
        const task = tasks.find(t => t.id === taskId);
        
        if (!task) {
            alert('Task not found');
            return;
        }
        
        // Populate form
        document.getElementById('editTaskId').value = task.id;
        document.getElementById('editTitle').value = task.title;
        document.getElementById('editDescription').value = task.description || '';
        document.getElementById('editPriority').value = task.priority;
        document.getElementById('editStatus').value = task.status;
        
        // Format date for input field (YYYY-MM-DD)
        if (task.due_date) {
            const date = new Date(task.due_date);
            const formattedDate = date.toISOString().split('T')[0];
            document.getElementById('editDueDate').value = formattedDate;
        } else {
            document.getElementById('editDueDate').value = '';
        }
        
        // Show modal
        editModal.style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading task details');
    }
}

// Edit Task Form Submission
editTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const taskId = document.getElementById('editTaskId').value;
    const formData = {
        title: document.getElementById('editTitle').value,
        description: document.getElementById('editDescription').value || null,
        priority: document.getElementById('editPriority').value,
        status: document.getElementById('editStatus').value,
        due_date: document.getElementById('editDueDate').value || null
    };
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('Task updated successfully!');
            editModal.style.display = 'none';
            location.reload(); // Reload to show updated task
        } else {
            const error = await response.json();
            alert('Error updating task: ' + error.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating task. Please try again.');
    }
});

// Delete Task Function
async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Task deleted successfully!');
            location.reload(); // Reload to remove deleted task
        } else {
            const error = await response.json();
            alert('Error deleting task: ' + error.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting task. Please try again.');
    }
}

// Filter Tasks
filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons
        filterButtons.forEach(btn => btn.classList.remove('active'));
        // Add active class to clicked button
        button.classList.add('active');
        
        const filter = button.getAttribute('data-filter');
        const taskCards = document.querySelectorAll('.task-card');
        
        taskCards.forEach(card => {
            if (filter === 'all') {
                card.style.display = 'block';
            } else {
                const status = card.getAttribute('data-status');
                if (status === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    });
});

// Modal Close Handlers
closeModal.addEventListener('click', () => {
    editModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === editModal) {
        editModal.style.display = 'none';
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && editModal.style.display === 'block') {
        editModal.style.display = 'none';
    }
});

// Make functions globally available
window.editTask = editTask;
window.deleteTask = deleteTask;

console.log('Task Manager Frontend Loaded Successfully!');
