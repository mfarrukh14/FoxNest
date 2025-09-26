#!/usr/bin/env python3
"""
FoxNest Server - Central repository server for the FoxNest version control system
"""

import os
import json
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
import base64

app = Flask(__name__)

# Server configuration
SERVER_ROOT = Path("/tmp/foxnest_server")  # Change this to your desired location
REPOS_DIR = SERVER_ROOT / "repositories"
USERS_DIR = SERVER_ROOT / "users"

class FoxNestServer:
    def __init__(self):
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary server directories"""
        SERVER_ROOT.mkdir(exist_ok=True)
        REPOS_DIR.mkdir(exist_ok=True)
        USERS_DIR.mkdir(exist_ok=True)
    
    def generate_repo_id(self, username, repo_name):
        """Generate unique repository ID"""
        return hashlib.md5(f"{username}_{repo_name}".encode()).hexdigest()[:16]
    
    def create_repository(self, username, repo_name):
        """Create a new repository for a user"""
        repo_id = self.generate_repo_id(username, repo_name)
        repo_path = REPOS_DIR / repo_id
        
        if repo_path.exists():
            return {"success": False, "error": "Repository already exists"}
        
        repo_path.mkdir(parents=True)
        
        # Create repository metadata
        repo_metadata = {
            "id": repo_id,
            "name": repo_name,
            "owner": username,
            "created_at": datetime.now().isoformat(),
            "commits": [],
            "head": None
        }
        
        with open(repo_path / "metadata.json", "w") as f:
            json.dump(repo_metadata, f, indent=2)
        
        # Create commits directory
        (repo_path / "commits").mkdir()
        (repo_path / "objects").mkdir()
        
        return {"success": True, "repo_id": repo_id}
    
    def get_repository(self, repo_id):
        """Get repository metadata"""
        repo_path = REPOS_DIR / repo_id
        if not repo_path.exists():
            return None
        
        with open(repo_path / "metadata.json", "r") as f:
            return json.load(f)
    
    def update_repository(self, repo_id, metadata):
        """Update repository metadata"""
        repo_path = REPOS_DIR / repo_id
        with open(repo_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    def store_commit(self, repo_id, commit_data):
        """Store a commit in the repository"""
        repo_path = REPOS_DIR / repo_id
        commit_id = commit_data["id"]
        
        # Store commit metadata
        with open(repo_path / "commits" / f"{commit_id}.json", "w") as f:
            json.dump(commit_data, f, indent=2)
        
        # Store file objects
        for file_hash, file_content in commit_data.get("files", {}).items():
            object_path = repo_path / "objects" / file_hash
            object_path.parent.mkdir(exist_ok=True)
            
            # Decode base64 content
            content = base64.b64decode(file_content.encode()).decode('utf-8')
            with open(object_path, "w") as f:
                f.write(content)
    
    def get_commit(self, repo_id, commit_id):
        """Get a specific commit"""
        repo_path = REPOS_DIR / repo_id
        commit_path = repo_path / "commits" / f"{commit_id}.json"
        
        if not commit_path.exists():
            return None
        
        with open(commit_path, "r") as f:
            return json.load(f)
    
    def get_file_content(self, repo_id, file_hash):
        """Get file content by hash"""
        repo_path = REPOS_DIR / repo_id
        object_path = repo_path / "objects" / file_hash
        
        if not object_path.exists():
            return None
        
        with open(object_path, "r") as f:
            content = f.read()
        
        return base64.b64encode(content.encode()).decode()

server = FoxNestServer()

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "FoxNest Server is running", "version": "1.0.0"})

@app.route("/api/repository/create", methods=["POST"])
def create_repository():
    """Create a new repository"""
    data = request.get_json()
    username = data.get("username")
    repo_name = data.get("repo_name")
    
    if not username or not repo_name:
        return jsonify({"success": False, "error": "Username and repo_name required"}), 400
    
    result = server.create_repository(username, repo_name)
    return jsonify(result)

@app.route("/api/repository/<repo_id>", methods=["GET"])
def get_repository(repo_id):
    """Get repository information"""
    repo = server.get_repository(repo_id)
    if not repo:
        return jsonify({"success": False, "error": "Repository not found"}), 404
    
    return jsonify({"success": True, "repository": repo})

@app.route("/api/repository/<repo_id>/push", methods=["POST"])
def push_commit(repo_id):
    """Push a commit to repository"""
    data = request.get_json()
    commit_data = data.get("commit")
    
    if not commit_data:
        return jsonify({"success": False, "error": "Commit data required"}), 400
    
    # Get repository
    repo = server.get_repository(repo_id)
    if not repo:
        return jsonify({"success": False, "error": "Repository not found"}), 404
    
    # Store the commit
    server.store_commit(repo_id, commit_data)
    
    # Update repository metadata
    repo["commits"].append(commit_data["id"])
    repo["head"] = commit_data["id"]
    server.update_repository(repo_id, repo)
    
    return jsonify({"success": True, "commit_id": commit_data["id"]})

@app.route("/api/repository/<repo_id>/pull", methods=["GET"])
def pull_commits(repo_id):
    """Pull commits from repository"""
    since_commit = request.args.get("since")
    
    repo = server.get_repository(repo_id)
    if not repo:
        return jsonify({"success": False, "error": "Repository not found"}), 404
    
    commits = []
    for commit_id in repo["commits"]:
        if since_commit and commit_id == since_commit:
            break
        
        commit = server.get_commit(repo_id, commit_id)
        if commit:
            # Include file contents
            for file_hash in commit.get("files", {}):
                content = server.get_file_content(repo_id, file_hash)
                if content:
                    commit["files"][file_hash] = content
            
            commits.append(commit)
    
    return jsonify({"success": True, "commits": commits, "head": repo.get("head")})

@app.route("/api/repository/<repo_id>/commits", methods=["GET"])
def get_commits(repo_id):
    """Get commit history"""
    repo = server.get_repository(repo_id)
    if not repo:
        return jsonify({"success": False, "error": "Repository not found"}), 404
    
    commits = []
    for commit_id in reversed(repo["commits"]):  # Most recent first
        commit = server.get_commit(repo_id, commit_id)
        if commit:
            # Don't include file content in history, just metadata
            commit_meta = {
                "id": commit["id"],
                "message": commit["message"],
                "author": commit["author"],
                "timestamp": commit["timestamp"],
                "parent": commit.get("parent"),
                "files": list(commit.get("files", {}).keys())
            }
            commits.append(commit_meta)
    
    return jsonify({"success": True, "commits": commits})

if __name__ == "__main__":
    print(f"Starting FoxNest Server...")
    print(f"Server root: {SERVER_ROOT}")
    print(f"Repositories will be stored in: {REPOS_DIR}")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
