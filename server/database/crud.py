from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from database.models import User, Repository, Commit, CommitFile, FileObject, RepositoryTag, Branch, Activity, PendingCommit, PendingRepository, UserPermission
from typing import List, Optional
from datetime import datetime
import hashlib

class UserCRUD:
    @staticmethod
    def create_user(db: Session, username: str, email: str = None, full_name: str = None, role: str = 'developer', team_lead_id: int = None) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            team_lead_id=team_lead_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_or_create_user(db: Session, username: str, email: str = None, full_name: str = None) -> User:
        """Get existing user or create new one"""
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            user = UserCRUD.create_user(db, username, email, full_name)
        return user

class RepositoryCRUD:
    @staticmethod
    def generate_repo_id(username: str, repo_name: str) -> str:
        """Generate unique repository ID"""
        return hashlib.md5(f"{username}_{repo_name}".encode()).hexdigest()[:16]
    
    @staticmethod
    def create_repository(db: Session, username: str, repo_name: str, description: str = None) -> Repository:
        """Create a new repository"""
        # Get user - DO NOT auto-create
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            raise ValueError(f"User '{username}' does not exist")
        
        repo_id = RepositoryCRUD.generate_repo_id(username, repo_name)
        
        # Check if repository already exists
        existing_repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if existing_repo:
            raise ValueError("Repository already exists")
        
        repository = Repository(
            id=repo_id,
            name=repo_name,
            description=description,
            owner_id=user.id
        )
        
        db.add(repository)
        db.commit()
        db.refresh(repository)
        
        # Create default branch
        BranchCRUD.create_branch(db, repo_id, "main", is_default=True)
        
        return repository
    
    @staticmethod
    def get_repository(db: Session, repo_id: str) -> Optional[Repository]:
        """Get repository by ID"""
        return db.query(Repository).filter(Repository.id == repo_id).first()
    
    @staticmethod
    def get_repositories_by_user(db: Session, username: str) -> List[Repository]:
        """Get all repositories for a user"""
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            return []
        return db.query(Repository).filter(Repository.owner_id == user.id).all()
    
    @staticmethod
    def get_all_repositories(db: Session) -> List[Repository]:
        """Get all repositories"""
        return db.query(Repository).all()
    
    @staticmethod
    def archive_repository(db: Session, repo_id: str, reason: str = None) -> Repository:
        """Archive a repository"""
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise ValueError("Repository not found")
        
        repository.is_archived = True
        repository.archived_at = datetime.utcnow()
        repository.archived_reason = reason
        
        db.commit()
        db.refresh(repository)
        return repository
    
    @staticmethod
    def unarchive_repository(db: Session, repo_id: str) -> Repository:
        """Unarchive a repository (move back to active repositories)"""
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise ValueError("Repository not found")
        
        repository.is_archived = False
        repository.archived_at = None
        repository.archived_reason = None
        
        db.commit()
        db.refresh(repository)
        return repository
    
    @staticmethod
    def delete_repository(db: Session, repo_id: str) -> bool:
        """Delete a repository and all associated data"""
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise ValueError("Repository not found")
        
        # Delete all associated data (cascade should handle this, but being explicit)
        # Delete commits, commit files, branches, tags, activities, permissions, pending commits
        from database.models import Commit, CommitFile, Branch, RepositoryTag, Activity, PendingCommit, UserPermission
        
        # Delete pending commits
        db.query(PendingCommit).filter(PendingCommit.repository_id == repo_id).delete()
        
        # Delete user permissions
        db.query(UserPermission).filter(UserPermission.repository_id == repo_id).delete()
        
        # Delete activities
        db.query(Activity).filter(Activity.repository_id == repo_id).delete()
        
        # Delete repository tags
        db.query(RepositoryTag).filter(RepositoryTag.repository_id == repo_id).delete()
        
        # Delete branches
        db.query(Branch).filter(Branch.repository_id == repo_id).delete()
        
        # Delete commit files for commits in this repository
        commit_ids = [c.id for c in db.query(Commit).filter(Commit.repository_id == repo_id).all()]
        if commit_ids:
            db.query(CommitFile).filter(CommitFile.commit_id.in_(commit_ids)).delete(synchronize_session=False)
        
        # Delete commits
        db.query(Commit).filter(Commit.repository_id == repo_id).delete()
        
        # Finally delete the repository itself
        db.delete(repository)
        db.commit()
        
        return True
    
    @staticmethod
    def update_repository_details(db: Session, repo_id: str, g1_coordinator: str = None, 
                                tested: bool = None, instruction_manual_path: str = None, 
                                instruction_manual_filename: str = None) -> Repository:
        """Update repository G1 coordinator, testing status, and instruction manual"""
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise ValueError("Repository not found")
        
        if g1_coordinator is not None:
            repository.g1_coordinator = g1_coordinator
        if tested is not None:
            repository.tested = tested
        if instruction_manual_path is not None:
            repository.instruction_manual_path = instruction_manual_path
        if instruction_manual_filename is not None:
            repository.instruction_manual_filename = instruction_manual_filename
        
        db.commit()
        db.refresh(repository)
        return repository

