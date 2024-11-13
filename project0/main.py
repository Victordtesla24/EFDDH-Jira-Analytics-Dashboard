import logging
from Jira_dashboard import JiraDashboard

def main():
    csv_path = '/Users/vicd/Downloads/EFDDH-Jira-12Nov.csv'
    
    try:
        dashboard = JiraDashboard(csv_path)
        dashboard.run_server()
    except FileNotFoundError:
        logging.error(f"CSV file not found at path: {csv_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()