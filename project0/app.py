import sys
import os
from flask import Flask, request, jsonify, render_template, send_file
from flask_bootstrap import Bootstrap  # Update this import
from dotenv import load_dotenv
import secrets
from datetime import datetime
import logging
import traceback

# Add the scripts/src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts', 'src'))

try:
    from PyPDF2 import PdfReader
except ImportError:
    logging.error("PyPDF2 not installed. Please install it using: pip install PyPDF2")
    raise

from resume_optimiser import ResumeOptimizer

# Load environment variables from the correct path
load_dotenv()

app = Flask(__name__)

# Set up secret key with fallback
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)

if not app.config['SECRET_KEY']:
    app.logger.warning("No FLASK_SECRET_KEY set, using random key")

Bootstrap(app)  # Update this initialization

# Initialize ResumeOptimizer with API key from environment
optimizer = ResumeOptimizer(api_key=os.getenv('OPENAI_API_KEY'))

# Add debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize_resume', methods=['POST'])
def optimize_resume():
    try:
        logger.debug("Starting resume optimization process")
        response_data = {
            'success': False,
            'current_step': 0,
            'steps': [],
            'error': None,
            'debug_info': []
        }

        def log_debug(message):
            logger.debug(message)
            response_data['debug_info'].append({
                'timestamp': datetime.now().isoformat(),
                'message': message
            })

        resume_file = request.files.get('resume')
        job_description = request.form.get('job_description')

        # Verify OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            log_debug("Error: OpenAI API key not found")
            raise ValueError("OpenAI API key not configured")

        log_debug(f"Received request - Resume file: {resume_file.filename if resume_file else 'None'}")
        
        try:
            # Save file temporarily to ensure it's properly read
            temp_path = os.path.join(app.instance_path, 'temp.pdf')
            os.makedirs(app.instance_path, exist_ok=True)
            resume_file.save(temp_path)
            
            log_debug("Starting PDF processing")
            try:
                pdf = PdfReader(temp_path)
                resume_text = ''
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            resume_text += page_text + '\n'
                    except Exception as page_error:
                        log_debug(f"Error extracting page: {str(page_error)}")
                
                if not resume_text.strip():
                    raise ValueError("No text could be extracted from PDF")
                
                log_debug(f"Successfully extracted {len(resume_text)} characters")
                
                # Update progress
                response_data['steps'].append({
                    'step': 1,
                    'status': 'complete',
                    'message': 'Resume uploaded and processed'
                })
                response_data['current_step'] = 1

                # Initialize resume optimizer with logged steps
                optimizer.original_resume = resume_text
                optimizer.job_description = job_description
                log_debug("Starting resume analysis")
                
                analysis = optimizer.analyze_relevance()
                if not analysis:
                    log_debug("Analysis returned no results")
                    raise ValueError("Resume analysis failed")
                
                log_debug("Analysis completed successfully")
                
                # Continue with optimization
                optimized = optimizer.optimize_resume(analysis)
                if not optimized:
                    log_debug("Optimization returned no results")
                    raise ValueError("Resume optimization failed")
                
                log_debug("Optimization completed successfully")
                
                # Return success response
                response_data.update({
                    'success': True,
                    'optimized_resume': optimized,
                    'analysis': analysis,
                    'current_step': 5,
                    'steps': [
                        {'step': 1, 'status': 'complete', 'message': 'Resume uploaded'},
                        {'step': 2, 'status': 'complete', 'message': 'Analysis complete'},
                        {'step': 3, 'status': 'complete', 'message': 'Skills matched'},
                        {'step': 4, 'status': 'complete', 'message': 'Resume optimized'},
                        {'step': 5, 'status': 'complete', 'message': 'Process completed'}
                    ]
                })
                
                return jsonify(response_data), 200
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            log_debug(f"Error details: {traceback.format_exc()}")
            raise ValueError(f"Error processing resume: {str(e)}")

    except Exception as e:
        logger.error(f"Server error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'success': False,
            'current_step': 0,
            'steps': [],
            'debug_info': response_data.get('debug_info', [])
        }), 500

@app.route('/download_resume')
def download_resume():
    try:
        return send_file(
            'static/optimized_resumes/latest.docx',
            as_attachment=True,
            download_name='optimized_resume.docx'
        )
    except Exception as e:
        return jsonify({'error': 'Failed to download resume'}), 500

if __name__ == '__main__':
    app.run(debug=True)