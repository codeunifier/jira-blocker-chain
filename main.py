from dotenv import load_dotenv
from jira_client import JiraClient
from graph_builder import build_blocker_graph
from visualizer import visualize_graph
from config import CLUSTER_LAYOUT, NODE_LAYOUT, CLUSTER_K_DIST, NODE_K_DIST
import os
import tkinter as tk
from gui import JiraBlockerChainGUI
import argparse


def run_cli_mode(args):
    """Run in command-line mode using environment variables and command-line arguments"""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    jira_client = JiraClient()

    try:
        # Get settings from environment variables
        project_key = os.getenv("PROJECT_KEY")
        sprint_codes = os.getenv("SPRINT")
        team_guid = os.getenv("TEAM_GUID")

        # Create layout settings dict for visualizer
        layout_settings = {
            'cluster_layout': args.cluster_layout,
            'node_layout': args.node_layout,
            'cluster_k': args.cluster_k,
            'node_k': args.node_k
        }
        
        # Print settings for user reference
        print(f"Project: {project_key}")
        print(f"Sprint(s): {sprint_codes}")
        print(f"Team GUID: {team_guid}")
        print(f"Layout - Cluster: {layout_settings['cluster_layout']} (k={layout_settings['cluster_k']}), " +
             f"Node: {layout_settings['node_layout']} (k={layout_settings['node_k']})")

        # Generate the graph
        issues = jira_client.fetch_issues(project_key, sprint_codes, team_guid)
        graph, issues_in_chains, node_sizes = build_blocker_graph(issues)
        chain_graph = graph.subgraph(issues_in_chains)
        
        # Use layout settings in visualization
        visualize_graph(
            chain_graph, issues, node_sizes, jira_client, sprint_codes, 
            save_file=args.save, layout_settings=layout_settings
        )
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    """Main entry point with support for GUI and CLI modes"""
    # Define available layout algorithms
    layout_algorithms = ["kamada-kawai", "spring", "fruchterman_reingold", "circular", "planar"]
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Jira Blocker Chain Tool')
    parser.add_argument('--cli', action='store_true', help='Run in command-line mode')
    parser.add_argument('--save', action='store_true', 
                        help='Save the graph to a file instead of displaying it (CLI mode only)')
    
    # Layout configuration arguments
    parser.add_argument('--cluster-layout', choices=layout_algorithms, default=CLUSTER_LAYOUT,
                       help=f'Layout algorithm for clusters (default: {CLUSTER_LAYOUT})')
    parser.add_argument('--node-layout', choices=layout_algorithms, default=NODE_LAYOUT,
                       help=f'Layout algorithm for nodes within clusters (default: {NODE_LAYOUT})')
    parser.add_argument('--cluster-k', type=float, default=CLUSTER_K_DIST,
                       help=f'K distance parameter for cluster layout (default: {CLUSTER_K_DIST})')
    parser.add_argument('--node-k', type=float, default=NODE_K_DIST,
                       help=f'K distance parameter for node layout (default: {NODE_K_DIST})')
    
    args = parser.parse_args()
    
    if args.cli:
        # Run in CLI mode with command-line arguments
        run_cli_mode(args)
    else:
        # Run in GUI mode
        root = tk.Tk()
        app = JiraBlockerChainGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
    print('Done')