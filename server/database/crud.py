from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from database.models import User, Repository, Commit, CommitFile, FileObject, RepositoryTag, Branch, Activity
from typing import List, Optional
from datetime import datetime
import hashlib

class UserCRUD:
    @staticmethod
    def create_user(db: Session, username: str, email: str = None, full_name: str = None) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            full_name=full_name
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
        # Get or create user
        user = UserCRUD.get_or_create_user(db, username)
        
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
            author = UserCRUD.create_user(db, commit_data["author"])
        
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
