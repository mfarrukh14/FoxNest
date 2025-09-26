#!/usr/bin/env python3
"""
Fox Client - Local version control client for FoxNest
"""

import os
import json
import hashlib
import shutil
import argparse
import base64
import sys
from datetime import datetime
from pathlib import Path
import requests

class FoxClient:
    def __init__(self):
        self.fox_dir = Path(".fox")
        self.config_file = self.fox_dir / "config.json"
        self.staging_dir = self.fox_dir / "staging"
        self.objects_dir = self.fox_dir / "objects"
        self.commits_file = self.fox_dir / "commits.json"
        self.head_file = self.fox_dir / "HEAD"
        
        # Default server configuration
        self.server_url = "http://localhost:5000"
    
    def check_repository(self, command_name="command"):
        """Check if current directory is a Fox repository"""
        if not self.is_initialized():
            current_dir = Path.cwd().name
            print(f"Fatal: {current_dir} not a repository, run 'fox init' to initialize a new repository")
            return False
        return True
    
    def get_origin_url(self):
        """Get the origin URL from config"""
        config = self.load_config()
        if not config:
            return None
        return config.get("origin_url")
    
    def set_origin(self, origin_url):
        """Set the origin URL for the repository"""
        if not self.check_repository("set origin"):
            return False
        
        # Validate URL format
        if not origin_url.startswith(('http://', 'https://')):
            # Assume it's an IP:port and add http://
            if ':' in origin_url:
                origin_url = f"http://{origin_url}"
            else:
                origin_url = f"http://{origin_url}:5000"
        
        config = self.load_config()
        config["origin_url"] = origin_url
        self.save_config(config)
        
        print(f"Origin set to: {origin_url}")
        return True
    
    def init(self, username=None, repo_name=None):
        """Initialize a new Fox repository"""
        if self.fox_dir.exists():
            print("Repository already initialized!")
            return False
        
        if not username:
            username = input("Enter username: ")
        if not repo_name:
            repo_name = input("Enter repository name: ")
        
        # Create .fox directory structure
        self.fox_dir.mkdir()
        self.staging_dir.mkdir()
        self.objects_dir.mkdir()
        
        # Create initial configuration
        config = {
            "username": username,
            "repo_name": repo_name,
            "server_url": self.server_url,
            "repo_id": None,
            "initialized_at": datetime.now().isoformat()
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        # Initialize empty commits file
        with open(self.commits_file, "w") as f:
            json.dump([], f)
        
        print(f"Initialized Fox repository for {username}/{repo_name}")
        print("Use 'fox add <files>' to add files and 'fox commit' to commit changes")
        return True
    
    def is_initialized(self):
        """Check if repository is initialized"""
        return self.fox_dir.exists() and self.config_file.exists()
    
    def load_config(self):
        """Load repository configuration"""
        if not self.is_initialized():
            print("Not a Fox repository! Run 'fox init' first.")
            return None
        
        with open(self.config_file, "r") as f:
            return json.load(f)
    
    def save_config(self, config):
        """Save repository configuration"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def get_file_hash(self, filepath):
        """Generate hash for a file"""
        with open(filepath, "rb") as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()[:16]
    
    def get_all_files(self):
        """Get all files in the working directory (excluding .fox directory)"""
        all_files = []
        for root, dirs, files in os.walk("."):
            # Skip .fox directory
            if ".fox" in dirs:
                dirs.remove(".fox")
            
            for file in files:
                filepath = Path(root) / file
                # Normalize path and convert to relative
                filepath = filepath.resolve().relative_to(Path.cwd())
                all_files.append(filepath)
        
        return all_files
    
    def add(self, files, add_all=False):
        """Add files to staging area"""
        if not self.check_repository("add"):
            return False

        # Handle --all flag or when files contains "."
        if add_all or (files and "." in files):
            files = [str(f) for f in self.get_all_files()]
            if not files:
                print("No files found to add")
                return True
        elif not files:
            print("No files specified. Use 'fox add <files>' or 'fox add --all' to add files")
            return False

        for file_pattern in files:
            file_paths = list(Path(".").glob(file_pattern))
            if not file_paths:
                file_paths = [Path(file_pattern)]
            
            for filepath in file_paths:
                if filepath.exists() and filepath.is_file():
                    # Skip .fox directory files
                    if ".fox" in str(filepath):
                        continue
                    
                    file_hash = self.get_file_hash(filepath)
                    
                    # Copy file to objects directory
                    object_path = self.objects_dir / file_hash
                    shutil.copy2(filepath, object_path)
                    
                    # Add to staging
                    staging_file = self.staging_dir / filepath.name
                    with open(staging_file, "w") as f:
                        json.dump({
                            "path": str(filepath),
                            "hash": file_hash,
                            "added_at": datetime.now().isoformat()
                        }, f)
                    
                    print(f"Added {filepath}")
                else:
                    print(f"File not found: {filepath}")
        
        return True
    
    def commit(self, message):
        """Commit staged changes"""
        if not self.check_repository("commit"):
            return False
        
        config = self.load_config()
        
        # Check if there are staged files
        staged_files = list(self.staging_dir.glob("*"))
        if not staged_files:
            print("No changes staged for commit")
            return False
        
        # Generate commit ID
        commit_id = hashlib.sha256(f"{message}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Get parent commit
        parent = None
        if self.head_file.exists():
            with open(self.head_file, "r") as f:
                parent = f.read().strip()
        
        # Collect staged files
        files = {}
        for staging_file in staged_files:
            with open(staging_file, "r") as f:
                file_info = json.load(f)
            
            # Read file content and encode
            with open(self.objects_dir / file_info["hash"], "rb") as f:
                content = base64.b64encode(f.read()).decode()
            
            files[file_info["hash"]] = {
                "path": file_info["path"],
                "content": content
            }
        
        # Create commit object
        commit = {
            "id": commit_id,
            "message": message,
            "author": config["username"],
            "timestamp": datetime.now().isoformat(),
            "parent": parent,
            "files": files
        }
        
        # Save commit locally
        commits = []
        if self.commits_file.exists():
            with open(self.commits_file, "r") as f:
                commits = json.load(f)
        
        commits.append(commit)
        with open(self.commits_file, "w") as f:
            json.dump(commits, f, indent=2)
        
        # Update HEAD
        with open(self.head_file, "w") as f:
            f.write(commit_id)
        
        # Clear staging area
        shutil.rmtree(self.staging_dir)
        self.staging_dir.mkdir()
        
        print(f"Committed changes: {commit_id}")
        print(f"Message: {message}")
        print(f"Files: {len(files)}")
        
        return True
    
    def create_remote_repository(self, config):
        """Create repository on remote server"""
        try:
            response = requests.post(
                f"{config['server_url']}/api/repository/create",
                json={
                    "username": config["username"],
                    "repo_name": config["repo_name"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    return data["repo_id"]
                else:
                    print(f"Server error: {data.get('error')}")
            else:
                print(f"HTTP error: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
        
        return None
    
    def push(self):
        """Push commits to remote repository"""
        if not self.check_repository("push"):
            return False
        
        config = self.load_config()
        
        # Check if origin is set
        origin_url = self.get_origin_url()
        if not origin_url:
            print("Fatal: No origin set. Use 'fox set origin <ip:port>' to set the remote repository URL")
            print("Example: fox set origin 192.168.15.207:502")
            return False
        
        # Update server_url to use origin
        self.server_url = origin_url
        config["server_url"] = origin_url
        
        # Create remote repository if needed
        if not config.get("repo_id"):
            print("Creating remote repository...")
            repo_id = self.create_remote_repository(config)
            if not repo_id:
                print("Failed to create remote repository")
                return False
            
            config["repo_id"] = repo_id
            self.save_config(config)
            print(f"Created remote repository: {repo_id}")
        
        # Load local commits
        if not self.commits_file.exists():
            print("No commits to push")
            return False
        
        with open(self.commits_file, "r") as f:
            commits = json.load(f)
        
        if not commits:
            print("No commits to push")
            return False
        
        # Push each commit
        for commit in commits:
            try:
                # Prepare commit data for server
                commit_data = commit.copy()
                
                # Convert file format for server
                server_files = {}
                for file_hash, file_info in commit["files"].items():
                    server_files[file_hash] = file_info["content"]
                
                commit_data["files"] = server_files
                
                response = requests.post(
                    f"{config['server_url']}/api/repository/{config['repo_id']}/push",
                    json={"commit": commit_data},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        print(f"Pushed commit: {commit['id']}")
                    else:
                        print(f"Failed to push commit {commit['id']}: {data.get('error')}")
                        return False
                else:
                    print(f"HTTP error: {response.status_code}")
                    return False
            
            except requests.exceptions.RequestException as e:
                print(f"Network error while pushing {commit['id']}: {e}")
                return False
        
        print("All commits pushed successfully!")
        return True
    
    def pull(self):
        """Pull commits from remote repository"""
        if not self.check_repository("pull"):
            return False
        
        config = self.load_config()
        
        # Check if origin is set
        origin_url = self.get_origin_url()
        if not origin_url:
            print("Fatal: No origin set. Use 'fox set origin <ip:port>' to set the remote repository URL")
            print("Example: fox set origin 192.168.15.207:502")
            return False
        
        # Update server_url to use origin
        self.server_url = origin_url
        
        if not config.get("repo_id"):
            print("No remote repository configured")
            return False
        
        try:
            # Get current HEAD
            since_commit = None
            if self.head_file.exists():
                with open(self.head_file, "r") as f:
                    since_commit = f.read().strip()
            
            # Pull from server
            params = {"since": since_commit} if since_commit else {}
            response = requests.get(
                f"{config['server_url']}/api/repository/{config['repo_id']}/pull",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    commits = data["commits"]
                    
                    if not commits:
                        print("Already up to date")
                        return True
                    
                    # Update local repository with pulled commits
                    for commit in commits:
                        # Save files from commit
                        for file_hash, content in commit["files"].items():
                            object_path = self.objects_dir / file_hash
                            with open(object_path, "wb") as f:
                                f.write(base64.b64decode(content))
                    
                    # Update local commits
                    local_commits = []
                    if self.commits_file.exists():
                        with open(self.commits_file, "r") as f:
                            local_commits = json.load(f)
                    
                    local_commits.extend(commits)
                    with open(self.commits_file, "w") as f:
                        json.dump(local_commits, f, indent=2)
                    
                    # Update HEAD
                    if data.get("head"):
                        with open(self.head_file, "w") as f:
                            f.write(data["head"])
                    
                    print(f"Pulled {len(commits)} commits")
                    return True
                else:
                    print(f"Server error: {data.get('error')}")
            else:
                print(f"HTTP error: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
        
        return False
    
    def status(self):
        """Show repository status"""
        if not self.check_repository("status"):
            return False
        
        config = self.load_config()
        origin_url = self.get_origin_url()
        
        print(f"Repository: {config['username']}/{config['repo_name']}")
        print(f"Origin: {origin_url if origin_url else 'Not set'}")
        
        # Show current HEAD
        if self.head_file.exists():
            with open(self.head_file, "r") as f:
                head = f.read().strip()
            print(f"Current commit: {head}")
        else:
            print("No commits yet")
        
        # Show staged files
        staged_files = list(self.staging_dir.glob("*"))
        if staged_files:
            print(f"\nStaged files ({len(staged_files)}):")
            for staging_file in staged_files:
                with open(staging_file, "r") as f:
                    file_info = json.load(f)
                print(f"  {file_info['path']}")
        else:
            print("\nNo files staged")
        
        return True
    
    def status_short(self):
        """Show short repository status"""
        if not self.check_repository("status"):
            return False
        
        # Show staged files with short format
        staged_files = list(self.staging_dir.glob("*"))
        if staged_files:
            for staging_file in staged_files:
                with open(staging_file, "r") as f:
                    file_info = json.load(f)
                print(f"A  {file_info['path']}")
        else:
            print("Nothing staged")
        
        return True
    
    def log(self, max_count=None):
        """Show commit history"""
        if not self.check_repository("log"):
            return False
        
        if not self.commits_file.exists():
            print("No commits yet")
            return True
        
        with open(self.commits_file, "r") as f:
            commits = json.load(f)
        
        if not commits:
            print("No commits yet")
            return True
        
        print("Commit history:")
        commits_to_show = commits
        if max_count:
            commits_to_show = commits[-max_count:]
        
        for commit in reversed(commits_to_show):  # Most recent first
            print(f"\nCommit: {commit['id']}")
            print(f"Author: {commit['author']}")
            print(f"Date: {commit['timestamp']}")
            print(f"Message: {commit['message']}")
            if commit.get('parent'):
                print(f"Parent: {commit['parent']}")
            print(f"Files: {len(commit['files'])}")
        
        return True
    
    def log_oneline(self, max_count=None):
        """Show commit history in one-line format"""
        if not self.check_repository("log"):
            return False
        
        if not self.commits_file.exists():
            print("No commits yet")
            return True
        
        with open(self.commits_file, "r") as f:
            commits = json.load(f)
        
        if not commits:
            print("No commits yet")
            return True
        
        commits_to_show = commits
        if max_count:
            commits_to_show = commits[-max_count:]
        
        for commit in reversed(commits_to_show):  # Most recent first
            date = commit['timestamp'][:10]  # Just the date part
            print(f"{commit['id']} {date} {commit['author']}: {commit['message']}")
        
        return True

def print_version():
    """Print FoxNest version information"""
    print("🦊 FoxNest Version Control System")
    print("Version: 1.0.0")
    print("A distributed version control system with simple commands")
    print("")

def print_extended_help():
    """Print extended help with examples"""
    print_version()
    print("USAGE:")
    print("  fox <command> [options]")
    print("")
    print("COMMANDS:")
    print("  init                     Initialize a new repository")
    print("  add <files>             Add files to staging area")
    print("  add --all               Add all files in working directory")
    print("  add .                   Add all files in working directory")
    print("  commit -m <message>     Commit staged changes")
    print("  set origin <url>        Set remote repository URL")
    print("  push                    Push commits to server")
    print("  pull                    Pull commits from server") 
    print("  status                  Show repository status")
    print("  log                     Show commit history")
    print("  help, --help, -h        Show this help message")
    print("  version, --version, -v  Show version information")
    print("")
    print("EXAMPLES:")
    print("  fox init --username alice --repo-name myproject")
    print("  fox set origin 192.168.15.207:502")
    print("  fox add *.py README.md")
    print("  fox add --all")
    print("  fox add .")
    print("  fox commit -m \"Initial commit\"")
    print("  fox push")
    print("  fox status")
    print("  fox log")
    print("")
    print("GETTING STARTED:")
    print("  1. Start server: fox-server")
    print("  2. Initialize repo: fox init")
    print("  3. Set origin: fox set origin <ip:port>")
    print("  4. Add files: fox add <files>")
    print("  5. Commit: fox commit -m \"message\"")
    print("  6. Push: fox push")
    print("")
    print("For more information, visit the documentation or run 'fox <command> --help'")

def main():
    # Handle special commands first
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ['help', '--help', '-h']:
            print_extended_help()
            return
        elif cmd in ['version', '--version', '-v']:
            print_version()
            return
    
    parser = argparse.ArgumentParser(
        prog="fox",
        description="🦊 FoxNest Version Control System - Simple, distributed version control",
        epilog="Use 'fox help' for detailed help with examples",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add global options
    parser.add_argument("--version", "-v", action="store_true", help="Show version information")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands", metavar="<command>")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new repository")
    init_parser.add_argument("--username", help="Username for commits")
    init_parser.add_argument("--repo-name", help="Repository name")
    init_parser.add_argument("--server", help="Server URL (default: http://localhost:5000)")
    
    # Add command  
    add_parser = subparsers.add_parser("add", help="Add files to staging area")
    add_parser.add_argument("files", nargs="*", help="Files to add (supports wildcards)")
    add_parser.add_argument("--all", "-A", action="store_true", help="Add all files in working directory")
    
    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Commit staged changes")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_parser.add_argument("--author", help="Override commit author")
    
    # Push command
    push_parser = subparsers.add_parser("push", help="Push commits to server")
    push_parser.add_argument("--force", action="store_true", help="Force push (use with caution)")
    
    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull commits from server")
    pull_parser.add_argument("--force", action="store_true", help="Force pull (overwrite local changes)")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show repository status")
    status_parser.add_argument("--short", "-s", action="store_true", help="Show short status")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Show commit history")
    log_parser.add_argument("--oneline", action="store_true", help="Show one line per commit")
    log_parser.add_argument("-n", "--max-count", type=int, help="Limit number of commits shown")
    
    # Set command (for setting origin)
    set_parser = subparsers.add_parser("set", help="Set repository configuration")
    set_subparsers = set_parser.add_subparsers(dest="set_command", help="Set commands")
    origin_parser = set_subparsers.add_parser("origin", help="Set remote origin URL")
    origin_parser.add_argument("url", help="Remote origin URL (e.g., 192.168.15.207:502)")
    
    # Help command
    help_parser = subparsers.add_parser("help", help="Show help information")
    
    args = parser.parse_args()
    
    # Handle global version flag
    if args.version:
        print_version()
        return
    
    if not args.command:
        print_extended_help()
        return
    
    fox = FoxClient()
    
    # Handle special commands
    if args.command == "help":
        print_extended_help()
        return
    
    # Override server URL if provided
    if hasattr(args, 'server') and args.server:
        fox.server_url = args.server
    
    # Execute commands
    if args.command == "init":
        # Use environment variable for default username if available
        username = args.username
        if not username and os.getenv('FOXNEST_USER'):
            username = os.getenv('FOXNEST_USER')
        
        server_url = getattr(args, 'server', None)
        if server_url:
            fox.server_url = server_url
            
        fox.init(username, args.repo_name)
        
    elif args.command == "add":
        fox.add(args.files, add_all=args.all)
        
    elif args.command == "commit":
        author = getattr(args, 'author', None)
        if author:
            # Temporarily override author
            config = fox.load_config()
            if config:
                original_username = config.get('username')
                config['username'] = author
                fox.save_config(config)
                fox.commit(args.message)
                config['username'] = original_username
                fox.save_config(config)
            else:
                fox.commit(args.message)
        else:
            fox.commit(args.message)
            
    elif args.command == "push":
        fox.push()
        
    elif args.command == "pull":
        fox.pull()
        
    elif args.command == "status":
        if getattr(args, 'short', False):
            fox.status_short()
        else:
            fox.status()
            
    elif args.command == "set":
        if getattr(args, 'set_command', None) == "origin":
            fox.set_origin(args.url)
        else:
            print("Usage: fox set origin <url>")
            print("Example: fox set origin 192.168.15.207:502")
            
    elif args.command == "log":
        if getattr(args, 'oneline', False):
            fox.log_oneline(getattr(args, 'max_count', None))
        else:
            fox.log(getattr(args, 'max_count', None))

if __name__ == "__main__":
    main()
