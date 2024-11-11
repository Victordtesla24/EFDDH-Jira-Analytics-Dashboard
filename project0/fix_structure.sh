#!/bin/bash

# Fix directory structure
echo "Fixing directory structure..."

mkdir -p project0/{instance,scripts/src,static/{css,js,optimized_resumes},templates,web-ui/src,web-ui/public}
touch project0/{.env,.gitignore,README.md,requirements.txt,app.py,config.py}
touch project0/scripts/src/{__init__.py,ai_service.py,resume_optimiser.py,utils.py}
touch project0/static/css/style.css
touch project0/static/js/script.js
touch project0/static/optimized_resumes/latest.docx
touch project0/templates/index.html
touch project0/web-ui/src/{App.js,index.js,index.css}
touch project0/web-ui/public/index.html
touch project0/web-ui/package.json

# Ensure the scripts/src directory has an __init__.py file
echo "# This file is intentionally left blank to make the directory a package." > project0/scripts/src/__init__.py

# Install dependencies
echo "Installing dependencies..."

# Upgrade pip and install wheel
pip install --upgrade pip
pip install wheel

# Install dependencies from requirements.txt
pip install -r project0/requirements.txt

# Install specific versions of thinc, srsly, and blis to avoid build issues
pip install thinc==8.0.15 srsly==2.4.2 blis==0.7.4

# Install spacy and its language model
pip install spacy==3.7.2
python -m spacy download en_core_web_sm

# Run Flask application
echo "Running Flask application..."
flask run