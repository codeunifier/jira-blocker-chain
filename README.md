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

## Controls to improve visualization

This isn't a perfect script yet, so there are lots of ways to make some tweaks to improve
the quality of the graph that this generates. The values in the config.py are your best friends.

Tweaking the color palette, the plotting algorithm, and the k distances should get you different variations
in the graph that may be more appealing, depending on the blocker chains. I've found the circular and spring
layouts to work the best, and the color palette is completely up to you.

See more on color palettes: https://matplotlib.org/stable/users/explain/colors/colormaps.html

See more on the plotting algorithms: https://networkx.org/documentation/networkx-1.11/reference/drawing.html#layout