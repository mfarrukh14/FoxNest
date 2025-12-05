#!/usr/bin/env python3
"""
FoxNest Server - Central repository server for the FoxNest version control system with SQL Database
"""
 
import os
import json
import hashlib
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import base64

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn

# Database imports
from database.database import get_db, create_tables, SessionLocal, engine
from database.models import User, Repository, Commit, CommitFile, FileObject, PendingRepository
from database.crud import UserCRUD, RepositoryCRUD, CommitCRUD, FileObjectCRUD, ActivityCRUD, PendingCommitCRUD, PendingRepositoryCRUD, UserPermissionCRUD

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SERVER_ROOT = Path("/tmp/foxnest_server")  # Keep for backward compatibility
REPOS_DIR = SERVER_ROOT / "repositories"

# Pydantic models for request/response
class CreateRepositoryRequest(BaseModel):
    username: str
    repo_name: str
    description: Optional[str] = None

class PushCommitRequest(BaseModel):
    commit: Dict[str, Any]
    archive: Optional[bool] = False

class RepositoryResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    repo_id: Optional[str] = None

class CommitResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    commit_id: Optional[str] = None

class CommitsResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    commits: Optional[List[Dict[str, Any]]] = None

class RepositoriesResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    repositories: Optional[List[Dict[str, Any]]] = None

class UpdateRepositoryDetailsRequest(BaseModel):
    g1_coordinator: Optional[str] = None
    tested: Optional[bool] = None

class UpdateRepositoryDetailsResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    repository: Optional[Dict[str, Any]] = None

class CreatePermissionRequest(BaseModel):
    username: str
    repo_id: str
    permission_level: str  # read, write, team_lead, admin
    granted_by: Optional[str] = None

class ReviewCommitRequest(BaseModel):
    reviewer_username: str
    action: str  # approve or reject
    comment: Optional[str] = None

# Create FastAPI app
app = FastAPI(title="FoxNest Server", description="Central repository server for the FoxNest version control system", version="2.0.0")

# Add CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add custom middleware to handle all OPTIONS requests
@app.middleware("http")
async def cors_options_middleware(request, call_next):
    """Handle all OPTIONS requests before they reach route handlers"""
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
        return JSONResponse(content={"message": "OK"}, status_code=200, headers=headers)
    
    response = await call_next(request)
    
    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    print("=" * 60)
    print("FoxNest Server Starting...")
    print("=" * 60)
    print("Initializing database...")
    
    # Create all tables if they don't exist
    create_tables()
    
    print("✓ Database tables created/verified")
    print("  - users (with role and team_lead_id)")
    print("  - repositories")
    print("  - commits")
    print("  - commit_files")
    print("  - file_objects")
    print("  - repository_tags")
    print("  - branches")
    print("  - activities")
    print("  - pending_commits")
    print("  - pending_repositories")
    print("  - user_permissions")
    print("=" * 60)

# Helper functions
def repository_to_dict(repo: Repository) -> Dict[str, Any]:
    """Convert Repository model to dictionary"""
    return {
        "id": repo.id,
        "name": repo.name,
        "description": repo.description,
        "owner": repo.owner.username,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
        "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
        "commits": [commit.id for commit in repo.commits],
        "head": repo.head_commit_id,
        "is_archived": repo.is_archived,
        "archived_at": repo.archived_at.isoformat() if repo.archived_at else None,
        "archived_reason": repo.archived_reason,
        "language": repo.language,
        "size": repo.size_bytes,
        "is_public": repo.is_public,
        "g1_coordinator": repo.g1_coordinator,
        "tested": repo.tested,
        "instruction_manual_filename": repo.instruction_manual_filename,
        "has_instruction_manual": bool(repo.instruction_manual_path)
    }

def commit_to_dict(commit: Commit, include_files: bool = False) -> Dict[str, Any]:
    """Convert Commit model to dictionary"""
    commit_dict = {
        "id": commit.id,
        "repository_id": commit.repository_id,
        "author": commit.author.username,
        "parent": commit.parent_commit_id,
        "message": commit.message,
        "timestamp": commit.created_at.isoformat() if commit.created_at else None,
        "tree_hash": commit.tree_hash
    }
    
    if include_files:
        files = {}
        for commit_file in commit.files:
            if commit_file.file_object:
                content_b64 = base64.b64encode(commit_file.file_object.content).decode()
                files[commit_file.file_hash] = content_b64
        commit_dict["files"] = files
    else:
        commit_dict["files"] = [cf.file_path for cf in commit.files]
    
    return commit_dict