class CommitCRUD:
    @staticmethod
    def create_commit(db: Session, commit_data: dict) -> Commit:
        """Create a new commit"""
        repository = RepositoryCRUD.get_repository(db, commit_data["repository_id"])
        if not repository:
            raise ValueError("Repository not found")
        
        author = UserCRUD.get_user_by_username(db, commit_data["author"])
        if not author:
            raise ValueError(f"User '{commit_data['author']}' does not exist. Please contact an administrator to create your account.")
        
        commit = Commit(
            id=commit_data["id"],
            repository_id=commit_data["repository_id"],
            author_id=author.id,
            parent_commit_id=commit_data.get("parent"),
            message=commit_data["message"],
            tree_hash=commit_data.get("tree_hash")
        )
        
        db.add(commit)
        db.flush()  # Get the commit ID without committing
        
        # Store files
        for file_path, file_content in commit_data.get("files", {}).items():
            FileObjectCRUD.store_file_and_create_commit_file(
                db, commit.id, file_path, file_content
            )
        
        # Update repository head
        repository.head_commit_id = commit.id
        repository.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(commit)
        return commit
    
    @staticmethod
    def get_commit(db: Session, commit_id: str) -> Optional[Commit]:
        """Get commit by ID"""
        return db.query(Commit).filter(Commit.id == commit_id).first()
    
    @staticmethod
    def get_commits_by_repository(db: Session, repo_id: str, limit: int = 50) -> List[Commit]:
        """Get commits for a repository"""
        return db.query(Commit).filter(
            Commit.repository_id == repo_id
        ).order_by(desc(Commit.created_at)).limit(limit).all()

class FileObjectCRUD:
    @staticmethod
    def calculate_file_hash(content: bytes) -> str:
        """Calculate SHA-1 hash of file content"""
        return hashlib.sha1(content).hexdigest()
    
    @staticmethod
    def store_file_object(db: Session, content: bytes, mime_type: str = None) -> FileObject:
        """Store a file object"""
        file_hash = FileObjectCRUD.calculate_file_hash(content)
        
        # Check if file already exists
        existing_file = db.query(FileObject).filter(FileObject.hash == file_hash).first()
        if existing_file:
            return existing_file
        
        file_object = FileObject(
            hash=file_hash,
            content=content,
            size=len(content),
            mime_type=mime_type
        )
        
        db.add(file_object)
        db.commit()
        db.refresh(file_object)
        return file_object
    
    @staticmethod
    def store_file_and_create_commit_file(db: Session, commit_id: str, file_path: str, file_content: str):
        """Store file content and create commit file entry"""
        import base64
        
        # Decode base64 content
        content = base64.b64decode(file_content.encode())
        
        # Store file object
        file_object = FileObjectCRUD.store_file_object(db, content)
        
        # Create commit file entry
        commit_file = CommitFile(
            commit_id=commit_id,
            file_path=file_path,
            file_hash=file_object.hash,
            file_size=file_object.size
        )
        
        db.add(commit_file)
        return commit_file

