import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from config import COLOR_PALETTE
from jira_client import JiraClient

CLUSTER_LAYOUT = 'spring'
NODE_LAYOUT = 'circular'

def create_plot_points(graph: nx.DiGraph, layout_type='spring', k=0.5, iterations=50) -> dict:
    if layout_type == 'kamada-kawai':
        return nx.kamada_kawai_layout(graph)
    elif layout_type == 'spring':
        return nx.spring_layout(graph, k=k, iterations=iterations)
    elif layout_type == 'fruchterman_reingold':
        return nx.fruchterman_reingold_layout(graph, k=k, iterations=iterations)
    elif layout_type == 'circular':
        return nx.circular_layout(graph)
    elif layout_type == 'planar':
        return nx.planar_layout(graph)
    else:
        raise ValueError("Invalid plotting algorithm selected.")

def _identify_clusters(graph: nx.DiGraph, issues: list) -> dict:
    clusters = {}
    for node in graph.nodes():
        parent_id = next((i["fields"].get("parent", {}).get("key") for i in issues if i["key"] == node), None)
        if parent_id:
            if parent_id not in clusters:
                clusters[parent_id] = []
            clusters[parent_id].append(node)
        else:
            if "orphan" not in clusters:
                clusters["orphan"] = []
            clusters["orphan"].append(node)
    return clusters

def _calculate_node_positions(graph: nx.DiGraph, clusters: dict) -> dict:
    cluster_graph = nx.Graph()
    for parent_id in clusters:
        cluster_graph.add_node(parent_id)
    cluster_pos = create_plot_points(cluster_graph, layout_type=CLUSTER_LAYOUT, k=1.0, iterations=100)

    node_pos = {}
    for parent_id, nodes in clusters.items():
        subgraph = graph.subgraph(nodes)
        sub_pos = create_plot_points(subgraph, layout_type=NODE_LAYOUT, k=0.5, iterations=100)
        center_x, center_y = cluster_pos[parent_id]
        for node, (x, y) in sub_pos.items():
            node_pos[node] = (x + center_x, y + center_y)
    return node_pos

def _calculate_node_colors(graph: nx.DiGraph, issues: list, jira_client: JiraClient) -> tuple[list, dict]:
    color_cycle = plt.cm.get_cmap(COLOR_PALETTE, len(_identify_clusters(graph, issues))).colors
    node_colors = []
    parent_colors = {}
    parent_names = {}

    for node in graph.nodes():
        parent_id = next((i["fields"].get("parent", {}).get("key") for i in issues if i["key"] == node), None)
        if parent_id:
            if parent_id not in parent_colors:
                parent_colors[parent_id] = color_cycle[len(parent_colors) % len(color_cycle)]
                parent_names[parent_id] = jira_client.fetch_parent_issue_summary(parent_id)
            node_colors.append(parent_colors[parent_id])
        else:
            node_colors.append("lightgray")
    return node_colors, parent_colors, parent_names

def _draw_graph(graph: nx.DiGraph, node_pos: dict, node_colors: list, node_sizes: dict, sprint_number: str, parent_colors: dict, parent_names:dict, clusters: dict):
    nx.draw(graph, node_pos, with_labels=True, labels={k: k for k in graph.nodes()}, node_color=node_colors, node_size=[node_sizes[node] for node in graph.nodes()], font_size=8, font_color="black", arrowsize=20)
    plt.title(f"Jira Blocker Chains - Sprint {sprint_number}")

    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in parent_colors.values()]
    labels = [f"{parent_names.get(key, key)} ({key})" for key in parent_colors]
    if len(handles) > 0:
        plt.legend(handles, labels, title="Parent Issues")

    # Add circles around clusters
    for parent_id, nodes in clusters.items():
        cluster_x = [node_pos[node][0] for node in nodes]
        cluster_y = [node_pos[node][1] for node in nodes]
        center_x = sum(cluster_x) / len(cluster_x)
        center_y = sum(cluster_y) / len(cluster_y)
        radius = max(max(abs(x - center_x), abs(y - center_y)) for x, y in zip(cluster_x, cluster_y)) * 1.2 #add a buffer to the radius.

        circle = patches.Circle((center_x, center_y), radius, fill=False, edgecolor='gray', linestyle='--')
        plt.gca().add_patch(circle)

    plt.show()

def visualize_graph(graph: nx.DiGraph, issues: list, node_sizes: dict, jira_client: JiraClient, sprint_number: str):
    if graph.number_of_nodes() == 0:
        print("No blocker chains found in the specified sprint.")
        return

    clusters = _identify_clusters(graph, issues)
    node_pos = _calculate_node_positions(graph, clusters)
    node_colors, parent_colors, parent_names = _calculate_node_colors(graph, issues, jira_client)
    _draw_graph(graph, node_pos, node_colors, node_sizes, sprint_number, parent_colors, parent_names, clusters)