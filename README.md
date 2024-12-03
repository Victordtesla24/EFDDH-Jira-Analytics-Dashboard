# Jira Analytics Dashboard

A Streamlit application for visualizing and analyzing Jira data.

## Setup

1. Create virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up pre-commit hooks (recommended):

   ```bash
   pre-commit install
   ```

4. Run the application:

   ```bash
   streamlit run src/streamlit_app.py
   ```

## Development

- Run tests: `pytest`
- Format code: `black src/`
- Check style: `flake8 src/`
- Sort imports: `isort src/`
- Type checking: `mypy src/`
- Run all checks: `./verify_and_fix.sh`

## Testing

- Run unit tests: `pytest src/tests/`
- Run integration tests: `pytest src/tests/integration/`
- Generate coverage report: `pytest --cov=src`
