from dotenv import load_dotenv
from jira_client import JiraClient
from graph_builder import build_blocker_graph
from visualizer import visualize_graph
import os

def main():
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

if __name__ == "__main__":
    main()
    print('Done')
