import networkx as nx
import matplotlib.pyplot as plt
from config import COLOR_PALETTE, PLOTTING_ALGORITHM
from jira_client import JiraClient

def create_plot_points(graph: nx.DiGraph) -> dict:
    if PLOTTING_ALGORITHM == 'kamada-kawai':
        return nx.kamada_kawai_layout(graph)
    elif PLOTTING_ALGORITHM == 'spring':
        return nx.spring_layout(graph, k=0.5, iterations=70)
    elif PLOTTING_ALGORITHM == 'fruchterman_reingold':
        return nx.fruchterman_reingold_layout(graph, k=.7, iterations=50)
    elif PLOTTING_ALGORITHM == 'circular':
        return nx.circular_layout(graph)
    elif PLOTTING_ALGORITHM == 'planar':
        return nx.planar_layout(graph)
    else:
        raise ValueError("Invalid plotting algorithm selected.")

def visualize_graph(graph: nx.DiGraph, issues: list, node_sizes: dict, jira_client: JiraClient, sprint_number:str):
    if graph.number_of_nodes() == 0:
        print("No blocker chains found in the specified sprint.")
        return

    chain_issue_keys = {k: k for k in graph.nodes()}
    chain_node_sizes = [node_sizes[node] for node in graph.nodes()]
    color_cycle = plt.cm.get_cmap(COLOR_PALETTE, graph.number_of_nodes()).colors
    parent_colors = {}
    chain_node_colors = []
    parent_names = {}

    for node in graph.nodes():
        parent_id = next((i["fields"].get("parent", {}).get("key") for i in issues if i["key"] == node), None)
        if parent_id:
            if parent_id not in parent_colors:
                parent_colors[parent_id] = color_cycle[(len(parent_colors) * 3) % 100]
                parent_names[parent_id] = jira_client.fetch_parent_issue_summary(parent_id)
            chain_node_colors.append(parent_colors[parent_id])
        else:
            chain_node_colors.append("lightgray")

    pos = create_plot_points(graph)
    nx.draw(graph, pos, with_labels=True, labels=chain_issue_keys, node_color=chain_node_colors, node_size=chain_node_sizes, font_size=8, font_color="black", arrowsize=20)
    plt.title(f"Jira Blocker Chains - Sprint {sprint_number}")

    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in parent_colors.values()]
    labels = [f"{parent_names.get(key, key)} ({key})" for key in parent_colors]
    if len(handles) > 0:
        plt.legend(handles, labels, title="Parent Issues")

    plt.show()