class BranchCRUD:
    @staticmethod
    def create_branch(db: Session, repo_id: str, branch_name: str, head_commit_id: str = None, is_default: bool = False) -> Branch:
        """Create a new branch"""
        branch = Branch(
            repository_id=repo_id,
            name=branch_name,
            head_commit_id=head_commit_id,
            is_default=is_default
        )
        
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch
    
    @staticmethod
    def get_branches_by_repository(db: Session, repo_id: str) -> List[Branch]:
        """Get all branches for a repository"""
        return db.query(Branch).filter(Branch.repository_id == repo_id).all()

class ActivityCRUD:
    @staticmethod
    def create_activity(db: Session, user_id: int, activity_type: str, description: str = None, repository_id: str = None):
        """Create an activity record"""
        activity = Activity(
            user_id=user_id,
            repository_id=repository_id,
            activity_type=activity_type,
            description=description
        )
        
        db.add(activity)
        db.commit()
        return activity
    
    @staticmethod
    def get_recent_activities(db: Session, limit: int = 20) -> List[Activity]:
        """Get recent activities"""
        return db.query(Activity).order_by(desc(Activity.created_at)).limit(limit).all()

class PendingCommitCRUD:
    @staticmethod
    def create_pending_commit(db: Session, commit_data: dict) -> PendingCommit:
        """Create a new pending commit awaiting approval"""
        
        repository = RepositoryCRUD.get_repository(db, commit_data["repository_id"])
        if not repository:
            raise ValueError("Repository not found")
        
        author = UserCRUD.get_user_by_username(db, commit_data["author"])
        if not author:
            raise ValueError(f"User '{commit_data['author']}' does not exist. Please contact an administrator to create your account.")
        
        # Store files data as JSON
        import json
        files_json = json.dumps(commit_data.get("files", {}))
        
        pending_commit = PendingCommit(
            id=commit_data["id"],
            repository_id=commit_data["repository_id"],
            author_id=author.id,
            parent_commit_id=commit_data.get("parent"),
            message=commit_data["message"],
            tree_hash=commit_data.get("tree_hash"),
            files_data=files_json,
            status='pending'
        )
        
        db.add(pending_commit)
        db.commit()
        db.refresh(pending_commit)
        return pending_commit
    
    @staticmethod
    def get_pending_commit(db: Session, commit_id: str):
        """Get pending commit by ID"""
        return db.query(PendingCommit).filter(PendingCommit.id == commit_id).first()
    
    @staticmethod
    def get_pending_commits_by_repository(db: Session, repo_id: str, status: str = None):
        """Get pending commits for a repository"""
        query = db.query(PendingCommit).filter(PendingCommit.repository_id == repo_id)
        if status:
            query = query.filter(PendingCommit.status == status)
        return query.order_by(desc(PendingCommit.created_at)).all()
    
    @staticmethod
    def get_all_pending_commits(db: Session, status: str = 'pending'):
        """Get all pending commits across all repositories"""
        query = db.query(PendingCommit)
        if status:
            query = query.filter(PendingCommit.status == status)
        return query.order_by(desc(PendingCommit.created_at)).all()
    
    @staticmethod
    def approve_pending_commit(db: Session, commit_id: str, reviewer_username: str, comment: str = None):
        """Approve a pending commit and convert it to a real commit"""
        import json
        
        pending = PendingCommitCRUD.get_pending_commit(db, commit_id)
        if not pending:
            raise ValueError("Pending commit not found")
        
        if pending.status != 'pending':
            raise ValueError(f"Commit is already {pending.status}")
        
        reviewer = UserCRUD.get_user_by_username(db, reviewer_username)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        # Update pending commit status
        pending.status = 'approved'
        pending.reviewed_by_id = reviewer.id
        pending.reviewed_at = datetime.utcnow()
        pending.review_comment = comment
        
        # Create actual commit
        files_data = json.loads(pending.files_data) if pending.files_data else {}
        commit_data = {
            "id": pending.id,
            "repository_id": pending.repository_id,
            "author": pending.author.username,
            "parent": pending.parent_commit_id,
            "message": pending.message,
            "tree_hash": pending.tree_hash,
            "files": files_data
        }
        
        commit = CommitCRUD.create_commit(db, commit_data)
        
        db.commit()
        db.refresh(pending)
        return pending, commit
    
    @staticmethod
    def reject_pending_commit(db: Session, commit_id: str, reviewer_username: str, comment: str = None):
        """Reject a pending commit"""
        
        pending = PendingCommitCRUD.get_pending_commit(db, commit_id)
        if not pending:
            raise ValueError("Pending commit not found")
        
        if pending.status != 'pending':
            raise ValueError(f"Commit is already {pending.status}")
        
        reviewer = UserCRUD.get_user_by_username(db, reviewer_username)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        pending.status = 'rejected'
        pending.reviewed_by_id = reviewer.id
        pending.reviewed_at = datetime.utcnow()
        pending.review_comment = comment
        
        db.commit()
        db.refresh(pending)
        return pending

