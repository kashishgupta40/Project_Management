// API Service for Project Collaborative Features

const API_BASE_URL = '/project-features/api';

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Generic API fetch function
async function apiFetch(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        credentials: 'same-origin',
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {}),
        },
    };

    try {
        const response = await fetch(url, mergedOptions);
        
        // Handle empty responses (like DELETE 204)
        if (response.status === 204) {
            return { success: true, data: {} };
        }
        
        // Try to parse JSON response
        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = {};
        }
        
        if (!response.ok) {
            const errorMsg = data.error || data.detail || data.message || `HTTP ${response.status}`;
            return { success: false, error: errorMsg };
        }
        
        return { success: true, data };
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message || 'An error occurred' };
    }
}

// Share Link API
const ShareAPI = {
    async shareProject(projectId) {
        const url = `${API_BASE_URL}/projects/${projectId}/share/`;
        return await apiFetch(url, {
            method: 'POST',
        });
    },

    async getShareLinks(projectId) {
        const url = `${API_BASE_URL}/share-links/?project_id=${projectId}`;
        return await apiFetch(url, {
            method: 'GET',
        });
    },

    async deactivateShareLink(shareLinkId) {
        const url = `${API_BASE_URL}/share-links/${shareLinkId}/`;
        return await apiFetch(url, {
            method: 'PATCH',
            body: JSON.stringify({ is_active: false }),
        });
    },
};

// Notes API
const NotesAPI = {
    async getNotes(projectId) {
        const url = `${API_BASE_URL}/notes/?project_id=${projectId}`;
        return await apiFetch(url, {
            method: 'GET',
        });
    },

    async createNote(projectId, content) {
        const url = `${API_BASE_URL}/notes/`;
        return await apiFetch(url, {
            method: 'POST',
            body: JSON.stringify({
                project: projectId,
                content: content,
            }),
        });
    },

    async updateNote(noteId, content) {
        const url = `${API_BASE_URL}/notes/${noteId}/`;
        return await apiFetch(url, {
            method: 'PATCH',
            body: JSON.stringify({ content }),
        });
    },

    async deleteNote(noteId) {
        const url = `${API_BASE_URL}/notes/${noteId}/`;
        return await apiFetch(url, {
            method: 'DELETE',
        });
    },
};

// Comments API
const CommentsAPI = {
    async getComments(projectId) {
        const url = `${API_BASE_URL}/comments/?project_id=${projectId}`;
        return await apiFetch(url, {
            method: 'GET',
        });
    },

    async createComment(projectId, message) {
        const url = `${API_BASE_URL}/comments/`;
        return await apiFetch(url, {
            method: 'POST',
            body: JSON.stringify({
                project: projectId,
                message: message,
            }),
        });
    },

    async updateComment(commentId, message) {
        const url = `${API_BASE_URL}/comments/${commentId}/`;
        return await apiFetch(url, {
            method: 'PATCH',
            body: JSON.stringify({ message }),
        });
    },

    async deleteComment(commentId) {
        const url = `${API_BASE_URL}/comments/${commentId}/`;
        return await apiFetch(url, {
            method: 'DELETE',
        });
    },
};

// Reminders API
const RemindersAPI = {
    async getReminders(projectId) {
        const url = `${API_BASE_URL}/reminders/?project_id=${projectId}`;
        return await apiFetch(url, {
            method: 'GET',
        });
    },

    async createReminder(projectId, title, reminderDatetime) {
        const url = `${API_BASE_URL}/reminders/`;
        return await apiFetch(url, {
            method: 'POST',
            body: JSON.stringify({
                project: projectId,
                title: title,
                reminder_datetime: reminderDatetime,
            }),
        });
    },

    async updateReminder(reminderId, data) {
        const url = `${API_BASE_URL}/reminders/${reminderId}/`;
        return await apiFetch(url, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    },

    async deleteReminder(reminderId) {
        const url = `${API_BASE_URL}/reminders/${reminderId}/`;
        return await apiFetch(url, {
            method: 'DELETE',
        });
    },
};

// Utility function to format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

// Utility function to format date for input
function formatDateForInput(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ShareAPI, NotesAPI, CommentsAPI, RemindersAPI, formatDateTime, formatDateForInput };
}

