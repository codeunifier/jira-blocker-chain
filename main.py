from dotenv import load_dotenv
from jira_client import JiraClient
from graph_builder import build_blocker_graph
from visualizer import visualize_graph
import os
import tkinter as tk
from gui import JiraBlockerChainGUI


def run_cli_mode():
    """Run in command-line mode using environment variables"""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    jira_client = JiraClient()

    try:
        project_key = os.getenv("PROJECT_KEY")
        sprint_code = os.getenv("SPRINT")
        team_guid = os.getenv("TEAM_GUID")

        issues = jira_client.fetch_issues(project_key, sprint_code, team_guid)
        graph, issues_in_chains, node_sizes = build_blocker_graph(issues)
        chain_graph = graph.subgraph(issues_in_chains)
        visualize_graph(chain_graph, issues, node_sizes, jira_client, sprint_code)
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    """Main entry point with support for GUI and CLI modes"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Jira Blocker Chain Tool')
    parser.add_argument('--cli', action='store_true', help='Run in command-line mode')
    args = parser.parse_args()
    
    if args.cli:
        # Run in CLI mode
        run_cli_mode()
    else:
        # Run in GUI mode
        root = tk.Tk()
        app = JiraBlockerChainGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
    print('Done')