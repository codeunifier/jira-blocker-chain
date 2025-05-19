import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from config import COLOR_PALETTE, CLUSTER_LAYOUT, NODE_LAYOUT, CLUSTER_K_DIST, NODE_K_DIST
from jira_client import JiraClient
import math
import os
import datetime

# Creates a dictionary of node positions using various graph layout algorithms
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

# Groups nodes into clusters based on their parent issues
def _identify_clusters(graph: nx.DiGraph, issues: list) -> dict:
    clusters = {}
    for node in graph.nodes():
        parent_id = next((i["fields"].get("parent", {}).get("key") for i in issues if i["key"] == node), None)
        if parent_id:
            clusters.setdefault(parent_id, []).append(node)
        else:
            clusters.setdefault("orphan", []).append(node)
    return clusters

# Creates a graph where each node represents a cluster of issues
def _create_cluster_graph(clusters: dict) -> nx.Graph:
    cluster_graph = nx.Graph()
    for parent_id in clusters:
        cluster_graph.add_node(parent_id)
    return cluster_graph

# Calculates the positions of each cluster in the visualization
def _calculate_cluster_positions(cluster_graph: nx.Graph) -> dict:
    return create_plot_points(cluster_graph, layout_type=CLUSTER_LAYOUT, k=CLUSTER_K_DIST, iterations=100)

# Calculates the positions of nodes within each cluster
def _calculate_sub_node_positions(graph: nx.DiGraph, clusters: dict, cluster_pos: dict) -> dict:
    node_pos = {}
    for parent_id, nodes in clusters.items():
        subgraph = graph.subgraph(nodes)
        sub_pos = create_plot_points(subgraph, layout_type=NODE_LAYOUT, k=NODE_K_DIST, iterations=100)
        for node, (x, y) in sub_pos.items():
            node_pos[node] = (x + cluster_pos[parent_id][0], y + cluster_pos[parent_id][1])
    return node_pos

# Determines the radius needed for each cluster based on the positions of nodes within it
def _calculate_cluster_radii(graph: nx.DiGraph, clusters: dict, cluster_pos: dict, node_pos: dict) -> dict:
    cluster_radii = {}
    for parent_id, nodes in clusters.items():
        max_dist = 0
        for node in nodes:
            x, y = node_pos[node]
            dist = math.sqrt((x - cluster_pos[parent_id][0])**2 + (y - cluster_pos[parent_id][1])**2)
            max_dist = max(max_dist, dist)
        cluster_radii[parent_id] = max_dist * 1.2
    return cluster_radii

# Adjusts cluster positions to prevent overlap between clusters
def _adjust_cluster_positions(clusters: dict, cluster_pos: dict, cluster_radii: dict) -> dict:
    adjusted_cluster_pos = cluster_pos.copy()
    for parent_id1 in clusters:
        for parent_id2 in clusters:
            if parent_id1 != parent_id2:
                x1, y1 = adjusted_cluster_pos[parent_id1]
                x2, y2 = adjusted_cluster_pos[parent_id2]
                dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                min_dist = cluster_radii[parent_id1] + cluster_radii[parent_id2]
                if dist < min_dist:
                    dx, dy = x2 - x1, y2 - y1
                    angle = math.atan2(dy, dx) if dx != 0 or dy != 0 else 0
                    move_dist = (min_dist - dist) / 2
                    adjusted_cluster_pos[parent_id1] = (x1 - move_dist * math.cos(angle), y1 - move_dist * math.sin(angle))
                    adjusted_cluster_pos[parent_id2] = (x2 + move_dist * math.cos(angle), y2 + move_dist * math.sin(angle))
    return adjusted_cluster_pos

