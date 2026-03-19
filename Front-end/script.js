// Configuration
const API_URL = "http://localhost:8000";
let currentQuestionId = null;
let currentStudent = Math.floor(Math.random() * 10000) + 1;
let selectedOption = null;

// DOM Elements
const elements = {
    // Status
    backendStatus: document.getElementById('backendStatus'),
    
    // Generate section
    generateForm: document.getElementById('generateForm'),
    generateBtn: document.getElementById('generateBtn'),
    generateError: document.getElementById('generateError'),
    questionContainer: document.getElementById('questionContainer'),
    questionText: document.getElementById('questionText'),
    optionsList: document.getElementById('optionsList'),
    questionId: document.getElementById('questionId'),
    
    // Submit section
    submitForm: document.getElementById('submitForm'),
    submitBtn: document.getElementById('submitBtn'),
    submitError: document.getElementById('submitError'),
    answer: document.getElementById('answer'),
    feedbackContainer: document.getElementById('feedbackContainer'),
    resultStatus: document.getElementById('resultStatus'),
    aiFeedback: document.getElementById('aiFeedback'),
    correctAnswerDisplay: document.getElementById('correctAnswerDisplay'),
    nextDifficultyDisplay: document.getElementById('nextDifficultyDisplay'),
    nextQuestionBtn: document.getElementById('nextQuestionBtn'),
    
    // Analytics section
    analyticsBtn: document.getElementById('analyticsBtn'),
    analyticsError: document.getElementById('analyticsError'),
    analyticsContainer: document.getElementById('analyticsContainer'),
    noStudentsMessage: document.getElementById('noStudentsMessage'),
    studentsTableBody: document.getElementById('studentsTableBody')
};

// ==================== UTILITY FUNCTIONS ====================

function setLoading(button, isLoading, originalText = '') {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span> Loading...';
    } else {
        button.disabled = false;
        button.textContent = originalText;
    }
}

function showError(element, message) {
    element.textContent = `❌ ${message}`;
    element.classList.remove('hidden');
}

function hideError(element) {
    element.classList.add('hidden');
}

// ==================== BACKEND STATUS ====================