class UserPermissionCRUD:
    @staticmethod
    def create_permission(db: Session, username: str, repo_id: str, permission_level: str, granted_by_username: str = None):
        """Grant a user permission to a repository"""
        
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            raise ValueError(f"User {username} not found")
        
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if not repository:
            raise ValueError("Repository not found")
        
        granted_by = None
        if granted_by_username:
            granted_by = UserCRUD.get_user_by_username(db, granted_by_username)
        
        # Check if permission already exists
        existing = db.query(UserPermission).filter(
            and_(UserPermission.user_id == user.id, UserPermission.repository_id == repo_id)
        ).first()
        
        if existing:
            # Update existing permission
            existing.permission_level = permission_level
            existing.granted_by_id = granted_by.id if granted_by else None
            existing.granted_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        
        permission = UserPermission(
            user_id=user.id,
            repository_id=repo_id,
            permission_level=permission_level,
            granted_by_id=granted_by.id if granted_by else None
        )
        
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    
    @staticmethod
    def get_user_permission(db: Session, username: str, repo_id: str):
        """Get a user's permission for a repository"""
        
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            return None
        
        return db.query(UserPermission).filter(
            and_(UserPermission.user_id == user.id, UserPermission.repository_id == repo_id)
        ).first()
    
    @staticmethod
    def get_repository_permissions(db: Session, repo_id: str):
        """Get all permissions for a repository"""
        return db.query(UserPermission).filter(UserPermission.repository_id == repo_id).all()
    
    @staticmethod
    def get_user_permissions(db: Session, username: str):
        """Get all permissions for a user"""
        
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            return []
        
        return db.query(UserPermission).filter(UserPermission.user_id == user.id).all()
    
    @staticmethod
    def revoke_permission(db: Session, username: str, repo_id: str):
        """Revoke a user's permission to a repository"""
        
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            raise ValueError(f"User {username} not found")
        
        permission = db.query(UserPermission).filter(
            and_(UserPermission.user_id == user.id, UserPermission.repository_id == repo_id)
        ).first()
        
        if permission:
            db.delete(permission)
            db.commit()
            return True
        return False
    
    @staticmethod
    def has_permission(db: Session, username: str, repo_id: str, required_level: str = 'write') -> bool:
        """Check if a user has permission to access a repository"""
        # Define permission hierarchy
        permission_hierarchy = {
            'read': 0,
            'write': 1,
            'team_lead': 2,
            'admin': 3
        }
        
        # Repository owner always has admin access
        repository = RepositoryCRUD.get_repository(db, repo_id)
        if repository and repository.owner.username == username:
            return True
        
        # Check explicit permissions
        permission = UserPermissionCRUD.get_user_permission(db, username, repo_id)
        if not permission:
            return False
        
        required_rank = permission_hierarchy.get(required_level, 1)
        user_rank = permission_hierarchy.get(permission.permission_level, 0)
        
        return user_rank >= required_rank

