# Jira Blocker Chains

## Environment variables

```
JIRA_API_TOKEN = # generate your api token from Jira and paste it in here
JIRA_BASE_URL = "https://packback.atlassian.net"
JIRA_USERNAME = # your email address / jira username

PROJECT_KEY = # the three-letter code for the project
TEAM_GUID = # this is a guid that can be pulled from Jira for the team
SPRINT_NUMBER = # this is a number that can be pulled from Jira for the sprint
```

## Glossary

<ul>
    <li>
        <strong>Cluster</strong> - a graph element synonymous with an Epic. Clusters can be arranged in a separate layout than the nodes, which may produce a better visual. I have plans to update the behavior to consider a blocker chain a cluster, which I think will produce much better results.
    </li>
    <li><strong>Node</strong> - a graph elemnent synonymous with a ticket.</li>
    <li><strong>Edge</strong> - a graph element indicating a ticket blocking another ticket</li>
</ul>

## Explanation of Graph

Nodes on the graph represent tickets, and clusters represent epics (soon to be changed, as mentioned above). Tickets that are blocking other tickets should be higher priority, so they become visually bigger on the graph. The biggest tickets should be considered the most crucial to complete so as to unblock everything else in their chains.

Depending on the number of clusters, the number of nodes in a blocker chain, and the overall number of tickets, you may need to tweak some of the configs or run this script a few times to produce a graph that works best (see below).

## Controls to improve visualization

This isn't a perfect script yet, so there are lots of ways to make some tweaks to improve
the quality of the graph that this generates. The values in the config.py are your best friends.

Tweaking the color palette, the plotting algorithm, and the k distances should get you different variations in the graph that may be more appealing, depending on the blocker chains. I've found the circular and spring layouts to work the best, and the color palette is completely up to you. Rerunning the script with the same configs may product different graphs, so try it out a few times until you get one that's decent.

See more on color palettes: https://matplotlib.org/stable/users/explain/colors/colormaps.html

See more on the plotting algorithms: https://networkx.org/documentation/networkx-1.11/reference/drawing.html#layout