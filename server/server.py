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
from database.models import User, Repository, Commit, CommitFile, FileObject
from database.crud import UserCRUD, RepositoryCRUD, CommitCRUD, FileObjectCRUD, ActivityCRUD

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
    create_tables()
    print("Database tables created/verified")

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
        repository = RepositoryCRUD.create_repository(
            db, request.username, request.repo_name, request.description
        )
        
        # Create activity
        ActivityCRUD.create_activity(
            db, repository.owner_id, "create_repository", 
            f"Created repository {request.repo_name}", repository.id
        )
        
        return {"success": True, "repo_id": repository.id}
    
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
        
        # Add repository_id to commit data
        commit_data = request.commit.copy()
        commit_data["repository_id"] = repo_id
        
        # Create commit
        commit = CommitCRUD.create_commit(db, commit_data)
        
        # Create activity
        ActivityCRUD.create_activity(
            db, commit.author_id, "push_commit", 
            f"Pushed commit: {commit.message[:50]}...", repo_id
        )
        
        return {"success": True, "commit_id": commit.id}
    
    except Exception as e:
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
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "is_active": user.is_active,
                    "repository_count": len(user.repositories)
                }
                for user in users
            ]
        }
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

if __name__ == "__main__":
    print(f"Starting FoxNest Server v2.0 with SQL Database...")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./foxnest.db')}")
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "5000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(app, host=host, port=port, log_level="info" if not debug else "debug")
