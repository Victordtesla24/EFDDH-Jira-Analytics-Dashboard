"""CSS styles for the Streamlit application."""

CUSTOM_CSS = """
    <style>
        /* Main app styling */
        .stApp {
            font-family: Arial, sans-serif;
        }

        /* Header styling */
        .main-header {
            padding: 1.5rem;
            text-align: center;
            background: linear-gradient(90deg, #007DBA, #0A2F64);
            color: white;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .main-header h1 {
            margin: 0;
            padding: 0;
            font-size: 2.5rem;
            font-weight: 600;
        }

        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 0.9rem;
        }

        /* Metrics container */
        .metrics-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2rem;
        }

        /* Metric card styling */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #007DBA;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
            cursor: help;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        .metric-card h3 {
            margin: 0;
            color: #666;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #007DBA;
            margin: 0.5rem 0;
        }

        .metric-delta {
            font-size: 0.9rem;
            color: #78BE20;
        }

        /* Dashboard content */
        .dashboard-content {
            margin-top: 2rem;
        }

        /* Chart container styling */
        .chart-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            transition: transform 0.2s ease;
        }

        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        /* Upload section styling */
        .upload-section {
            background-color: #F8F9FA;
            padding: 2rem;
            border-radius: 10px;
            border: 2px dashed #007DBA;
            text-align: center;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }

        .upload-section:hover {
            background-color: #E3F2FD;
            border-color: #0A2F64;
        }

        .upload-section h3 {
            color: #007DBA;
            margin-bottom: 0.5rem;
        }

        .upload-section p {
            color: #666;
            margin: 0;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #F5F5F5;
            border-bottom: 2px solid #007DBA;
            padding: 0 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0px 24px;
            background-color: #FFFFFF;
            border-radius: 4px 4px 0px 0px;
            color: #1E1E1E;
            font-weight: 500;
            border: none;
            transition: all 0.3s ease;
        }

        .stTabs [aria-selected="true"] {
            background-color: #007DBA;
            color: #FFFFFF;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #F8F9FA;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            color: #0A2F64;
        }

        .streamlit-expanderHeader:hover {
            background-color: #E3F2FD;
        }

        /* Documentation styling */
        .doc-section {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }

        .doc-section h3 {
            color: #0A2F64;
            border-bottom: 2px solid #007DBA;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }

        /* Info box styling */
        .info-box {
            background-color: #E3F2FD;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #007DBA;
            margin-bottom: 1rem;
        }

        /* Table styling */
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9em;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }

        .styled-table thead tr {
            background-color: #007DBA;
            color: white;
            text-align: left;
        }

        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
        }

        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }

        .styled-table tbody tr:nth-of-type(even) {
            background-color: #f8f9fa;
        }

        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid #007DBA;
        }

        /* Success message styling */
        .success-message {
            color: #4CAF50;
            background-color: #E8F5E9;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            display: flex;
            align-items: center;
        }

        /* Error message styling */
        .error-message {
            color: #DC3545;
            background-color: #FFEBEE;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            display: flex;
            align-items: center;
        }

        /* Button styling */
        .stButton>button {
            background-color: #007DBA;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #0A2F64;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* Tooltip styling */
        [title] {
            position: relative;
            cursor: help;
        }

        [title]:hover::before {
            content: attr(title);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            padding: 0.5rem;
            background-color: #333;
            color: white;
            border-radius: 4px;
            font-size: 0.8rem;
            white-space: nowrap;
            z-index: 1000;
        }
    </style>
"""
