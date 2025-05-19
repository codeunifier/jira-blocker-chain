import requests
import json
import base64
from requests.exceptions import RequestException
import os
import urllib.parse

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

    def fetch_issues(self, project_key: str, sprint_codes: str, team_guid: str) -> list:
        """
        Fetch issues from Jira based on project, sprint(s), and team.
        Handles pagination to retrieve all matching issues.
        
        Args:
            project_key: The Jira project key
            sprint_codes: Comma-separated list of sprint codes
            team_guid: The team's GUID
            
        Returns:
            List of Jira issues
        """
        # Process the comma-separated sprint codes
        sprint_codes = sprint_codes.strip()
        if ',' in sprint_codes:
            # Multiple sprints: sprint in (A, B, C)
            sprint_parts = [part.strip() for part in sprint_codes.split(',') if part.strip()]
            sprint_clause = f"sprint in ({', '.join(sprint_parts)})"
        else:
            # Single sprint: sprint = X
            sprint_clause = f"sprint = {sprint_codes}"
        
        # Build the JQL query with the appropriate sprint clause
        jql = f'project = {project_key} AND {sprint_clause} AND Team[Team] = {team_guid} AND status != DONE'
        print(f"Executing JQL query: {jql}")
        
        # URL encode the JQL query
        encoded_jql = urllib.parse.quote(jql)
        
        # Initialize variables for pagination
        all_issues = []
        start_at = 0
        max_results = 100  # Maximum allowed by Jira
        total = None
        
        # Fetch all pages of results
        while total is None or start_at < total:
            url = f"{self.jira_base_url}/rest/api/2/search?jql={encoded_jql}&startAt={start_at}&maxResults={max_results}"
            
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                # Get issues from this page
                page_issues = data.get("issues", [])
                all_issues.extend(page_issues)
                
                # Get total for pagination
                if total is None:
                    total = data.get("total", 0)
                    print(f"Total issues matching query: {total}")
                
                # Update for next page
                start_at += len(page_issues)
                print(f"Fetched {len(page_issues)} issues (total fetched: {len(all_issues)} of {total})")
                
                # If this page returned fewer results than requested, we're done
                if len(page_issues) < max_results:
                    break
                    
            except RequestException as e:
                raise ValueError(f"Error fetching Jira issues: {e}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding Jira response: {e}")
        
        print(f"Successfully fetched all {len(all_issues)} issues")
        return all_issues

    def fetch_parent_issue_summary(self, issue_key: str) -> str:
        """Fetch the summary of a parent issue from Jira"""
        print(f'Fetching parent issue summary: {issue_key}')
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