import requests
import json
import base64
from requests.exceptions import RequestException
import os

class JiraClient:
    jira_base_url = None

    def __init__(self):
        jira_api_token = os.getenv("JIRA_API_TOKEN")
        jira_username = os.getenv("JIRA_USERNAME")
        self.jira_base_url = os.getenv("JIRA_BASE_URL")

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{jira_username}:{jira_api_token}'.encode()).decode()}",
        }

    def fetch_issues(self, project_key: str, sprint_number: str, team_guid: str) -> list:
        jql = f'project = {project_key} AND sprint = {sprint_number} AND Team[Team] = {team_guid} AND status != DONE'
        url = f"{self.jira_base_url}/rest/api/2/search?jql={jql}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("issues", [])
        except RequestException as e:
            raise ValueError(f"Error fetching Jira issues: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding Jira response: {e}")

    def fetch_parent_issue_summary(self, issue_key: str) -> str:
        print('fetching parent issue summary', issue_key)
        url = f"{self.jira_base_url}/rest/api/2/issue/{issue_key}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data["fields"]["summary"]
        except RequestException as e:
            return f"Error: {issue_key} - {e}"
        except (json.JSONDecodeError, KeyError) as e:
            return f"Error: {issue_key} - Invalid Jira response: {e}"