# Updates node positions based on the adjusted cluster positions
def _apply_adjusted_cluster_positions(clusters: dict, node_pos: dict, adjusted_cluster_pos: dict, cluster_pos: dict) -> dict:
    adjusted_node_pos = {}
    for node, (x, y) in node_pos.items():
        parent_id = next(pid for pid, nodes in clusters.items() if node in nodes)
        x_diff = adjusted_cluster_pos[parent_id][0] - cluster_pos[parent_id][0]
        y_diff = adjusted_cluster_pos[parent_id][1] - cluster_pos[parent_id][1]
        adjusted_node_pos[node] = (x + x_diff, y + y_diff)
    return adjusted_node_pos

# Assigns colors to nodes based on their parent issues
def _calculate_node_colors(graph: nx.DiGraph, issues: list, jira_client: JiraClient) -> tuple[list, dict]:
    color_cycle = plt.cm.get_cmap(COLOR_PALETTE, len(_identify_clusters(graph, issues))).colors
    node_colors, parent_colors, parent_names = [], {}, {}
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

# Renders the graph with all visual elements including nodes, edges, clusters, and legend
def _draw_graph(graph: nx.DiGraph, node_pos: dict, node_colors: list, node_sizes: dict, sprint_number: str, parent_colors: dict, parent_names: dict, clusters: dict, save_path=None):
    plt.figure(figsize=(12, 10))
    nx.draw(graph, node_pos, with_labels=True, labels={k: k for k in graph.nodes()}, node_color=node_colors, node_size=[node_sizes[node] for node in graph.nodes()], font_size=8, font_color="black", arrowsize=20)
    plt.title(f"Jira Blocker Chains - Sprint {sprint_number}")
    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in parent_colors.values()]
    labels = [f"{parent_names.get(key, key)} ({key})" for key in parent_colors]
    if handles:
        plt.legend(handles, labels, title="Parent Issues")
    for parent_id, nodes in clusters.items():
        cluster_x = [node_pos[node][0] for node in nodes]
        cluster_y = [node_pos[node][1] for node in nodes]
        center_x = sum(cluster_x) / len(cluster_x)
        center_y = sum(cluster_y) / len(cluster_y)
        radius = max(max(abs(x - center_x), abs(y - center_y)) for x, y in zip(cluster_x, cluster_y)) * 1.2
        circle = patches.Circle((center_x, center_y), radius, fill=False, edgecolor='gray', linestyle='--')
        plt.gca().add_patch(circle)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        return save_path
    else:
        plt.show()
        return None

# Main visualization function that orchestrates the entire graph rendering process
def visualize_graph(graph: nx.DiGraph, issues: list, node_sizes: dict, jira_client: JiraClient, sprint_number: str, save_file=True):
    if graph.number_of_nodes() == 0:
        print("No blocker chains found in the specified sprint.")
        return None
        
    clusters = _identify_clusters(graph, issues)
    cluster_graph = _create_cluster_graph(clusters)
    cluster_pos = _calculate_cluster_positions(cluster_graph)
    node_pos = _calculate_sub_node_positions(graph, clusters, cluster_pos)
    cluster_radii = _calculate_cluster_radii(graph, clusters, cluster_pos, node_pos)
    adjusted_cluster_pos = _adjust_cluster_positions(clusters, cluster_pos, cluster_radii)
    adjusted_node_pos = _apply_adjusted_cluster_positions(clusters, node_pos, adjusted_cluster_pos, cluster_pos)
    node_colors, parent_colors, parent_names = _calculate_node_colors(graph, issues, jira_client)
    
    if save_file:
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blocker_chain_sprint_{sprint_number}_{timestamp}.png"
        save_path = os.path.join(output_dir, filename)
        
        result = _draw_graph(graph, adjusted_node_pos, node_colors, node_sizes, 
                           sprint_number, parent_colors, parent_names, clusters, 
                           save_path=save_path)
        print(f"Graph saved to: {save_path}")
        return save_path
    else:
        # Just show the graph
        return _draw_graph(graph, adjusted_node_pos, node_colors, node_sizes, 
                         sprint_number, parent_colors, parent_names, clusters)