import os

JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://packback.atlassian.net")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
SPRINT_NUMBER = os.getenv("SPRINT_NUMBER")
TEAM_GUID = os.getenv("TEAM_GUID")
PROJECT_KEY = os.getenv("PROJECT_KEY")

DEFAULT_DOT_SIZE = 1500
DOT_SCALING_AMOUNT = 1000

# COLOR_PALETTE = "Pastel1"
# COLOR_PALETTE = "Set3"
COLOR_PALETTE = "Set2"

# PLOTTING_ALGORITHM = "kamada-kawai"
PLOTTING_ALGORITHM = "spring"
# PLOTTING_ALGORITHM = "fruchterman_reingold"
# PLOTTING_ALGORITHM = "circular"
# PLOTTING_ALGORITHM = "planar"