# API Endpoints
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "FoxNest Server v2.0 is running with SQL Database", "version": "2.0.0"}

@app.get("/api/")
async def api_root():
    """API root endpoint"""
    return {"status": "FoxNest API v2.0 is running", "version": "2.0.0", "endpoints": [
        "/api/repository/create",
        "/api/repository/list",
        "/api/repositories/all",
        "/api/repository/{repo_id}",
        "/api/repository/{repo_id}/push",
        "/api/repository/{repo_id}/pull",
        "/api/repository/{repo_id}/commits",
        "/api/users",
        "/api/activities"
    ]}

@app.post("/api/repository/create")
async def create_repository(request: CreateRepositoryRequest, db: Session = Depends(get_db)):
    """Create a new repository"""
    if not request.username or not request.repo_name:
        raise HTTPException(status_code=400, detail="Username and repo_name required")
    
    try:
        # Check if user exists - DO NOT auto-create
        user = UserCRUD.get_user_by_username(db, request.username)
        if not user:
            raise HTTPException(
                status_code=403, 
                detail=f"User '{request.username}' does not exist. Please contact an administrator to create your account."
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail=f"User '{request.username}' is inactive. Please contact an administrator."
            )
        
        # Determine the owner based on user role FIRST
        owner_username = request.username
        user_role = getattr(user, 'role', 'developer')
        
        if user_role == 'developer' and user.team_lead:
            # For developers, the team lead is the owner
            owner_username = user.team_lead.username
        
        # Generate repo_id with the OWNER's username (not the requester)
        repo_id = RepositoryCRUD.generate_repo_id(owner_username, request.repo_name)
        
        # Check if repository already exists (approved)
        existing_repo = RepositoryCRUD.get_repository(db, repo_id)
        if existing_repo:
            return {
                "success": True,
                "repo_id": existing_repo.id,
                "owner": existing_repo.owner.username,
                "message": "Repository already exists"
            }
        
        if user_role == 'developer' and user.team_lead:
            # Developer with team lead - team lead becomes owner
            owner_username = user.team_lead.username
            print(f"DEBUG - Repository creation: {request.username} (developer) requesting repo, owner will be team lead: {owner_username}")
            
            # Check if pending request already exists for this repo
            existing_pending = db.query(PendingRepository).filter(
                PendingRepository.repo_name == request.repo_name,
                PendingRepository.requested_by_id == user.id,
                PendingRepository.status == 'pending'
            ).first()
            
            if existing_pending:
                return {
                    "success": True,
                    "status": "pending_approval",
                    "team_lead": owner_username,
                    "pending_id": existing_pending.id,
                    "message": f"Repository creation request already pending approval from {owner_username}."
                }
            
            # For developers, create a pending repository request instead
            pending_repo = PendingRepositoryCRUD.create_pending_repository(
                db,
                repo_name=request.repo_name,
                description=request.description,
                requested_by_username=request.username,
                owner_username=owner_username
            )
            
            # Create activity for the request
            ActivityCRUD.create_activity(
                db, user.id, "request_repository", 
                f"Requested repository {request.repo_name}", None
            )
            
            return {
                "success": True,
                "status": "pending_approval",
                "team_lead": owner_username,
                "pending_id": pending_repo.id,
                "message": f"Repository creation request submitted. Awaiting approval from {owner_username}."
            }
        else:
            # Team lead or user without team lead can create directly
            print(f"DEBUG - Repository creation: {request.username} creating repo as owner (role: {user_role})")
            
            repository = RepositoryCRUD.create_repository(
                db, owner_username, request.repo_name, request.description
            )
            
            # Create activity
            ActivityCRUD.create_activity(
                db, user.id, "create_repository", 
                f"Created repository {request.repo_name}", repository.id
            )
            
            return {
                "success": True, 
                "repo_id": repository.id,
                "owner": owner_username,
                "message": None
            }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repository/list")
