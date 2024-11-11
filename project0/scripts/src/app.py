from flask import Flask, request, jsonify, render_template, send_file
from resume_optimiser import ResumeOptimizer
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
Bootstrap5(app)

# Initialize ResumeOptimizer with API key from environment
optimizer = ResumeOptimizer(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize_resume', methods=['POST'])
def optimize_resume():
    resume_file = request.files.get('resume')
    job_description = request.form.get('job_description')
    
    if not resume_file or not job_description:
        return jsonify({'error': 'Resume and job description are required.'}), 400
    
    # Read resume content
    resume_text = resume_file.read().decode('utf-8')
    
    # Set resume and job description
    optimizer.original_resume = resume_text
    optimizer.job_description = job_description
    
    # Analyze relevance
    analysis = optimizer.analyze_relevance()
    if not analysis:
        return jsonify({'error': 'Failed to analyze resume.'}), 500
    
    # Optimize resume
    optimized_resume = optimizer.optimize_resume(analysis)
    if not optimized_resume:
        return jsonify({'error': 'Failed to optimize resume.'}), 500
    
    return jsonify({'optimized_resume': optimized_resume}), 200

@app.route('/download_resume')
def download_resume():
    try:
        return send_file(
            'optimized_resumes/latest.docx',
            as_attachment=True,
            download_name='optimized_resume.docx'
        )
    except Exception as e:
        return jsonify({'error': 'Failed to download resume'}), 500

if __name__ == '__main__':
    app.run(debug=True)