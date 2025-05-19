import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
from dotenv import load_dotenv
from jira_client import JiraClient
from graph_builder import build_blocker_graph
from visualizer import visualize_graph

class LoadingWindow:
    def __init__(self, parent, message="Loading..."):
        self.top = tk.Toplevel(parent)
        self.top.title("Processing")
        
        # Center the window relative to parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = 300
        height = 100
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        self.top.geometry(f"{width}x{height}+{x}+{y}")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Remove close button
        self.top.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Message
        tk.Label(self.top, text=message, padx=20, pady=10).pack()
        
        # Progress indicator
        self.progress = ttk.Progressbar(self.top, orient="horizontal", length=250, mode="indeterminate")
        self.progress.pack(padx=20, pady=10)
        self.progress.start(10)
    
    def close(self):
        self.top.grab_release()
        self.top.destroy()


class JiraBlockerChainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jira Blocker Chain")
        self.root.geometry("500x350")
        
        self.env_vars = self.load_env_variables()
        
        # Team GUIDs for dropdown
        self.team_options = {
            "Armadillo": "cea040b4-0710-4359-b46d-f9b64c27ef36",
            "Backpack": "a4bb26c1-324e-4218-9120-feda39ca1279"
        }
        
        # Create main frame
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project Settings Frame
        project_frame = ttk.LabelFrame(main_frame, text="Project Settings", padding=10)
        project_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(project_frame, text="Project Key:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.project_key = ttk.Entry(project_frame, width=40)
        self.project_key.grid(column=1, row=0, sticky=tk.W)
        if "PROJECT_KEY" in self.env_vars:
            self.project_key.insert(0, self.env_vars["PROJECT_KEY"])
            
        ttk.Label(project_frame, text="Team:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.team_var = tk.StringVar()
        self.team_combo = ttk.Combobox(project_frame, 
                                      textvariable=self.team_var,
                                      values=list(self.team_options.keys()),
                                      width=38,
                                      state="readonly")
        self.team_combo.grid(column=1, row=1, sticky=tk.W)
        
        # Set default selected team based on .env
        if "TEAM_GUID" in self.env_vars:
            current_guid = self.env_vars["TEAM_GUID"]
            for team_name, guid in self.team_options.items():
                if guid == current_guid:
                    self.team_var.set(team_name)
                    break
            if not self.team_var.get() and len(self.team_options) > 0:
                self.team_var.set(list(self.team_options.keys())[0])
        elif len(self.team_options) > 0:
            self.team_var.set(list(self.team_options.keys())[0])
            
        ttk.Label(project_frame, text="Sprints:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.sprint = ttk.Entry(project_frame, width=40)
        self.sprint.grid(column=1, row=2, sticky=tk.W)
        if "SPRINT" in self.env_vars:
            self.sprint.insert(0, self.env_vars["SPRINT"])
        
        # Add sprint help text
        sprint_help = "Comma-separated list of sprint codes (e.g. 'J07,K07,L07')"
        ttk.Label(project_frame, text=sprint_help, foreground="gray", font=('Arial', 8)).grid(column=1, row=3, sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Generate Graph", command=self.on_generate_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
        # Add help text
        help_text = "Note: Jira credentials must be configured in the .env file."
        ttk.Label(main_frame, text=help_text, foreground="gray").pack(side=tk.BOTTOM, pady=10)
    
    def load_env_variables(self):
        """Load environment variables from .env file"""
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path=dotenv_path)
        
        env_vars = {}
        for var in ["JIRA_API_TOKEN", "JIRA_USERNAME", "JIRA_BASE_URL", 
                   "PROJECT_KEY", "TEAM_GUID", "SPRINT"]:
            value = os.getenv(var)
            if value:
                env_vars[var] = value
        
        return env_vars
    
    def on_generate_click(self):
        """Handle generate button click by validating inputs and starting the background process"""
        # Validate required fields
        project_key = self.project_key.get().strip()
        team_name = self.team_var.get()
        team_guid = self.team_options.get(team_name, "")
        sprint_codes = self.sprint.get().strip()
        
        if not project_key:
            messagebox.showerror("Error", "Project Key is required!")
            return
        if not team_guid:
            messagebox.showerror("Error", "Team selection is required!")
            return
        if not sprint_codes:
            messagebox.showerror("Error", "At least one Sprint code is required!")
            return
        
        # Make sure Jira credentials exist in environment
        for key in ["JIRA_API_TOKEN", "JIRA_USERNAME", "JIRA_BASE_URL"]:
            if not os.getenv(key):
                messagebox.showerror("Error", f"{key} is missing from .env file! Please add it manually.")
                return
        
        # Start the processing in a separate thread with a loading window
        thread = threading.Thread(
            target=self.generate_graph_thread,
            args=(project_key, team_guid, sprint_codes),
            daemon=True
        )
        
        self.loading_window = LoadingWindow(
            self.root, 
            "Fetching data and generating graph...\nThis may take a moment."
        )
        
        thread.start()
    
    def generate_graph_thread(self, project_key, team_guid, sprint_codes):
        """Generate the graph in a background thread to keep UI responsive"""
        result = None
        error = None
        
        try:
            # Create Jira client using environment credentials
            jira_client = JiraClient()
            
            # Generate graph using form values directly (not from environment)
            issues = jira_client.fetch_issues(project_key, sprint_codes, team_guid)
            graph, issues_in_chains, node_sizes = build_blocker_graph(issues)
            chain_graph = graph.subgraph(issues_in_chains)
            
            # Save the graph to a file
            saved_file = visualize_graph(chain_graph, issues, node_sizes, jira_client, sprint_codes, save_file=True)
            result = saved_file
            
        except Exception as e:
            error = str(e)
        
        # Use after method to schedule UI updates on the main thread
        self.root.after(100, lambda: self.on_process_complete(result, error))
    
    def on_process_complete(self, result, error):
        """Handle the completion of graph generation process"""
        # Close the loading window
        if hasattr(self, 'loading_window'):
            self.loading_window.close()
        
        # Show result or error
        if error:
            messagebox.showerror("Error", f"An error occurred: {error}")
        elif result:
            messagebox.showinfo("Success", f"Graph generated and saved to:\n\n{result}")
        else:
            messagebox.showinfo("Information", "No blocker chains found in the specified sprints.")