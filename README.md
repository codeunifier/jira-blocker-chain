# Jira Blocker Chains

A tool for visualizing blocker chains in Jira sprints to help prioritize work effectively.

## Setup

1. Create a `.env` file in the project directory with your Jira credentials:

```
JIRA_API_TOKEN = # generate your api token from Jira and paste it in here
JIRA_BASE_URL = "https://packback.atlassian.net"
JIRA_USERNAME = # your email address / jira username

# Default values (optional - can be set in GUI)
PROJECT_KEY = "ENG"
TEAM_GUID = "cea040b4-0710-4359-b46d-f9b64c27ef36" # Armadillo
# TEAM_GUID = "a4bb26c1-324e-4218-9120-feda39ca1279" # Backpack
SPRINT = "J07,K07" # Comma-separated list of sprint codes
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

The application can be run in two modes:

### GUI Mode (Recommended)

Simply run the script without any arguments:

```
python main.py
```

This will open a graphical interface where you can:

1. Select your team (Armadillo or Backpack) from the dropdown
2. Configure project key and sprint(s)
3. Generate the blocker chain graph with a single click

**Sprint Configuration:**
- You can specify multiple sprints by entering a comma-separated list (e.g., `J07,K07,L07`)
- The tool will fetch tickets from all specified sprints and combine them in a single graph
- This is useful for seeing blocker chains that span across multiple sprints

**Important:**
- Jira credentials (API token, username, base URL) must be configured in the `.env` file
- The GUI does not modify the `.env` file; it only reads default values from it
- Any changes to settings in the GUI are used only for the current session

### CLI Mode

For automation or scripting, you can run in command-line mode using:

```
python main.py --cli
```

In CLI mode, the application reads all configuration from the `.env` file, including project key, team GUID, and sprint(s).

## Graph Output

When running in GUI mode, the generated graph is saved as a PNG file in the `output` directory with a timestamp. The filename includes the sprint codes and timestamp to make it easy to identify different graph iterations.

## Glossary

<ul>
    <li>
        <strong>Cluster</strong> - a graph element synonymous with an Epic. Clusters can be arranged in a separate layout than the nodes, which may produce a better visual. I have plans to update the behavior to consider a blocker chain a cluster, which I think will produce much better results.
    </li>
    <li><strong>Node</strong> - a graph element synonymous with a ticket.</li>
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