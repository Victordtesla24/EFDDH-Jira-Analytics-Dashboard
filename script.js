$(document).ready(function() {
    const progressSteps = [
        { step: 1, message: "Uploading resume...", progress: 20 },
        { step: 2, message: "Analyzing content...", progress: 40 },
        { step: 3, message: "Comparing with job description...", progress: 60 },
        { step: 4, message: "Optimizing resume...", progress: 80 },
        { step: 5, message: "Finalizing...", progress: 100 }
    ];

    // Add error logging system
    const errorLog = {
        errors: [],
        add: function(error, type = 'error') {
            const errorObj = {
                id: Date.now(),
                message: error,
                type: type,
                timestamp: new Date().toLocaleTimeString()
            };
            this.errors.push(errorObj);
            this.display(errorObj);
        },
        display: function(errorObj) {
            const errorHtml = `
                <div class="alert alert-${errorObj.type === 'error' ? 'danger' : 'warning'} alert-dismissible fade show" role="alert" id="error-${errorObj.id}">
                    <strong>${errorObj.timestamp}</strong>: ${errorObj.message}
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
            `;
            $('#globalErrorLogger').append(errorHtml);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                $(`#error-${errorObj.id}`).alert('close');
            }, 5000);
        },
        clear: function() {
            this.errors = [];
            $('#globalErrorLogger').empty();
        }
    };

    const debugLog = {
        logs: [],
        add: function(message, type = 'debug') {
            const logEntry = {
                timestamp: new Date().toISOString(),
                message: message,
                type: type
            };
            this.logs.push(logEntry);
            this.display(logEntry);
        },
        display: function(logEntry) {
            const logHtml = `
                <div class="debug-log ${logEntry.type}">
                    <span class="timestamp">${new Date(logEntry.timestamp).toLocaleTimeString()}</span>
                    <span class="message">${logEntry.message}</span>
                </div>
            `;
            $('#debugOutput').append(logHtml);
            $('#debugOutput').scrollTop($('#debugOutput')[0].scrollHeight);
        },
        clear: function() {
            this.logs = [];
            $('#debugOutput').empty();
        }
    };

    function updateProgress(step) {
        if (step < 1 || step > progressSteps.length) return;
        const stepInfo = progressSteps[step - 1];
        $('#optimizationProgress')
            .css('width', `${stepInfo.progress}%`)
            .attr('aria-valuenow', stepInfo.progress);
        $('#statusMessage').text(stepInfo.message);
    }

    // Update error handling
    function showError(message) {
        errorLog.add(message);
        $('#progressContainer').hide();
    }

    function displayOptimizationInsights(response) {
        const analysis = response.analysis;
        $('#optimizationInsights').show();
        
        // Display match score
        $('#matchScore').html(`
            <h6>Match Score</h6>
            <div class="progress">
                <div class="progress-bar bg-${getScoreColor(analysis.match_score)}" 
                     role="progressbar" 
                     style="width: ${analysis.match_score}%">
                    ${Math.round(analysis.match_score)}%
                </div>
            </div>
        `);

        // Display keyword matches
        $('#keywordMatches').html(`
            <h6>Matching Keywords</h6>
            <div class="keyword-chips">
                ${analysis.matching_skills.map(skill => 
                    `<span class="badge badge-success mr-2 mb-2">${skill}</span>`
                ).join('')}
            </div>
        `);

        // Display skills gap
        $('#skillsGap').html(`
            <h6>Missing Skills</h6>
            <div class="keyword-chips">
                ${analysis.missing_skills.map(skill => 
                    `<span class="badge badge-warning mr-2 mb-2">${skill}</span>`
                ).join('')}
            </div>
        `);

        // Display improvements
        $('#improvements').html(`
            <h6>Suggested Improvements</h6>
            <ul class="list-group">
                ${analysis.improvement_suggestions.map(suggestion => 
                    `<li class="list-group-item">${suggestion}</li>`
                ).join('')}
            </ul>
        `);

        // Display optimized resume
        if (response.optimized_resume) {
            $('#results .card').show();
            $('#optimizedContent').html(`<pre class="resume-content">${response.optimized_resume}</pre>`);
        }
    }

    function getScoreColor(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    function updateProgressBar(currentStep, totalSteps) {
        const progress = (currentStep / totalSteps) * 100;
        $('#optimizationProgress')
            .css('width', `${progress}%`)
            .attr('aria-valuenow', progress);
    }

    // Update form submission
    $('#resumeForm').on('submit', function(event) {
        event.preventDefault();
        
        // Reset everything
        errorLog.clear();
        debugLog.clear();
        
        debugLog.add('Starting resume optimization process');
        
        const file = $('#resume')[0].files[0];
        if (!file) {
            debugLog.add('No file selected', 'error');
            showError('Please select a PDF file');
            return;
        }
        
        debugLog.add(`File selected: ${file.name} (${file.type})`);
        
        if (file.type !== 'application/pdf') {
            debugLog.add('Invalid file type', 'error');
            showError('Only PDF files are accepted');
            return;
        }
        
        const formData = new FormData(this);
        
        // Start progress at upload
        updateProgress(1);
        
        $.ajax({
            url: '/optimize_resume',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            xhr: function() {
                const xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        const percent = (e.loaded / e.total) * 100;
                        debugLog.add(`Upload progress: ${Math.round(percent)}%`);
                        $('#optimizationProgress').css('width', percent + '%');
                    }
                });
                return xhr;
            },
            success: function(response) {
                if (response.debug_info) {
                    response.debug_info.forEach(info => {
                        debugLog.add(info.message, 'server');
                    });
                }
                
                if (response.error) {
                    debugLog.add(`Error: ${response.error}`, 'error');
                    showError(response.error);
                    return;
                }
                
                // Process steps sequentially
                let stepIndex = 0;
                const processStep = () => {
                    if (stepIndex < response.steps.length) {
                        const step = response.steps[stepIndex];
                        updateProgress(step.step);
                        $('#statusMessage').text(step.message);
                        stepIndex++;
                        setTimeout(processStep, 1000);
                    } else {
                        // Show results
                        if (response.analysis && response.optimized_resume) {
                            displayOptimizationInsights(response);
                        }
                    }
                };
                
                processStep();
            },
            error: function(xhr, status, error) {
                const errorMessage = xhr.responseJSON?.error || error;
                debugLog.add(`Ajax error: ${errorMessage}`, 'error');
                showError(`Error: ${errorMessage}`);
                $('#progressContainer').hide();
            },
            complete: function() {
                $('#spinner').hide();
            }
        });
    });

    // Add download handler
    $('#downloadBtn').on('click', function() {
        window.location.href = '/download_resume';
    });
});
