# JIRA Analytics Dashboard

A powerful analytics dashboard for visualizing and analyzing JIRA project data, with a focus on sprint metrics, team velocity, and issue tracking.

## Features

- 📊 **Sprint Analytics**
  - Real-time sprint progress tracking
  - Burndown charts and velocity metrics
  - Issue status distribution
  - Story point analysis

- 📈 **Performance Metrics**
  - Team velocity trends
  - Completion rate analysis
  - Sprint-over-sprint comparisons
  - Issue type distribution

- 👥 **Team Capacity**
  - Resource allocation visualization
  - Workload distribution
  - Sprint capacity planning
  - Team member utilization

- 🔄 **Dynamic Sprint Selection**
  - Flexible sprint comparison
  - Historical data analysis
  - Trend identification
  - Performance benchmarking

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/EFDDH-Jira-Analytics-Dashboard.git
cd EFDDH-Jira-Analytics-Dashboard
```

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Set up the configuration:

```bash
cp .streamlit/config.toml.example .streamlit/config.toml
# Edit config.toml with your settings
```

## Usage

1. Start the Streamlit app:

```bash
./run.sh
```

1. Open your browser and navigate to:

```bash
http://localhost:8501
```

1. Upload your JIRA CSV export file:

```bash
# Export your JIRA data as CSV
# Use the file upload feature in the dashboard
# View your analytics instantly
```

## Development

### Project Structure

```plaintext
.
├── .streamlit/              # Streamlit configuration
├── src/                     # Source code
│   ├── components/          # Reusable UI components
│   ├── pages/              # Dashboard pages
│   ├── utils/              # Utility functions
│   ├── data/               # Data handling
│   ├── config/             # Configuration
│   └── tests/              # Test suite
├── logs/                    # Application logs
└── docs/                    # Documentation
```

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src --cov-report=html
```

### Code Quality

Format code:

```bash
black src/
isort src/
```

Run linters:

```bash
flake8 src/
mypy src/
```

## Deployment to Streamlit Cloud

1. Fork and clone the repository

2. Set up the following secrets in Streamlit Cloud:
   - `JIRA_SERVER`: Your JIRA server URL
   - `JIRA_USERNAME`: Your JIRA username
   - `JIRA_API_TOKEN`: Your JIRA API token

3. Deploy to Streamlit Cloud:
   - Connect your GitHub repository to [share.streamlit.io](https://share.streamlit.io)
   - Select the repository and branch
   - Set the main file path to: `src/streamlit_app.py`
   - Add the required secrets in the Streamlit Cloud dashboard
   - Deploy

### Environment Variables

Required environment variables (set in Streamlit Cloud):

- `JIRA_SERVER`: JIRA server URL
- `JIRA_USERNAME`: JIRA username
- `JIRA_API_TOKEN`: JIRA API token
- `DEBUG`: Set to "True" for debug mode (optional)

### Local Development

1. Copy `.env.example` to `.env`
2. Fill in your JIRA credentials
3. Run `./verify_and_fix.sh` to verify setup
4. Start the app with `streamlit run src/streamlit_app.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## Requirements

- Python 3.8+
- Streamlit 1.24.0+
- Pandas 1.5.0+
- Plotly 5.13.0+
- Additional dependencies in requirements.txt

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

1. Check the [Issues](https://github.com/yourusername/EFDDH-Jira-Analytics-Dashboard/issues) page
2. Create a new issue with detailed information
3. Contact the development team

## Acknowledgments

- JIRA API Documentation
- Streamlit Community
- Contributors and maintainers
