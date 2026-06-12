/**
 * AI Learning Management System - Main JavaScript
 */

// =============================================================================
// API Client
// =============================================================================

class APIClient {
    constructor() {
        this.baseURL = '/api/v1';
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    setTokens(access, refresh) {
        this.accessToken = access;
        this.refreshToken = refresh;
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
    }

    clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        const accessToken = this.accessToken || localStorage.getItem('access_token');
        if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle token refresh
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    headers['Authorization'] = `Bearer ${this.accessToken}`;
                    return fetch(url, { ...options, headers });
                }
            }

            return response;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: this.refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access, this.refreshToken);
                return true;
            }

            this.clearTokens();
            window.location.href = '/auth/login/';
            return false;
        } catch (error) {
            this.clearTokens();
            return false;
        }
    }

    async get(endpoint) {
        const response = await this.request(endpoint);
        return response.json();
    }

    async post(endpoint, data) {
        const response = await this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        return { response, data: await response.json() };
    }

    async put(endpoint, data) {
        const response = await this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        return { response, data: await response.json() };
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

const api = new APIClient();

// =============================================================================
// Authentication
// =============================================================================

const Auth = {
    async register(data) {
        const { response, data: result } = await api.post('/auth/register/', data);
        if (response.ok) {
            api.setTokens(result.access, result.refresh);
            localStorage.setItem('user', JSON.stringify(result.user));
            return { success: true, user: result.user };
        }
        return { success: false, errors: result };
    },

    async login(email, password) {
        const { response, data: result } = await api.post('/auth/login/', { email, password });
        if (response.ok) {
            api.setTokens(result.access, result.refresh);
            localStorage.setItem('user', JSON.stringify(result.user));
            console.log(result);
            return { success: true, user: result.user };
        }
        return { success: false, errors: result };
    },

    async logout() {
        try {
            await api.post('/auth/logout/', { refresh: api.refreshToken });
        } catch (e) {}
        api.clearTokens();
        window.location.href = '/';
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isAuthenticated() {
        return !!api.accessToken;
    }
};

// =============================================================================
// Course Functions
// =============================================================================

const Courses = {
    async list(params = {}) {
        let query = new URLSearchParams(params).toString();
        return api.get(`/courses/${query ? '?' + query : ''}`);
    },

    async get(id) {
        return api.get(`/courses/${id}/`);
    },

    async enroll(id) {
        return api.post(`/courses/${id}/enroll/`, {});
    },

    async getLessons(courseId) {
        return api.get(`/courses/${courseId}/lessons/`);
    },

    async getLesson(lessonId) {
        return api.get(`/courses/lessons/${lessonId}/`);
    },

    async completeLesson(lessonId) {
        return api.post(`/courses/lessons/${lessonId}/complete/`, {});
    },

    async getMyEnrollments() {
        return api.get('/courses/my-enrollments/');
    },

    async getProgress(courseId) {
        return api.get(`/progress/${courseId}/`);
    },

    async getAllProgress() {
        return api.get('/progress/');
    }
};

// =============================================================================
// Quiz Functions
// =============================================================================

const Quiz = {
    async list(courseId) {
        return api.get(`/quiz/?course=${courseId}`);
    },

    async get(id) {
        return api.get(`/quiz/${id}/`);
    },

    async create(data) {
        return api.post('/quiz/create/', data);
    },

    async createQuestion(quizId, data) {
        return api.post(`/quiz/${quizId}/questions/create/`, data);
    },

    async start(id) {
        return api.post(`/quiz/${id}/start/`, {});
    },

    async submit(id, answers) {
        return api.post(`/quiz/${id}/submit/`, { answers });
    },

    async getAttempts() {
        return api.get('/quiz/attempts/');
    },

    async getAttempt(id) {
        return api.get(`/quiz/attempts/${id}/`);
    }
};

// =============================================================================
// AI Tutor
// =============================================================================

const AITutor = {
    async chat(message, courseId = null, lessonId = null) {
        return api.post('/ai/chat/', {
            message,
            course_id: courseId,
            lesson_id: lessonId
        });
    },

    async getHistory(courseId = null) {
        let endpoint = '/ai/history/';
        if (courseId) endpoint += `?course=${courseId}`;
        return api.get(endpoint);
    },

    async clearHistory(courseId = null) {
        let endpoint = '/ai/history/clear/';
        if (courseId) endpoint += `?course=${courseId}`;
        return api.delete(endpoint);
    }
};

// =============================================================================
// UI Components
// =============================================================================

const UI = {
    showLoader() {
        const loader = document.createElement('div');
        loader.className = 'loader-overlay';
        loader.id = 'global-loader';
        loader.innerHTML = '<div class="loader"></div>';
        document.body.appendChild(loader);
    },

    hideLoader() {
        const loader = document.getElementById('global-loader');
        if (loader) loader.remove();
    },

    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        const container = document.querySelector('.main-body') || document.body;
        container.insertBefore(alert, container.firstChild);
        
        setTimeout(() => alert.remove(), 5000);
    },

    formatDuration(minutes) {
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    },

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    formatPrice(price) {
        if (price === 0 || price === '0.00') return 'Free';
        return `$${parseFloat(price).toFixed(2)}`;
    },

    renderProgressBar(percentage, className = '') {
        return `
            <div class="progress-bar">
                <div class="progress-bar-fill ${className}" style="width: ${percentage}%"></div>
            </div>
        `;
    }
};

// =============================================================================
// Chat Widget
// =============================================================================

class ChatWidget {
    constructor(container, courseId = null, lessonId = null) {
        this.container = container;
        this.courseId = courseId;
        this.lessonId = lessonId;
        this.messages = [];
        this.render();
        this.loadHistory();
    }

    render() {
        this.container.innerHTML = `
            <div class="ai-chat">
                <div class="ai-chat-header">
                    <div class="ai-chat-avatar">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                        </svg>
                    </div>
                    <div>
                        <strong>AI Learning Assistant</strong>
                        <div style="font-size: 0.75rem; opacity: 0.8;">Powered by Claude</div>
                    </div>
                </div>
                <div class="ai-chat-messages" id="chat-messages">
                    <div class="ai-chat-message assistant">
                        Hello! I'm your AI learning assistant. How can I help you today?
                    </div>
                </div>
                <div class="ai-chat-input">
                    <input type="text" id="chat-input" placeholder="Ask a question..." />
                    <button id="chat-send">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        this.messagesContainer = this.container.querySelector('#chat-messages');
        this.input = this.container.querySelector('#chat-input');
        this.sendBtn = this.container.querySelector('#chat-send');

        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    async loadHistory() {
        try {
            const history = await AITutor.getHistory(this.courseId);
            if (history.results && history.results.length > 0) {
                // Clear default message
                this.messagesContainer.innerHTML = '';
                
                // Add history (reversed for chronological order)
                history.results.reverse().forEach(chat => {
                    this.addMessage(chat.message, 'user');
                    this.addMessage(chat.response, 'assistant');
                });
            }
        } catch (e) {
            console.error('Failed to load chat history:', e);
        }
    }

    addMessage(text, role) {
        const msg = document.createElement('div');
        msg.className = `ai-chat-message ${role}`;
        msg.innerHTML = this.formatMessage(text);
        this.messagesContainer.appendChild(msg);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    formatMessage(text) {
        // Basic markdown-like formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        this.input.value = '';
        this.addMessage(message, 'user');

        // Show typing indicator
        const typing = document.createElement('div');
        typing.className = 'ai-chat-message assistant';
        typing.innerHTML = '<div class="loader"></div>';
        this.messagesContainer.appendChild(typing);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;

        try {
            const { response, data } = await AITutor.chat(message, this.courseId, this.lessonId);
            typing.remove();

            if (response.ok) {
                this.addMessage(data.response, 'assistant');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            }
        } catch (e) {
            typing.remove();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    }
}

// =============================================================================
// Page Handlers
// =============================================================================

const Pages = {
    // Login Page
    initLogin() {
        const form = document.getElementById('login-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = form.querySelector('#email').value;
            const password = form.querySelector('#password').value;
            const errorDiv = form.querySelector('.form-error');

            UI.showLoader();
            const result = await Auth.login(email, password);
            UI.hideLoader();

            if (result.success) {
                window.location.href = '/dashboard/';
            } else {
                errorDiv.textContent = result.errors.detail || 'Invalid credentials';
                errorDiv.style.display = 'block';
            }
        });
    },

    // Register Page
    initRegister() {
        const form = document.getElementById('register-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                email: form.querySelector('#email').value,
                password: form.querySelector('#password').value,
                password_confirm: form.querySelector('#password_confirm').value,
                first_name: form.querySelector('#first_name').value,
                last_name: form.querySelector('#last_name').value,
                role: form.querySelector('#role').value
            };
            const errorDiv = form.querySelector('.form-error');

            UI.showLoader();
            const result = await Auth.register(data);
            UI.hideLoader();

            if (result.success) {
                window.location.href = '/dashboard/';
            } else {
                const errors = Object.values(result.errors).flat().join(', ');
                errorDiv.textContent = errors;
                errorDiv.style.display = 'block';
            }
        });
    },

    // Dashboard Page
    async initDashboard() {
        const user = Auth.getUser();
        if (!user) return;

        // Update user info
        const userNameEl = document.getElementById('user-name');
        const userAvatarEl = document.getElementById('user-avatar');
        if (userNameEl) userNameEl.textContent = user.full_name;
        if (userAvatarEl) userAvatarEl.textContent = user.full_name.charAt(0).toUpperCase();

        // Load enrollments
        try {
            const enrollments = await Courses.getMyEnrollments();
            const container = document.getElementById('enrolled-courses');
            if (container && enrollments.results) {
                if (enrollments.results.length === 0) {
                    container.innerHTML = `
                        <div class="card-body text-center">
                            <p class="text-muted">You haven't enrolled in any courses yet.</p>
                            <a href="/courses/" class="btn btn-primary">Browse Courses</a>
                        </div>
                    `;
                } else {
                    container.innerHTML = enrollments.results.map(enrollment => `
                        <div class="card-body" style="border-bottom: 1px solid var(--gray-200);">
                            <div class="d-flex justify-between align-center mb-1">
                                <a href="/courses/${enrollment.course.id}/" class="course-card-title" style="margin:0;">
                                    ${enrollment.course.title}
                                </a>
                                <span class="badge ${enrollment.completed ? 'badge-success' : 'badge-primary'}">
                                    ${enrollment.completed ? 'Completed' : enrollment.progress_percentage + '%'}
                                </span>
                            </div>
                            ${UI.renderProgressBar(enrollment.progress_percentage, enrollment.completed ? 'success' : '')}
                        </div>
                    `).join('');
                }
            }

            // Update stats
            const totalCourses = enrollments.results?.length || 0;
            const completedCourses = enrollments.results?.filter(e => e.completed).length || 0;
            
            const totalEl = document.getElementById('stat-total-courses');
            const completedEl = document.getElementById('stat-completed');
            const inProgressEl = document.getElementById('stat-in-progress');
            const quizzesEl = document.getElementById('stat-quizzes');
            
            if (totalEl) totalEl.textContent = totalCourses;
            if (completedEl) completedEl.textContent = completedCourses;
            if (inProgressEl) inProgressEl.textContent = Math.max(0, totalCourses - completedCourses);

            // Fetch quiz attempts and display count
            try {
                const attempts = await Quiz.getAttempts();
                const attemptsCount = attempts?.results ? attempts.results.length : (Array.isArray(attempts) ? attempts.length : 0);
                if (quizzesEl) quizzesEl.textContent = attemptsCount;
            } catch (e) {
                console.error('Failed to load quiz attempts:', e);
            }

        } catch (e) {
            console.error('Failed to load dashboard:', e);
        }
    },

    // Course List Page
    async initCourseList() {
        const container = document.getElementById('courses-container');
        if (!container) return;

        UI.showLoader();
        try {
            const courses = await Courses.list();
            console.log(courses);
            UI.hideLoader();

            if (courses.results && courses.results.length > 0) {
                container.innerHTML = courses.results.map(course => `
                    <div class="course-card">
                        <div class="course-card-thumbnail">
                            ${course.thumbnail 
                                ? `<img src="${course.thumbnail}" alt="${course.title}">`
                                : `<div style="height:100%;display:flex;align-items:center;justify-content:center;background:var(--primary);">
                                    <svg width="48" height="48" fill="white" viewBox="0 0 24 24">
                                        <path d="M12 3L1 9l11 6 9-4.91V17h2V9M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
                                    </svg>
                                   </div>`
                            }
                            <span class="course-card-badge">${course.level}</span>
                        </div>
                        <div class="course-card-body">
                            <a href="/courses/${course.id}/" class="course-card-title">${course.title}</a>
                            <div class="course-card-meta">
                                <span>👤 ${course.instructor_name}</span>
                                <span>📚 ${course.total_lessons} lessons</span>
                            </div>
                            <div class="d-flex justify-between align-center">
                                <span class="course-card-price ${course.price === '0.00' ? 'free' : ''}">
                                    ${UI.formatPrice(course.price)}
                                </span>
                                ${course.is_enrolled 
                                    ? '<span class="badge badge-success">Enrolled</span>'
                                    : ''
                                }
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p class="text-center text-muted">No courses available yet.</p>';
            }
        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<p class="text-center text-danger">Failed to load courses.</p>';
        }
    },

    // Course Detail Page
    async initCourseDetail(courseId) {
        const container = document.getElementById('course-detail');
        if (!container) return;

        UI.showLoader();
        try {
            const course = await Courses.get(courseId);
            UI.hideLoader();

            document.title = `${course.title} - AI LMS`;

            container.innerHTML = `
                <div class="card mb-3">
                    ${course.thumbnail 
                        ? `<img src="${course.thumbnail}" alt="${course.title}" style="width:100%;height:300px;object-fit:cover;">`
                        : ''
                    }
                    <div class="card-body">
                        <h1>${course.title}</h1>
                        <div class="course-card-meta mb-2">
                            <span class="badge badge-${course.level === 'beginner' ? 'success' : course.level === 'intermediate' ? 'warning' : 'primary'}">
                                ${course.level}
                            </span>
                            <span>👤 ${course.instructor.full_name}</span>
                            <span>📚 ${course.total_lessons} lessons</span>
                            <span>⏱️ ${course.duration_hours} hours</span>
                            <span>👥 ${course.enrolled_count} students</span>
                        </div>
                        <p>${course.description}</p>
                        ${Auth.getUser()?.id === course.instructor.id ? `
                            <div class="mb-3">
                                <a href="/quiz/manage/${courseId}/" class="btn btn-secondary">Manage Quizzes</a>
                            </div>
                        ` : ''}
                        
                        ${course.is_enrolled 
                            ? `<div class="mb-2">
                                <div class="d-flex justify-between mb-1">
                                    <span>Your Progress</span>
                                    <span>${course.progress}%</span>
                                </div>
                                ${UI.renderProgressBar(course.progress)}
                               </div>
                                <a href="/courses/${courseId}/lessons/${course.lessons[0]?.id || ''}/" class="btn btn-primary">
                                   Continue Learning
                               </a>`

                            : `<div class="d-flex align-center gap-2">
                                <span class="course-card-price ${course.price === '0.00' ? 'free' : ''}" style="font-size:1.5rem;">
                                    ${UI.formatPrice(course.price)}
                                </span>
                                <button class="btn btn-primary btn-lg" id="enroll-btn">
                                    Enroll Now
                                </button>
                               </div>`
                        }
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 style="margin:0;">Course Content</h3>
                    </div>
                    <div class="card-body" style="padding:0;">
                        ${course.lessons.map((lesson, index) => `
                            <div style="padding:1rem;border-bottom:1px solid var(--gray-200);display:flex;align-items:center;gap:1rem;">
                                <span style="width:32px;height:32px;border-radius:50%;background:${lesson.is_completed ? 'var(--success)' : 'var(--gray-200)'};display:flex;align-items:center;justify-content:center;color:${lesson.is_completed ? 'white' : 'var(--gray-500)'};">
                                    ${lesson.is_completed ? '✓' : index + 1}
                                </span>
                                <div style="flex:1;">
                                    ${course.is_enrolled || lesson.is_free
                                        ? `<a href="/courses/${courseId}/lessons/${lesson.id}/">${lesson.title}</a>`
                                        : `<span>${lesson.title}</span>`
                                    }
                                    <div style="font-size:0.875rem;color:var(--gray-500);">
                                        ${lesson.content_type} • ${lesson.duration_minutes} min
                                        ${lesson.is_free ? '<span class="badge badge-success">Free Preview</span>' : ''}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;

            // Enroll button handler
            const enrollBtn = document.getElementById('enroll-btn');
            if (enrollBtn) {
                enrollBtn.addEventListener('click', async () => {
                    if (!Auth.isAuthenticated()) {
                        window.location.href = '/auth/login/';
                        return;
                    }

                    UI.showLoader();
                    const { response, data } = await Courses.enroll(courseId);
                    UI.hideLoader();

                    if (response.ok) {
                        UI.showAlert('Successfully enrolled!', 'success');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        UI.showAlert(data.error || 'Failed to enroll', 'danger');
                    }
                });
            }

        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<p class="text-center text-danger">Failed to load course.</p>';
        }
    },

    // Quiz Management Pages
    async initQuizManage(courseId) {
        const container = document.getElementById('manage-quiz-container');
        if (!container) return;

        UI.showLoader();
        try {
            const [course, quizzes] = await Promise.all([
                Courses.get(courseId),
                Quiz.list(courseId)
            ]);
            UI.hideLoader();

            document.getElementById('course-title').textContent = course.title;

            if (quizzes.results && quizzes.results.length > 0) {
                container.innerHTML = `
                    <div class="table-container card">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Questions</th>
                                    <th>Attempts</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${quizzes.results.map(quiz => `
                                    <tr>
                                        <td>${quiz.title}</td>
                                        <td>${quiz.question_count}</td>
                                        <td>${quiz.user_attempts}</td>
                                        <td>
                                            <span class="badge badge-${quiz.is_published ? 'success' : 'warning'}">
                                                ${quiz.is_published ? 'Published' : 'Draft'}
                                            </span>
                                        </td>
                                        <td>
                                            <a href="/quiz/${quiz.id}/questions/" class="btn btn-sm btn-secondary">Manage Questions</a>
                                            <button
                                             class="btn btn-sm btn-danger ms-2"
                                             onclick="deleteQuiz(${quiz.id})">
                                               Delete
                                            </button>
                                        </td>
                                            
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="card">
                        <div class="card-body text-center">
                            <p class="text-muted">No quizzes created yet for this course.</p>
                            <a href="/quiz/create/${courseId}/" class="btn btn-primary">Create Quiz</a>
                        </div>
                    </div>
                `;
            }
        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<div class="alert alert-danger">Unable to load quizzes. Please try again.</div>';
        }
    },

    async initQuizCreate(courseId) {
        const container = document.getElementById('quiz-create-container');
        if (!container) return;

        UI.showLoader();
        try {
            const course = await Courses.get(courseId);
            UI.hideLoader();

            document.getElementById('course-title').textContent = course.title;
            const lessonsSelect = document.getElementById('lesson-select');
            lessonsSelect.innerHTML = `
                <option value="">No lesson association</option>
                ${course.lessons.map(lesson => `
                    <option value="${lesson.id}">${lesson.title}</option>
                `).join('')}
            `;

            const form = document.getElementById('create-quiz-form');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = {
                    course_id: courseId,
                    title: form.querySelector('[name="title"]').value,
                    description: form.querySelector('[name="description"]').value,
                    lesson: form.querySelector('[name="lesson"]').value || null,
                    pass_score: parseInt(form.querySelector('[name="pass_score"]').value, 10) || 70,
                    time_limit_minutes: parseInt(form.querySelector('[name="time_limit_minutes"]').value, 10) || 0,
                    max_attempts: parseInt(form.querySelector('[name="max_attempts"]').value, 10) || 0,
                    shuffle_questions: form.querySelector('[name="shuffle_questions"]').checked,
                    show_correct_answers: form.querySelector('[name="show_correct_answers"]').checked,
                    is_published: form.querySelector('[name="is_published"]').checked,
                };

                UI.showLoader();
                const { response, data: result } = await Quiz.create(data);
                console.log(result);
                UI.hideLoader();

                if (response.ok) {
                    console.log('Result=', result);
                    //alert(JSON.stringify(result));
                    UI.showAlert('Quiz created successfully.', 'success');
                    setTimeout(() => {
                        window.location.href = `/quiz/${result.id}/questions/`;
                    }, 400);
                } else {
                    UI.showAlert(result.error || 'Unable to create quiz.', 'danger');
                }
            });
        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<div class="alert alert-danger">Unable to load course information.</div>';
        }
    },

    async initQuizQuestions(quizId) {
        const container = document.getElementById('quiz-questions-container');
        if (!container) return;

        UI.showLoader();
        try {
            const quiz = await Quiz.get(quizId);
            UI.hideLoader();

            document.getElementById('quiz-title').textContent = quiz.title;
            const backLink = document.getElementById('back-to-manage');
            if (backLink) {
                backLink.href = `/quiz/manage/${quiz.course_id}/`;
            }

            const renderQuestions = (questions) => {
                const list = document.getElementById('question-list');
                if (!list) return;

                if (!questions || questions.length === 0) {
                    list.innerHTML = '<div class="text-center text-muted">No questions added yet.</div>';
                    return;
                }

                list.innerHTML = questions.map(question => `
                    <div class="card mb-3">
                        <div class="card-body">
                            <div class="d-flex justify-between align-center mb-2">
                                <strong>${question.text}</strong>
                                <span class="badge badge-${question.question_type === 'single' ? 'primary' : question.question_type === 'multiple' ? 'warning' : 'success'}">
                                    ${question.question_type.replace('_', ' ')}
                                </span>
                            </div>
                            <div class="text-muted mb-2">Points: ${question.points}</div>
                            <ul class="list-group">
                                ${question.choices.map(choice => `
                                    <li class="list-group-item ${choice.is_correct ? 'list-group-item-success' : ''}">
                                        ${choice.text} ${choice.is_correct ? '<strong>(Correct)</strong>' : ''}
                                    </li>
                                `).join('')}
                            </ul>
                            ${question.explanation ? `<div class="mt-2 text-muted">Explanation: ${question.explanation}</div>` : ''}
                        </div>
                    </div>
                `).join('');
            };

            renderQuestions(quiz.questions);

            const form = document.getElementById('add-question-form');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const text = form.querySelector('[name="text"]').value.trim();
                const questionType = form.querySelector('[name="question_type"]').value;
                const points = parseInt(form.querySelector('[name="points"]').value, 10) || 1;
                const explanation = form.querySelector('[name="explanation"]').value.trim();
                const choices = [1, 2, 3, 4].map(i => ({
                    text: form.querySelector(`[name="choice_${i}"]`).value.trim(),
                    is_correct: form.querySelector(`[name="correct_${i}"]`).checked,
                    order: i - 1
                })).filter(c => c.text.length > 0);

                if (!text || choices.length === 0) {
                    UI.showAlert('Please add a question text and at least one answer choice.', 'danger');
                    return;
                }

                const payload = {
                    text,
                    question_type: questionType,
                    explanation,
                    points,
                    order: quiz.questions.length,
                    choices
                };

                UI.showLoader();
                const { response, data: result } = await Quiz.createQuestion(quizId, payload);
                UI.hideLoader();

                if (response.ok) {
                    quiz.questions.push(result.question);
                    renderQuestions(quiz.questions);
                    form.reset();
                    UI.showAlert('Question added successfully.', 'success');
                } else {
                    UI.showAlert(result.error || 'Unable to add question.', 'danger');
                }
            });
        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<div class="alert alert-danger">Unable to load quiz details.</div>';
        }
    },

    // Lesson Page
    async initLesson(courseId, lessonId) {
        const container = document.getElementById('lesson-content');
        const chatContainer = document.getElementById('ai-chat-container');
        if (!container) return;

        UI.showLoader();
        try {
            const lesson = await Courses.getLesson(lessonId);
            UI.hideLoader();

            document.title = `${lesson.title} - AI LMS`;

            container.innerHTML = `
                ${lesson.video_url 
                    ? `<div class="lesson-video">
                        <iframe src="${lesson.video_url}" frameborder="0" allowfullscreen></iframe>
                       </div>`
                    : ''
                }
                <h1>${lesson.title}</h1>
                <div class="lesson-text">${lesson.content}</div>
                
                <div class="d-flex justify-between mt-3">
                    ${lesson.prev_lesson 
                        ? `<a href="/courses/${courseId}/lessons/${lesson.prev_lesson.id}/" class="btn btn-secondary">
                            ← ${lesson.prev_lesson.title}
                           </a>`
                        : '<div></div>'
                    }
                    <button class="btn btn-success" id="complete-btn">
                        Mark as Complete ✓
                    </button>
                    ${lesson.quiz_id
                        ? `<button class="btn btn-primary ms-2" onclick="window.location.href='/quiz/${lesson.quiz_id}/'">Take Quiz</button>`
                        : `<button class="btn btn-primary ms-2" disabled>No Quiz</button>`
                    }
                    ${lesson.next_lesson 
                        ? `<a href="/courses/${courseId}/lessons/${lesson.next_lesson.id}/" class="btn btn-primary">
                            ${lesson.next_lesson.title} →
                           </a>`
                        : '<div></div>'
                    }
                </div>
            `;

            // Complete button handler
            const completeBtn = document.getElementById('complete-btn');
            if (completeBtn) {
                completeBtn.addEventListener('click', async () => {
                    const { response, data } = await Courses.completeLesson(lessonId);
                    if (response.ok) {
                        completeBtn.textContent = 'Completed ✓';
                        completeBtn.disabled = true;
                        UI.showAlert('Lesson completed!', 'success');
                    }
                });
            }

            // Initialize AI Chat
            if (chatContainer) {
                new ChatWidget(chatContainer, courseId, lessonId);
            }

        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<p class="text-center text-danger">Failed to load lesson.</p>';
        }
    },

    // Quiz Page
    async initQuiz(quizId) {
        const container = document.getElementById('quiz-container');
        if (!container) return;

        UI.showLoader();
        try {
            const { response, data } = await Quiz.start(quizId);
            UI.hideLoader();

            if (!response.ok) {
                container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }

            const quiz = data.quiz;
            const attempt = data.attempt;
            let answers = {};
            let timeLeft = quiz.time_limit_minutes * 60;

            container.innerHTML = `
                <div class="quiz-header">
                    <h2>${quiz.title}</h2>
                    ${quiz.time_limit_minutes > 0 
                        ? `<div class="quiz-timer" id="quiz-timer">${Math.floor(timeLeft/60)}:${String(timeLeft%60).padStart(2,'0')}</div>`
                        : ''
                    }
                </div>
                <div id="quiz-questions">
                    ${quiz.questions.map((q, i) => `
                        <div class="quiz-question" data-question="${q.id}">
                            <div class="quiz-question-text">${i + 1}. ${q.text}</div>
                            <div class="quiz-choices">
                                ${q.choices.map(c => `
                                    <div class="quiz-choice" data-choice="${c.id}">
                                        ${c.text}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary btn-lg btn-block" id="submit-quiz">
                        Submit Quiz
                    </button>
                </div>
            `;

            // Timer
            if (quiz.time_limit_minutes > 0) {
                const timerEl = document.getElementById('quiz-timer');
                const timerInterval = setInterval(() => {
                    timeLeft--;
                    timerEl.textContent = `${Math.floor(timeLeft/60)}:${String(timeLeft%60).padStart(2,'0')}`;
                    if (timeLeft <= 0) {
                        clearInterval(timerInterval);
                        document.getElementById('submit-quiz').click();
                    }
                }, 1000);
            }

            // Choice selection
            container.querySelectorAll('.quiz-choice').forEach(choice => {
                choice.addEventListener('click', () => {
                    const question = choice.closest('.quiz-question');
                    const questionId = question.dataset.question;
                    const choiceId = choice.dataset.choice;

                    // Single choice - deselect others
                    question.querySelectorAll('.quiz-choice').forEach(c => c.classList.remove('selected'));
                    choice.classList.add('selected');
                    answers[questionId] = [parseInt(choiceId)];
                });
            });

            // Submit
            document.getElementById('submit-quiz').addEventListener('click', async () => {
                const formattedAnswers = Object.entries(answers).map(([qId, cIds]) => ({
                    question_id: parseInt(qId),
                    choice_ids: cIds
                }));

                UI.showLoader();
                const { response: submitResponse, data: result } = await Quiz.submit(quizId, formattedAnswers);
                UI.hideLoader();

                if (submitResponse.ok) {
                    window.location.href = `/quiz/result/${result.result.id}/`;
                } else {
                    UI.showAlert(result.error || 'Failed to submit quiz', 'danger');
                }
            });

        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<p class="text-center text-danger">Failed to load quiz.</p>';
        }
    },

    // Quiz Result Page
    async initQuizResult(attemptId) {
        const container = document.getElementById('result-container');
        if (!container) return;

        UI.showLoader();
        try {
            const result = await Quiz.getAttempt(attemptId);
            UI.hideLoader();

            container.innerHTML = `
                <div class="card mb-3">
                    <div class="card-body text-center">
                        <h2>${result.quiz.title}</h2>
                        <div style="font-size:4rem;font-weight:700;color:${result.passed ? 'var(--success)' : 'var(--danger)'};">
                            ${Math.round(result.score)}%
                        </div>
                        <p class="text-muted">
                            ${result.earned_points} / ${result.total_points} points
                        </p>
                        <span class="badge ${result.passed ? 'badge-success' : 'badge-warning'}" style="font-size:1rem;padding:0.5rem 1rem;">
                            ${result.passed ? '✓ Passed' : '✗ Not Passed'}
                        </span>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 style="margin:0;">Review Answers</h3>
                    </div>
                    <div class="card-body" style="padding:0;">
                        ${result.answers.map((answer, i) => `
                            <div style="padding:1rem;border-bottom:1px solid var(--gray-200);">
                                <div class="quiz-question-text">
                                    ${i + 1}. ${answer.question.text}
                                    ${answer.is_correct 
                                        ? '<span class="badge badge-success">Correct</span>'
                                        : '<span class="badge badge-warning">Incorrect</span>'
                                    }
                                </div>
                                <div class="quiz-choices">
                                    ${answer.question.choices.map(c => {
                                        const selected = answer.selected_choices.some(sc => sc.id === c.id);
                                        let className = '';
                                        if (c.is_correct) className = 'correct';
                                        else if (selected && !c.is_correct) className = 'incorrect';
                                        return `<div class="quiz-choice ${className}" style="cursor:default;">
                                            ${selected ? '→ ' : ''}${c.text}
                                        </div>`;
                                    }).join('')}
                                </div>
                                ${answer.question.explanation 
                                    ? `<div class="mt-1" style="color:var(--gray-600);font-style:italic;">
                                        💡 ${answer.question.explanation}
                                       </div>`
                                    : ''
                                }
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="mt-3 text-center">
                    <a href="/dashboard/" class="btn btn-primary">Back to Dashboard</a>
                </div>
            `;

        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<p class="text-center text-danger">Failed to load result.</p>';
        }
    },

    // Progress Page
    async initProgress() {
        const container = document.getElementById('progress-container');
        if (!container) return;

        UI.showLoader();
        try {
            const progress = await Courses.getAllProgress();
            UI.hideLoader();

            if (progress.length === 0) {
                container.innerHTML = `
                    <div class="card-body text-center">
                        <p class="text-muted">No progress to show. Start learning!</p>
                        <a href="/courses/" class="btn btn-primary">Browse Courses</a>
                    </div>
                `;
                return;
            }

            container.innerHTML = progress.map(course => `
                <div class="card mb-2">
                    <div class="card-body">
                        <div class="d-flex justify-between align-center mb-1">
                            <h4 style="margin:0;">
                                <a href="/courses/${course.course_id}/">${course.course_title}</a>
                            </h4>
                            <span class="badge ${course.completed ? 'badge-success' : 'badge-primary'}">
                                ${course.completed ? 'Completed' : `${course.progress_percentage}%`}
                            </span>
                        </div>
                        <div class="d-flex justify-between text-muted mb-1" style="font-size:0.875rem;">
                            <span>${course.completed_lessons} / ${course.total_lessons} lessons completed</span>
                            <span>Enrolled ${UI.formatDate(course.enrolled_at)}</span>
                        </div>
                        ${UI.renderProgressBar(course.progress_percentage, course.completed ? 'success' : '')}
                    </div>
                </div>
            `).join('');

        } catch (e) {
            UI.hideLoader();
            container.innerHTML = '<p class="text-center text-danger">Failed to load progress.</p>';
        }
    }
};

// =============================================================================
// Sidebar Toggle (Mobile)
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.querySelector('.mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });
});
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
async function deleteQuiz(quizId) {
    if (!confirm('Delete this quiz?')) return;

    try {
        const response = await fetch(`/api/v1/quiz/${quizId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        console.log('Status:', response.status);
        console.log( await response.text());

        if (response.ok) {
            alert('Quiz deleted successfully');
            location.reload()
        } else {
            alert('Failed: ' + response.status);
        }
    } catch (error) {
        console.error(error);
    }
}

// Export for use in templates
window.API = api;
window.Auth = Auth;
window.Courses = Courses;
window.Quiz = Quiz;
window.AITutor = AITutor;
window.UI = UI;
window.Pages = Pages;
window.ChatWidget = ChatWidget;