async def list_repositories(username: str, repo_name: Optional[str] = None, db: Session = Depends(get_db)):
    """List repositories for a user"""
    if not username:
        raise HTTPException(status_code=400, detail="Username required")
    
    try:
        if repo_name:
            # Get specific repository
            repo_id = RepositoryCRUD.generate_repo_id(username, repo_name)
            repository = RepositoryCRUD.get_repository(db, repo_id)
            repositories = [repository] if repository else []
        else:
            # Get all repositories for user
            repositories = RepositoryCRUD.get_repositories_by_user(db, username)
        
        return {
            "success": True, 
            "repositories": [repository_to_dict(repo) for repo in repositories]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repositories/all")
async def list_all_repositories(db: Session = Depends(get_db)):
    """List all repositories from all users"""
    try:
        repositories = RepositoryCRUD.get_all_repositories(db)
        return {
            "success": True, 
            "repositories": [repository_to_dict(repo) for repo in repositories]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repository/{repo_id}")
async def get_repository(repo_id: str, db: Session = Depends(get_db)):
    """Get repository information"""
    repository = RepositoryCRUD.get_repository(db, repo_id)
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return {"success": True, "repository": repository_to_dict(repository)}

@app.delete("/api/repository/{repo_id}")
async def delete_repository(repo_id: str, db: Session = Depends(get_db)):
    """Delete a repository permanently"""
    try:
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        repo_name = repository.name
        owner_name = repository.owner.username
        
        # Delete the repository
        RepositoryCRUD.delete_repository(db, repo_id)
        
        return {
            "success": True,
            "message": f"Repository '{repo_name}' owned by '{owner_name}' has been permanently deleted"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/repository/{repo_id}/push")
async def push_commit(repo_id: str, request: PushCommitRequest, db: Session = Depends(get_db)):
    """Push a commit to repository"""
    if not request.commit:
        raise HTTPException(status_code=400, detail="Commit data required")
    
    try:
        # Ensure repository exists
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Get the author username from commit data
        author_username = request.commit.get("author")
        if not author_username:
            raise HTTPException(status_code=400, detail="Commit author required")
        
        # Check if repository is archived and user is trying regular push
        if repository.is_archived and not request.archive:
            raise HTTPException(
                status_code=400, 
                detail="Repository is archived. Use 'fox push --archive' to push to archived repository."
            )
        
        # Get the user to check their role
        user = UserCRUD.get_user_by_username(db, author_username)
        if not user:
            raise HTTPException(
                status_code=403,
                detail=f"User '{author_username}' does not exist. Please contact an administrator to create your account."
            )
        
        # Check basic permissions (owner or has permission)
        is_owner = repository.owner.username == author_username
        has_write_permission = UserPermissionCRUD.has_permission(db, author_username, repo_id, 'write')
        
        if not is_owner and not has_write_permission:
            raise HTTPException(
                status_code=403, 
                detail=f"User '{author_username}' does not have permission to push to this repository. Please contact the repository owner or an administrator."
            )
        
        # Add repository_id to commit data
        commit_data = request.commit.copy()
        commit_data["repository_id"] = repo_id
        
        # Check if user role is 'developer' - developers always need approval regardless of ownership or permissions
        # Team leads can push directly
        user_role = getattr(user, 'role', 'developer')  # Default to developer if role not set
        user_is_developer = user_role == 'developer'
        
        # Debug logging
        print(f"DEBUG - Push from {author_username}:")
        print(f"  - User role: {user_role}")
        print(f"  - Is developer: {user_is_developer}")
        print(f"  - Is owner: {is_owner}")
        
        # If user is a developer, they ALWAYS need approval, regardless of being owner
        if user_is_developer:
            # Developer - create pending commit for approval
            pending_commit = PendingCommitCRUD.create_pending_commit(db, commit_data)
            
            # Get team lead info
            team_lead_name = None
            if user.team_lead:
                team_lead_name = user.team_lead.username
            
            # Create activity
            ActivityCRUD.create_activity(
                db, user.id, "pending_commit", 
                f"Created pending commit: {pending_commit.message[:50]}...", repo_id
            )
            
            return {
                "success": True, 
                "commit_id": pending_commit.id, 
                "status": "pending_approval",
                "team_lead": team_lead_name,
                "message": f"Your commit has been submitted for review by {team_lead_name or 'the team lead'}."
            }
        else:
            # Team lead or other role - check permissions for direct push
            is_team_lead = UserPermissionCRUD.has_permission(db, author_username, repo_id, 'team_lead')
            
            print(f"  - Has team_lead permission: {is_team_lead}")
            
            if not is_team_lead and not is_owner:
                raise HTTPException(
                    status_code=403,
                    detail=f"User '{author_username}' does not have team lead permission to push directly."
                )
            
            # Team lead or owner with non-developer role can push directly
            commit = CommitCRUD.create_commit(db, commit_data)
            
            # Create activity
            ActivityCRUD.create_activity(
                db, user.id, "push_commit", 
                f"Pushed commit: {commit.message[:50]}...", repo_id
            )
            
            # Handle archiving based on flag
            if request.archive:
                RepositoryCRUD.archive_repository(db, repo_id, reason="Archived via push --archive command")
            
            return {"success": True, "commit_id": commit.id, "status": "merged"}
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log and raise other exceptions
        import traceback
        print(f"Error in push_commit: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repository/{repo_id}/pull")
async def pull_commits(repo_id: str, since_commit: Optional[str] = None, db: Session = Depends(get_db)):
    """Pull commits from repository"""
    repository = RepositoryCRUD.get_repository(db, repo_id)
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    try:
        commits = CommitCRUD.get_commits_by_repository(db, repo_id)
        
        # Filter commits if since_commit is provided
        if since_commit:
            filtered_commits = []
            for commit in commits:
                if commit.id == since_commit:
                    break
                filtered_commits.append(commit)
            commits = filtered_commits
        
        return {
            "success": True, 
            "commits": [commit_to_dict(commit, include_files=True) for commit in commits],
            "head": repository.head_commit_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repository/{repo_id}/commits")
async def get_commits(repo_id: str, full: bool = False, db: Session = Depends(get_db)):
    """Get commit history"""
    repository = RepositoryCRUD.get_repository(db, repo_id)
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    try:
        commits = CommitCRUD.get_commits_by_repository(db, repo_id)
        return {
            "success": True, 
            "commits": [commit_to_dict(commit, include_files=full) for commit in commits]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repository/{repo_id}/files")
async def get_repository_files(repo_id: str, db: Session = Depends(get_db)):
    """Get all files in repository from latest commit"""
    repository = RepositoryCRUD.get_repository(db, repo_id)
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    try:
        # Get the latest commit
        if not repository.head_commit_id:
            return {
                "success": True,
                "files": {},
                "folders": [],
                "message": "Repository is empty"
            }
        
        head_commit = db.query(Commit).filter(Commit.id == repository.head_commit_id).first()
        if not head_commit:
            return {
                "success": True,
                "files": {},
                "folders": [],
                "message": "No commits found"
            }
        
        # Get all files from the head commit
        files_dict = {}
        folders_set = set()
        
        for commit_file in head_commit.files:
            file_path = commit_file.file_path
            
            # Extract folder structure
            path_parts = file_path.split('/')
            for i in range(len(path_parts) - 1):
                folder_path = '/'.join(path_parts[:i+1])
                folders_set.add(folder_path)
            
            # Get file content
            if commit_file.file_object:
                try:
                    # Try to decode as text
                    content = commit_file.file_object.content.decode('utf-8')
                    is_binary = False
                except UnicodeDecodeError:
                    # Binary file, encode to base64
                    content = base64.b64encode(commit_file.file_object.content).decode('utf-8')
                    is_binary = True
                
                files_dict[file_path] = {
                    "content": content,
                    "is_binary": is_binary,
                    "size": commit_file.file_size,
                    "hash": commit_file.file_hash,
                    "mime_type": commit_file.file_object.mime_type
                }
        
        return {
            "success": True,
            "files": files_dict,
            "folders": sorted(list(folders_set)),
            "commit_id": head_commit.id,
            "commit_message": head_commit.message
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/admin/create-sample-data")
async def create_sample_data(db: Session = Depends(get_db)):
    """Create sample repositories for testing (development only)"""
    try:
        sample_repos = [
            {"username": "john_doe", "repo_name": "legacy-system", "description": "Legacy system components and utilities"},
            {"username": "jane_smith", "repo_name": "old-mobile-prototype", "description": "Initial mobile app prototype"},
            {"username": "mike_wilson", "repo_name": "experimental-ui", "description": "Experimental UI components library"},
            {"username": "sarah_connor", "repo_name": "temp-data-migration", "description": "Temporary scripts for data migration"},
        ]
        
        created_repos = []
        for repo_data in sample_repos:
            try:
                repository = RepositoryCRUD.create_repository(
                    db, repo_data["username"], repo_data["repo_name"], repo_data["description"]
                )
                created_repos.append(repository.id)
            except ValueError:
                # Repository already exists, skip
                repo_id = RepositoryCRUD.generate_repo_id(repo_data["username"], repo_data["repo_name"])
                created_repos.append(repo_id)
        
        return {"success": True, "created_repositories": created_repos}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/users")
async def list_users(db: Session = Depends(get_db)):
    """List all users"""
    try:
        users = db.query(User).all()
        return {
            "success": True,
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role if hasattr(user, 'role') else 'developer',
                    "team_lead_id": user.team_lead_id if hasattr(user, 'team_lead_id') else None,
                    "team_lead_name": user.team_lead.username if hasattr(user, 'team_lead') and user.team_lead else None,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "is_active": user.is_active,
                    "repository_count": len(user.repositories)
                }
                for user in users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/users/create")
async def create_user(request: dict, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        username = request.get("username")
        email = request.get("email")
        full_name = request.get("full_name")
        role = request.get("role", "developer")  # Default to 'developer'
        team_lead_id = request.get("team_lead_id")  # ID of the team lead (for developers)
        
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")
        
        if role not in ['developer', 'team_lead']:
            raise HTTPException(status_code=400, detail="Role must be 'developer' or 'team_lead'")
        
        # If role is developer and team_lead_id is provided, validate the team lead exists
        if role == 'developer' and team_lead_id:
            team_lead = UserCRUD.get_user_by_id(db, team_lead_id)
            if not team_lead:
                raise HTTPException(status_code=400, detail="Team lead user not found")
            if team_lead.role != 'team_lead':
                raise HTTPException(status_code=400, detail="Selected user is not a team lead")
        
        # Check if user already exists
        existing_user = UserCRUD.get_user_by_username(db, username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        user = UserCRUD.create_user(db, username, email, full_name, role, team_lead_id)
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "team_lead_id": user.team_lead_id,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/users/{username}")
async def update_user(username: str, request: dict, db: Session = Depends(get_db)):
    """Update user information"""
    try:
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if "email" in request:
            user.email = request["email"]
        if "full_name" in request:
            user.full_name = request["full_name"]
        if "is_active" in request:
            user.is_active = request["is_active"]
        
        db.commit()
        db.refresh(user)
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/users/{username}")
async def delete_user(username: str, db: Session = Depends(get_db)):
    """Delete a user"""
    try:
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user owns any repositories
        if len(user.repositories) > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete user who owns repositories. User owns {len(user.repositories)} repository(ies)."
            )
        
        db.delete(user)
        db.commit()
        
        return {
            "success": True,
            "message": f"User {username} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/activities")
async def get_recent_activities(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent activities"""
    try:
        activities = ActivityCRUD.get_recent_activities(db, limit)
        return {
            "success": True,
            "activities": [
                {
                    "id": activity.id,
                    "user": activity.user.username,
                    "repository": activity.repository.name if activity.repository else None,
                    "activity_type": activity.activity_type,
                    "description": activity.description,
                    "created_at": activity.created_at.isoformat() if activity.created_at else None
                }
                for activity in activities
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/repository/{repo_id}/details")
async def update_repository_details(repo_id: str, request: UpdateRepositoryDetailsRequest, db: Session = Depends(get_db)):
    """Update repository G1 coordinator and testing status"""
    try:
        repository = RepositoryCRUD.update_repository_details(
            db, 
            repo_id, 
            g1_coordinator=request.g1_coordinator,
            tested=request.tested
        )
        
        return UpdateRepositoryDetailsResponse(
            success=True,
            repository={
                "id": repository.id,
                "name": repository.name,
                "g1_coordinator": repository.g1_coordinator,
                "tested": repository.tested,
                "instruction_manual_filename": repository.instruction_manual_filename
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/repository/{repo_id}/upload-manual")
async def upload_instruction_manual(
    repo_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload instruction manual PDF for a repository"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("/tmp/foxnest_uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{repo_id}_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update repository with file path
        repository = RepositoryCRUD.update_repository_details(
            db,
            repo_id,
            instruction_manual_path=str(file_path),
            instruction_manual_filename=file.filename
        )
        
        return {
            "success": True,
            "message": "Instruction manual uploaded successfully",
            "filename": file.filename,
            "repository": {
                "id": repository.id,
                "name": repository.name,
                "instruction_manual_filename": repository.instruction_manual_filename
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repository/{repo_id}/download-manual")
async def download_instruction_manual(repo_id: str, db: Session = Depends(get_db)):
    """Download instruction manual PDF for a repository"""
    try:
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        if not repository.instruction_manual_path:
            raise HTTPException(status_code=404, detail="No instruction manual found for this repository")
        
        file_path = Path(repository.instruction_manual_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Instruction manual file not found on server")
        
        return FileResponse(
            path=str(file_path),
            filename=repository.instruction_manual_filename or "instruction_manual.pdf",
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# User Permissions Management Endpoints
@app.post("/api/permissions/create")
async def create_permission(request: CreatePermissionRequest, db: Session = Depends(get_db)):
    """Grant a user permission to a repository"""
    try:
        permission = UserPermissionCRUD.create_permission(
            db,
            request.username,
            request.repo_id,
            request.permission_level,
            request.granted_by
        )
        
        return {
            "success": True,
            "permission": {
                "user": permission.user.username,
                "repository": permission.repository.name,
                "permission_level": permission.permission_level,
                "granted_at": permission.granted_at.isoformat() if permission.granted_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/permissions/update")
async def update_permission(request: CreatePermissionRequest, db: Session = Depends(get_db)):
    """Update a user's permission level for a repository"""
    try:
        permission = UserPermissionCRUD.create_permission(
            db,
            request.username,
            request.repo_id,
            request.permission_level,
            request.granted_by
        )
        
        return {
            "success": True,
            "permission": {
                "user": permission.user.username,
                "repository": permission.repository.name,
                "permission_level": permission.permission_level,
                "granted_at": permission.granted_at.isoformat() if permission.granted_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/permissions/repository/{repo_id}")
async def get_repository_permissions(repo_id: str, db: Session = Depends(get_db)):
    """Get all permissions for a repository"""
    try:
        permissions = UserPermissionCRUD.get_repository_permissions(db, repo_id)
        return {
            "success": True,
            "permissions": [
                {
                    "user": p.user.username,
                    "permission_level": p.permission_level,
                    "granted_by": p.granted_by.username if p.granted_by else None,
                    "granted_at": p.granted_at.isoformat() if p.granted_at else None
                }
                for p in permissions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/permissions/user/{username}")
async def get_user_permissions(username: str, db: Session = Depends(get_db)):
    """Get all permissions for a user"""
    try:
        permissions = UserPermissionCRUD.get_user_permissions(db, username)
        return {
            "success": True,
            "permissions": [
                {
                    "repository_id": p.repository.id,
                    "repository_name": p.repository.name,
                    "permission_level": p.permission_level,
                    "granted_by": p.granted_by.username if p.granted_by else None,
                    "granted_at": p.granted_at.isoformat() if p.granted_at else None
                }
                for p in permissions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/permissions/revoke")
async def revoke_permission(username: str, repo_id: str, db: Session = Depends(get_db)):
    """Revoke a user's permission to a repository"""
    try:
        success = UserPermissionCRUD.revoke_permission(db, username, repo_id)
        if success:
            return {"success": True, "message": "Permission revoked successfully"}
        else:
            raise HTTPException(status_code=404, detail="Permission not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Pending Commits Management Endpoints
@app.get("/api/pending-commits")
async def get_all_pending_commits(
    status: str = 'pending', 
    team_lead_username: str = None,
    db: Session = Depends(get_db)
):
    """Get all pending commits across all repositories, optionally filtered by team lead"""
    try:
        pending_commits = PendingCommitCRUD.get_all_pending_commits(db, status)
        
        # Filter by team lead if specified
        if team_lead_username:
            team_lead = UserCRUD.get_user_by_username(db, team_lead_username)
            if team_lead:
                # Only show commits from developers assigned to this team lead
                pending_commits = [
                    pc for pc in pending_commits 
                    if pc.author.team_lead_id == team_lead.id
                ]
        
        return {
            "success": True,
            "pending_commits": [
                {
                    "id": pc.id,
                    "repository_id": pc.repository.id,
                    "repository_name": pc.repository.name,
                    "author": pc.author.username,
                    "author_full_name": pc.author.full_name,
                    "team_lead_name": pc.author.team_lead.username if pc.author.team_lead else None,
                    "message": pc.message,
                    "created_at": pc.created_at.isoformat() if pc.created_at else None,
                    "status": pc.status,
                    "reviewed_by": pc.reviewer.username if pc.reviewer else None,
                    "reviewed_at": pc.reviewed_at.isoformat() if pc.reviewed_at else None,
                    "review_comment": pc.review_comment
                }
                for pc in pending_commits
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/repository/{repo_id}/pending-commits")
async def get_repository_pending_commits(repo_id: str, status: str = None, db: Session = Depends(get_db)):
    """Get pending commits for a specific repository"""
    try:
        pending_commits = PendingCommitCRUD.get_pending_commits_by_repository(db, repo_id, status)
        return {
            "success": True,
            "pending_commits": [
                {
                    "id": pc.id,
                    "author": pc.author.username,
                    "message": pc.message,
                    "created_at": pc.created_at.isoformat() if pc.created_at else None,
                    "status": pc.status,
                    "reviewed_by": pc.reviewer.username if pc.reviewer else None,
                    "reviewed_at": pc.reviewed_at.isoformat() if pc.reviewed_at else None,
                    "review_comment": pc.review_comment
                }
                for pc in pending_commits
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/pending-commits/{commit_id}/review")
async def review_pending_commit(commit_id: str, request: ReviewCommitRequest, db: Session = Depends(get_db)):
    """Approve or reject a pending commit"""
    try:
        if request.action == "approve":
            pending, commit = PendingCommitCRUD.approve_pending_commit(
                db, commit_id, request.reviewer_username, request.comment
            )
            return {
                "success": True,
                "message": "Commit approved and merged",
                "commit_id": commit.id,
                "status": "approved"
            }
        elif request.action == "reject":
            pending = PendingCommitCRUD.reject_pending_commit(
                db, commit_id, request.reviewer_username, request.comment
            )
            return {
                "success": True,
                "message": "Commit rejected",
                "status": "rejected"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/pending-repositories")
async def get_all_pending_repositories(
    status: str = 'pending', 
    team_lead_username: str = None,
    db: Session = Depends(get_db)
):
    """Get all pending repository requests, optionally filtered by team lead"""
    try:
        if team_lead_username:
            pending_repos = PendingRepositoryCRUD.get_pending_repositories_by_team_lead(db, team_lead_username, status)
        else:
            pending_repos = PendingRepositoryCRUD.get_all_pending_repositories(db, status)
        
        return {
            "success": True,
            "pending_repositories": [
                {
                    "id": pr.id,
                    "repo_name": pr.repo_name,
                    "description": pr.description,
                    "requested_by": pr.requested_by.username,
                    "requested_by_full_name": pr.requested_by.full_name,
                    "owner": pr.owner.username,
                    "owner_full_name": pr.owner.full_name,
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "status": pr.status,
                    "reviewed_by": pr.reviewer.username if pr.reviewer else None,
                    "reviewed_at": pr.reviewed_at.isoformat() if pr.reviewed_at else None,
                    "review_comment": pr.review_comment
                }
                for pr in pending_repos
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/pending-repositories/{pending_id}/review")
async def review_pending_repository(pending_id: int, request: ReviewCommitRequest, db: Session = Depends(get_db)):
    """Approve or reject a pending repository"""
    try:
        if request.action == "approve":
            pending, repository = PendingRepositoryCRUD.approve_pending_repository(
                db, pending_id, request.reviewer_username, request.comment
            )
            return {
                "success": True,
                "message": "Repository approved and created",
                "repo_id": repository.id,
                "status": "approved"
            }
        elif request.action == "reject":
            pending = PendingRepositoryCRUD.reject_pending_repository(
                db, pending_id, request.reviewer_username, request.comment
            )
            return {
                "success": True,
                "message": "Repository request rejected",
                "status": "rejected"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    print(f"Starting FoxNest Server v2.0 with SQL Database...")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./foxnest.db')}")
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "5000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(app, host=host, port=port, log_level="info" if not debug else "debug")

