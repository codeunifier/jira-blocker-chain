import requests
import json
import networkx as nx
import matplotlib.pyplot as plt
import base64
from dotenv import load_dotenv
import os

load_dotenv()

# keep these in a .env file
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
SPRINT_NUMBER = os.getenv("SPRINT_NUMBER")
TEAM_GUID = os.getenv("TEAM_GUID")
PROJECT_KEY = os.getenv("PROJECT_KEY")

DEFAULT_DOT_SIZE = 1500
DOT_SCALING_AMOUNT = 1000

# fetches the issues from Jira
def fetch_issues(headers):
    jql = f'project = {PROJECT_KEY} AND sprint = {SPRINT_NUMBER} AND Team[Team] = {TEAM_GUID}'
    url = f"{JIRA_BASE_URL}/rest/api/2/search?jql={jql}&expand=changelog"

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    return data.get("issues", [])
    
# finds the issues that are blocked or are blocking - we can ignore the rest
def get_blocker_chains(issues): 
    graph = nx.DiGraph()
    issues_in_chains = set()
    node_sizes = {} #add node_sizes

    for issue in issues:
        key = issue["key"]
        node_sizes[key] = DEFAULT_DOT_SIZE
        if "issuelinks" in issue["fields"]:
            for link in issue["fields"]["issuelinks"]:
                if "outwardIssue" in link and link["type"]["name"] == "Blocks":
                    blocked_issue_key = link["outwardIssue"]["key"]
                    if blocked_issue_key in [i["key"] for i in issues]:
                        graph.add_edge(key, blocked_issue_key)
                        issues_in_chains.add(key)
                        issues_in_chains.add(blocked_issue_key)
                        if key in node_sizes:
                            node_sizes[key]+= DOT_SCALING_AMOUNT

    return graph, issues_in_chains, node_sizes

# #########################################################
# gets the name of the parents for each ticket
# 
# can be generalized if there is more parent data we need
# #########################################################
def get_parent_data(chain_graph, issues, headers):
    parent_names = {}
    chain_node_colors = []
    parent_colors = {}
    color_cycle = plt.cm.get_cmap("Set3", chain_graph.number_of_nodes()).colors

     # Fetch parent info only for issues in blocker chains
    for node in chain_graph.nodes:
        parent_id = next((i["fields"].get("parent", {}).get("key") for i in issues if i["key"] == node), None)
        if parent_id:
            if parent_id not in parent_colors:
                parent_colors[parent_id] = color_cycle[len(parent_colors) % 20]
                parent_issue_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{parent_id}"

                try:
                    parent_response = requests.get(parent_issue_url, headers=headers)
                    parent_response.raise_for_status()
                    parent_data = parent_response.json()
                    parent_names[parent_id] = parent_data["fields"]["summary"]
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching parent issue {parent_id}: {e}")
                    parent_names[parent_id] = f"Error: {parent_id}"
            chain_node_colors.append(parent_colors[parent_id])
        else:
            chain_node_colors.append("lightgray")

    return parent_names, chain_node_colors, parent_colors

def visualize_blocker_chains(headers, issues):   
    graph, issues_in_chains, node_sizes = get_blocker_chains(issues)

    chain_graph = graph.subgraph(issues_in_chains)
    chain_issue_keys = {k: k for k in issues_in_chains}
    chain_node_sizes = [node_sizes[node] for node in chain_graph.nodes()] #get list of node sizes

    parent_names, chain_node_colors, parent_colors = get_parent_data(chain_graph, issues, headers)

    if chain_graph.number_of_nodes() > 0:
        # Create the graph
        pos = nx.kamada_kawai_layout(chain_graph)
        nx.draw(chain_graph, pos, with_labels=True, labels=chain_issue_keys, node_color=chain_node_colors, node_size=chain_node_sizes, font_size=8, font_color="black", arrowsize=20)
        plt.title(f"Jira Blocker Chains - Sprint {SPRINT_NUMBER}")

        # Create the legend
        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in parent_colors.values()]
        labels = [f"{parent_names.get(key, key)} ({key})" for key in parent_colors]
        if len(handles) > 0:
            plt.legend(handles, labels, title="Parent Issues")

        plt.show()
    else:
        print("No blocker chains found in the specified sprint.")

def main():
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_USERNAME}:{JIRA_API_TOKEN}'.encode()).decode()}",
        }

        issues = fetch_issues(headers)
        visualize_blocker_chains(headers, issues)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Jira data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
    except KeyError as e:
        print(f"Error accessing Jira data: {e}")

if __name__ == "__main__":
    main()
    print('Done')
