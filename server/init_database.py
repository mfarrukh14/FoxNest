#!/usr/bin/env python3
"""
Initialize FoxNest Database
Creates all tables from scratch with proper schema
"""

from database.database import Base, engine, create_tables
from database.models import (
    User, Repository, Commit, CommitFile, FileObject, 
    RepositoryTag, Branch, Activity, PendingCommit, UserPermission
)

def init_db():
    """Initialize database with all tables"""
    print("=" * 60)
    print("FoxNest Database Initialization")
    print("=" * 60)
    print()
    
    # Drop all tables (careful - this deletes all data!)
    print("⚠️  Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")
    print()
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully!")
    print()
    
    # List created tables
    print("Tables created:")
    tables = [
        "users (with role and team_lead_id)",
        "repositories",
        "commits",
        "commit_files",
        "file_objects",
        "repository_tags",
        "branches",
        "activities",
        "pending_commits",
        "user_permissions"
    ]
    
    for table in tables:
        print(f"  ✓ {table}")
    
    print()
    print("=" * 60)
    print("Database initialized successfully!")
    print("=" * 60)
    print()
    print("Schema includes:")
    print("  - User.role: 'developer' or 'team_lead'")
    print("  - User.team_lead_id: Reference to team lead user")
    print("  - User.email: Non-unique (allows NULL)")
    print("  - PendingCommit: For approval workflow")
    print("  - UserPermission: For repository access control")
    print()

if __name__ == "__main__":
    init_db()
