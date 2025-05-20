import typing

import networkx as nx

from config import DEFAULT_DOT_SIZE, DOT_SCALING_AMOUNT


def build_blocker_graph(issues: list) -> typing.Tuple[nx.DiGraph, set, dict]:
    graph = nx.DiGraph()
    issues_in_chains = set()
    node_sizes = {}

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
                        node_sizes[key] += DOT_SCALING_AMOUNT

    return graph, issues_in_chains, node_sizes
