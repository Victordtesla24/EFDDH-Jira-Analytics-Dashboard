document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('resumeForm');
    const results = document.getElementById('results');
    const analysisResults = document.getElementById('analysisResults');
    const downloadBtn = document.getElementById('downloadBtn');
    const optimizationSteps = document.getElementById('optimizationSteps');
    const steps = document.getElementById('steps');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';

        const formData = new FormData(form);
        const resumeFile = document.getElementById('resumeFile').files[0];
        const jobDescription = document.getElementById('jobDescription').value;

        formData.append('resume', resumeFile);
        formData.append('job_description', jobDescription);

        try {
            const response = await fetch('/optimize_resume', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                displayResults(data);
                displayOptimizationSteps(data.optimization_steps);
                results.style.display = 'block';
                optimizationSteps.style.display = 'block';
            } else {
                alert(data.error || 'An error occurred');
            }
        } catch (error) {
            alert('An error occurred while processing your request');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Optimize Resume';
        }
    });

    function displayResults(data) {
        const analysis = data.analysis;
        const score = Math.round(analysis.match_score);
        
        analysisResults.innerHTML = `
            <div class="analysis-item">
                <h4>Match Score</h4>
                <span class="score-badge bg-${getScoreColor(score)}">${score}%</span>
            </div>
            <div class="analysis-item">
                <h4>Matching Skills</h4>
                <p>${analysis.matching_skills.join(', ') || 'None found'}</p>
            </div>
            <div class="analysis-item">
                <h4>Suggested Improvements</h4>
                <ul>
                    ${analysis.improvement_suggestions.map(sugg => `<li>${sugg}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    function displayOptimizationSteps(stepsData) {
        steps.innerHTML = stepsData.map(step => `<div class="step-item">${step}</div>`).join('');
    }

    function getScoreColor(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    downloadBtn.addEventListener('click', function() {
        window.location.href = '/download_resume';
    });

    const ws = new WebSocket('ws://localhost:8000/ws');
    const messages = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');

    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        addMessage(message.text, message.type);
    };

    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        messageDiv.textContent = text;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    sendButton.onclick = function() {
        const text = messageInput.value;
        if (text) {
            ws.send(JSON.stringify({text: text}));
            addMessage(text, 'user');
            messageInput.value = '';
        }
    };
});