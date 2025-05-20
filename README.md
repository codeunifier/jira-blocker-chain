# Jira Blocker Chains

A tool for visualizing blocker chains in Jira sprints to help prioritize work effectively.

## AI Advisory

A lot of this code was written with the help of Claude. It is certainly not the cleanest / readable code. I will work on improving that as I continue working on this code. I am not the most experienced with highly sophisticated Python code so if you see any glaring issues, please open an Issue or even a Pull Request. It would be greatly appreciated.

## Setup

1. Create a `.env` file in the project directory with your Jira credentials:

```
JIRA_API_TOKEN = # generate your api token from Jira and paste it in here
JIRA_BASE_URL = "https://packback.atlassian.net"
JIRA_USERNAME = # your email address / jira username

# Default values (optional - can be set in GUI)
PROJECT_KEY = "ENG"
TEAM_GUID = "cea040b4-0710-4359-b46d-f9b64c27ef36"
SPRINT = "J07,K07,L07"
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Alternatively, you can install the package in development mode:

```
pip install -e .
```

This will make the package installable and create a command-line entry point.

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
3. Customize graph layout options (new feature!)
4. Generate the blocker chain graph with a single click

**Sprint Configuration:**
- You can specify multiple sprints by entering a comma-separated list (e.g., `J07,K07,L07`)
- The tool will fetch tickets from all specified sprints and combine them in a single graph
- This is useful for seeing blocker chains that span across multiple sprints

**Layout Controls:**
The GUI now provides controls to customize how the graph is rendered:

- **Cluster Layout**: The algorithm used to arrange clusters (epics) in the graph
- **Node Layout**: The algorithm used to arrange nodes (tickets) within each cluster
- **Cluster K Distance**: Controls spacing between clusters (higher values = more spread out)
- **Node K Distance**: Controls spacing between nodes within clusters

**Important:**
- Jira credentials (API token, username, base URL) must be configured in the `.env` file
- The GUI does not modify the `.env` file; it only reads default values from it
- Any changes to settings in the GUI are used only for the current session

### CLI Mode

For automation or scripting, you can run in command-line mode with various customization options:

```
python main.py --cli [LAYOUT OPTIONS]
```

Basic CLI options:
- `--cli`: Run in command-line mode using settings from `.env` file
- `--save`: Save the graph to a file instead of displaying it interactively

Layout customization options:
- `--cluster-layout {algorithm}`: Layout algorithm for clusters
- `--node-layout {algorithm}`: Layout algorithm for nodes within clusters
- `--cluster-k {value}`: K distance parameter for cluster layout (0.1-2.0)
- `--node-k {value}`: K distance parameter for node layout (0.1-2.0)

Available layout algorithms:
- `kamada-kawai`: Physics-based layout that often produces aesthetically pleasing graphs
- `spring`: Force-directed layout based on attraction/repulsion
- `fruchterman_reingold`: Alternative force-directed layout
- `circular`: Arranges nodes in a circle
- `planar`: Creates a planar layout (no edge crossings when possible)

Example with customized layout:
```
python main.py --cli --cluster-layout spring --node-layout circular --cluster-k 1.5 --node-k 0.8 --save
```

## Graph Output

When running in GUI mode or CLI mode with `--save`, the generated graph is saved as a PNG file in the `output` directory with a timestamp. The filename includes:

- Sprint codes
- Layout algorithms used
- Timestamp

This makes it easy to identify different graph iterations and compare different layout combinations.

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

Depending on the number of clusters, the number of nodes in a blocker chain, and the overall number of tickets, you may need to tweak some of the layout settings to produce a graph that works best (see below).

## Layout Optimization Tips

Different layout algorithms work better for different graphs, depending on the structure of your data:

- **Spring** and **Fruchterman-Reingold** layouts work well for most graphs and show natural clustering
- **Kamada-Kawai** often produces aesthetically pleasing graphs with minimal edge crossings
- **Circular** layouts are good for seeing the overall structure at a glance
- **Planar** layouts minimize edge crossings but can distort the graph in other ways

The **K distance** parameter controls spacing:
- Higher values (>1.0) create more spread-out layouts
- Lower values (<1.0) create more compact layouts
- Try different values to find the best visualization

The best approach is often to try several layout combinations to find what works best for your specific data.

## Additional Settings

For more customization options, see the `config.py` file which allows you to adjust:
- Color palette for the graph
- Default layout algorithms
- Node size parameters

See more on color palettes: https://matplotlib.org/stable/users/explain/colors/colormaps.html

See more on the plotting algorithms: https://networkx.org/documentation/networkx-1.11/reference/drawing.html#layout
