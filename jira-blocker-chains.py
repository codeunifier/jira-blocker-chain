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

# applies the legend matching parent / epic names to dot colors
def apply_legend(lengend_colors, legend_labels, title):
    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in lengend_colors.values()]
    labels = [f"{legend_labels.get(key, key)} ({key})" for key in lengend_colors]
    if len(handles) > 0:
        plt.legend(handles, labels, title=title)

# #########################################################################################
# plots the dots on the graph.
#
# currently using the kamada_kawai_layout algorithm, but spring_layout could also work
# #########################################################################################
def graph_issues(chain_graph, chain_issue_keys, chain_node_colors, node_sizes):
    pos = nx.kamada_kawai_layout(chain_graph)
    nx.draw(chain_graph, pos, with_labels=True, labels=chain_issue_keys, node_color=chain_node_colors, node_size=node_sizes, font_size=8, font_color="black", arrowsize=20)
    plt.title(f"Jira Blocker Chains - Sprint {SPRINT_NUMBER}")

# fetches the issues from Jira
def fetch_issues(headers):
    jql = f'project = {PROJECT_KEY} AND sprint = {SPRINT_NUMBER} AND Team[Team] = {TEAM_GUID}'
    url = f"{JIRA_BASE_URL}/rest/api/2/search?jql={jql}&expand=changelog"

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    return data.get("issues", [])

# finds the issues that are blocked or are blocking - we can ignore the rest
def get_issues_in_blocker_chains(graph, issues, node_sizes):
    issues_in_chains = set()

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

    return issues_in_chains

# #########################################################
# gets the name of the parents for each ticket
# 
# can be generalized if there is more parent data we need
# #########################################################
def get_parent_data(chain_graph, issues, headers):
    parent_names = {}
    chain_node_colors = []
    parent_colors = {}
    color_cycle = plt.cm.get_cmap("tab20", 20).colors

     # Fetch parent info only for issues in blocker chains
    for node in chain_graph.nodes:
        parent_id = next((i["fields"].get("parent", {}).get("key") for i in issues if i["key"] == node), None)
        if parent_id:
            if parent_id not in parent_colors:
                parent_colors[parent_id] = color_cycle[len(parent_colors) % 20]
                parent_issue_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{parent_id}"
                parent_response = requests.get(parent_issue_url, headers=headers)
                parent_response.raise_for_status()
                parent_data = parent_response.json()
                parent_names[parent_id] = parent_data["fields"]["summary"]
            chain_node_colors.append(parent_colors[parent_id])
        else:
            chain_node_colors.append("lightgray")

    return parent_names, chain_node_colors, parent_colors

def get_issue_keys(issues):
    issue_keys = {}  # Store issue keys and their summaries
    for issue in issues:
        key = issue["key"]
        issue_keys[key] = key
    return issue_keys

def visualize_jira_blockers(headers, issues):    
    graph = nx.DiGraph()
    node_sizes = {} #add node_sizes

    issue_keys = get_issue_keys(issues)
    issues_in_chains = get_issues_in_blocker_chains(graph, issues, node_sizes)

    chain_graph = graph.subgraph(issues_in_chains)
    chain_issue_keys = {k: issue_keys[k] for k in issues_in_chains}
    chain_node_sizes = [node_sizes[node] for node in chain_graph.nodes()] #get list of node sizes

    parent_names, chain_node_colors, parent_colors = get_parent_data(chain_graph, issues, headers)

    if chain_graph.number_of_nodes() > 0:
        # Create the graph
        graph_issues(chain_graph, chain_issue_keys, chain_node_colors, chain_node_sizes)

        # Create the legend
        apply_legend(parent_colors, parent_names, "Parent Issues")

        plt.show()
    else:
        print("No blocker chains found in the specified sprint.")

def run():
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_USERNAME}:{JIRA_API_TOKEN}'.encode()).decode()}",
        }

        issues = fetch_issues(headers)
        visualize_jira_blockers(headers, issues)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Jira data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
    except KeyError as e:
        print(f"Error accessing Jira data: {e}")


run()
print('Done')