async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_URL}/health`, {
            mode: 'cors',
            headers: { 'Accept': 'application/json' }
        });
        
        if (response.ok) {
            elements.backendStatus.textContent = '● Online';
            elements.backendStatus.className = 'status-indicator online';
        } else {
            throw new Error('Backend error');
        }
    } catch (error) {
        elements.backendStatus.textContent = '● Offline';
        elements.backendStatus.className = 'status-indicator offline';
        console.error('Backend connection failed:', error);
    }
}

// ==================== GENERATE QUESTION ====================

async function handleGenerateSubmit(e) {
    e.preventDefault();
    
    const topic = document.getElementById('topic').value.trim();
    const difficulty = document.getElementById('difficulty').value;
    
    if (!topic) {
        showError(elements.generateError, 'Please enter a topic');
        return;
    }
    
    setLoading(elements.generateBtn, true, 'Generate Question');
    hideError(elements.generateError);
    
    try {
        const response = await fetch(
            `${API_URL}/generate-question?topic=${encodeURIComponent(topic)}&difficulty=${difficulty}`,
            {
                mode: 'cors',
                headers: { 'Accept': 'application/json' }
            }
        );
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.error || 'Failed to generate question');
        }
        
        currentQuestionId = data.question_id;
        displayQuestion(data);
        
        // Reset answer section
        elements.answer.value = '';
        elements.feedbackContainer.classList.add('hidden');
        selectedOption = null;
        
    } catch (error) {
        console.error('Generate error:', error);
        showError(elements.generateError, error.message);
        elements.questionContainer.classList.add('hidden');
    } finally {
        setLoading(elements.generateBtn, false, 'Generate Question');
    }
}

function displayQuestion(data) {
    elements.questionText.textContent = data.question;
    elements.questionId.textContent = `Question ID: ${data.question_id}`;
    
    // Clear and populate options
    elements.optionsList.innerHTML = '';
    
    ['A', 'B', 'C', 'D'].forEach(letter => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option-item';
        optionDiv.setAttribute('data-option', letter);
        optionDiv.textContent = `${letter}: ${data.options[letter]}`;
        
        optionDiv.addEventListener('click', () => {
            // Remove selected class from all options
            document.querySelectorAll('.option-item').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Add selected class to clicked option
            optionDiv.classList.add('selected');
            elements.answer.value = letter;
            selectedOption = letter;
        });
        
        elements.optionsList.appendChild(optionDiv);
    });
    
    elements.questionContainer.classList.remove('hidden');
    
    // Scroll to question
    elements.questionContainer.scrollIntoView({ behavior: 'smooth' });
}

// ==================== SUBMIT ANSWER ====================

async function handleSubmitAnswer(e) {
    e.preventDefault();
    
    if (!currentQuestionId) {
        showError(elements.submitError, 'Please generate a question first');
        return;
    }
    
    const answer = elements.answer.value.trim().toUpperCase();
    
    if (!answer || !['A', 'B', 'C', 'D'].includes(answer)) {
        showError(elements.submitError, 'Please enter A, B, C, or D');
        return;
    }
    
    setLoading(elements.submitBtn, true, 'Submit Answer');
    hideError(elements.submitError);
    
    try {
        const payload = {
            student_id: currentStudent,
            question_id: currentQuestionId,
            student_answer: answer
        };
        
        console.log('Submitting:', payload);
        
        const response = await fetch(`${API_URL}/submit-answer`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        console.log('Response:', data);
        
        if (!response.ok) {
            throw new Error(data.detail || data.error || 'Submission failed');
        }
        
        displayFeedback(data);
        
    } catch (error) {
        console.error('Submit error:', error);
        showError(elements.submitError, error.message);
        elements.feedbackContainer.classList.add('hidden');
    } finally {
        setLoading(elements.submitBtn, false, 'Submit Answer');
    }
}

function displayFeedback(data) {
    const isCorrect = data.status === 'Correct';
    
    // Set status
    elements.resultStatus.textContent = isCorrect ? '✅ Correct!' : '❌ Incorrect';
    elements.resultStatus.className = isCorrect ? 'result-status correct' : 'result-status incorrect';
    
    // Set feedback content
    elements.aiFeedback.textContent = data.ai_feedback || 'No AI feedback available';
    elements.correctAnswerDisplay.textContent = data.correct_answer;
    
    // Format next difficulty with emoji
    let difficultyEmoji = '🟢';
    if (data.next_difficulty === 'intermediate') difficultyEmoji = '🟡';
    if (data.next_difficulty === 'advanced') difficultyEmoji = '🔴';
    
    elements.nextDifficultyDisplay.innerHTML = `${difficultyEmoji} ${data.next_difficulty.charAt(0).toUpperCase() + data.next_difficulty.slice(1)}`;
    
    // Update difficulty dropdown
    document.getElementById('difficulty').value = data.next_difficulty;
    
    elements.feedbackContainer.classList.remove('hidden');
    
    // Scroll to feedback
    elements.feedbackContainer.scrollIntoView({ behavior: 'smooth' });
}

// ==================== ANALYTICS ====================

async function handleAnalytics() {
    setLoading(elements.analyticsBtn, true, 'Load Struggling Students');
    hideError(elements.analyticsError);
    
    try {
        const response = await fetch(`${API_URL}/analytics/struggling-students`, {
            mode: 'cors',
            headers: { 'Accept': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch analytics');
        }
        
        const students = await response.json();
        console.log('Analytics:', students);
        
        if (students.length === 0) {
            elements.noStudentsMessage.classList.remove('hidden');
            elements.studentsTableBody.innerHTML = '';
        } else {
            elements.noStudentsMessage.classList.add('hidden');
            
            // Populate table
            elements.studentsTableBody.innerHTML = '';
            students.forEach(student => {
                const scoreValue = parseFloat(student.score);
                const scoreClass = scoreValue < 50 ? 'score-low' : 'score-medium';
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${student.name}</td>
                    <td class="${scoreClass}">${student.score}</td>
                `;
                elements.studentsTableBody.appendChild(row);
            });
        }
        
        elements.analyticsContainer.classList.remove('hidden');
        
    } catch (error) {
        console.error('Analytics error:', error);
        showError(elements.analyticsError, error.message);
        elements.analyticsContainer.classList.add('hidden');
    } finally {
        setLoading(elements.analyticsBtn, false, 'Load Struggling Students');
    }
}

// ==================== RESET ====================

function resetForNextQuestion() {
    elements.questionContainer.classList.add('hidden');
    elements.feedbackContainer.classList.add('hidden');
    elements.answer.value = '';
    currentQuestionId = null;
    selectedOption = null;
    
    // Clear option selections
    document.querySelectorAll('.option-item').forEach(opt => {
        opt.classList.remove('selected');
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    // Generate question
    elements.generateForm.addEventListener('submit', handleGenerateSubmit);
    
    // Submit answer
    elements.submitForm.addEventListener('submit', handleSubmitAnswer);
    
    // Analytics
    elements.analyticsBtn.addEventListener('click', handleAnalytics);
    
    // Next question button
    elements.nextQuestionBtn.addEventListener('click', resetForNextQuestion);
    
    // Auto-uppercase answer input
    elements.answer.addEventListener('input', (e) => {
        e.target.value = e.target.value.toUpperCase().replace(/[^A-D]/g, '');
    });
    
    // Enter key in answer input triggers submit
    elements.answer.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSubmitAnswer(e);
        }
    });
}

// ==================== INITIALIZATION ====================

function init() {
    console.log('AI Tutor Frontend Initialized');
    console.log('Student ID:', currentStudent);
    
    // Check backend status immediately
    checkBackendStatus();
    
    // Set up periodic status check
    setInterval(checkBackendStatus, 10000);
    
    // Set up event listeners
    setupEventListeners();
}

// Start everything when DOM is ready
document.addEventListener('DOMContentLoaded', init);