class PendingRepositoryCRUD:
    @staticmethod
    def create_pending_repository(db: Session, repo_name: str, description: str, requested_by_username: str, owner_username: str):
        """Create a new pending repository awaiting approval"""
        
        requested_by = UserCRUD.get_user_by_username(db, requested_by_username)
        if not requested_by:
            raise ValueError(f"User '{requested_by_username}' not found")
        
        owner = UserCRUD.get_user_by_username(db, owner_username)
        if not owner:
            raise ValueError(f"Owner '{owner_username}' not found")
        
        pending_repo = PendingRepository(
            repo_name=repo_name,
            description=description,
            requested_by_id=requested_by.id,
            owner_id=owner.id,
            status='pending'
        )
        
        db.add(pending_repo)
        db.commit()
        db.refresh(pending_repo)
        return pending_repo
    
    @staticmethod
    def get_pending_repository(db: Session, pending_id: int):
        """Get pending repository by ID"""
        return db.query(PendingRepository).filter(PendingRepository.id == pending_id).first()
    
    @staticmethod
    def get_all_pending_repositories(db: Session, status: str = 'pending'):
        """Get all pending repositories"""
        query = db.query(PendingRepository)
        if status:
            query = query.filter(PendingRepository.status == status)
        return query.order_by(desc(PendingRepository.created_at)).all()
    
    @staticmethod
    def get_pending_repositories_by_team_lead(db: Session, team_lead_username: str, status: str = 'pending'):
        """Get pending repositories for a specific team lead"""
        team_lead = UserCRUD.get_user_by_username(db, team_lead_username)
        if not team_lead:
            return []
        
        query = db.query(PendingRepository).filter(PendingRepository.owner_id == team_lead.id)
        if status:
            query = query.filter(PendingRepository.status == status)
        return query.order_by(desc(PendingRepository.created_at)).all()
    
    @staticmethod
    def approve_pending_repository(db: Session, pending_id: int, reviewer_username: str, comment: str = None):
        """Approve a pending repository and create it"""
        
        pending = PendingRepositoryCRUD.get_pending_repository(db, pending_id)
        if not pending:
            raise ValueError("Pending repository not found")
        
        if pending.status != 'pending':
            raise ValueError(f"Repository request is already {pending.status}")
        
        reviewer = UserCRUD.get_user_by_username(db, reviewer_username)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        # Update pending repository status
        pending.status = 'approved'
        pending.reviewed_by_id = reviewer.id
        pending.reviewed_at = datetime.utcnow()
        pending.review_comment = comment
        
        # Create actual repository
        repository = RepositoryCRUD.create_repository(
            db, 
            pending.owner.username, 
            pending.repo_name, 
            pending.description
        )
        
        # Grant write permission to the requester if different from owner
        if pending.requested_by_id != pending.owner_id:
            UserPermissionCRUD.create_permission(
                db,
                username=pending.requested_by.username,
                repo_id=repository.id,
                permission_level='write',
                granted_by_username=pending.owner.username
            )
        
        db.commit()
        db.refresh(pending)
        return pending, repository
    
    @staticmethod
    def reject_pending_repository(db: Session, pending_id: int, reviewer_username: str, comment: str = None):
        """Reject a pending repository"""
        
        pending = PendingRepositoryCRUD.get_pending_repository(db, pending_id)
        if not pending:
            raise ValueError("Pending repository not found")
        
        if pending.status != 'pending':
            raise ValueError(f"Repository request is already {pending.status}")
        
        reviewer = UserCRUD.get_user_by_username(db, reviewer_username)
        if not reviewer:
            raise ValueError("Reviewer not found")
        
        # Update pending repository status
        pending.status = 'rejected'
        pending.reviewed_by_id = reviewer.id
        pending.reviewed_at = datetime.utcnow()
        pending.review_comment = comment
        
        db.commit()
        db.refresh(pending)
        return pending
