from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    repositories = relationship("Repository", back_populates="owner")
    commits = relationship("Commit", back_populates="author")

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(String(16), primary_key=True, index=True)  # Using the hash-based ID
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    head_commit_id = Column(String(40), ForeignKey("commits.id"))
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime)
    archived_reason = Column(Text)
    
    # Repository settings
    is_public = Column(Boolean, default=True)
    language = Column(String(50))
    size_bytes = Column(Integer, default=0)
    
    # G1 Coordinator and Testing fields
    g1_coordinator = Column(String(100))  # Name of G1 coordinator
    tested = Column(Boolean, default=False)  # Yes/No testing status
    instruction_manual_path = Column(String(500))  # Path to uploaded PDF instruction manual
    instruction_manual_filename = Column(String(255))  # Original filename of the manual
    
    # Relationships
    owner = relationship("User", back_populates="repositories")
    commits = relationship("Commit", back_populates="repository", foreign_keys="Commit.repository_id")
    head_commit = relationship("Commit", foreign_keys=[head_commit_id], post_update=True)
    tags = relationship("RepositoryTag", back_populates="repository")

class Commit(Base):
    __tablename__ = "commits"
    
    id = Column(String(40), primary_key=True, index=True)  # SHA-1 hash
    repository_id = Column(String(16), ForeignKey("repositories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_commit_id = Column(String(40), ForeignKey("commits.id"))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Commit metadata
    tree_hash = Column(String(40))  # Hash of the file tree state
    
    # Relationships
    repository = relationship("Repository", back_populates="commits", foreign_keys=[repository_id])
    author = relationship("User", back_populates="commits")
    parent_commit = relationship("Commit", remote_side=[id])
    files = relationship("CommitFile", back_populates="commit")

class CommitFile(Base):
    __tablename__ = "commit_files"
    
    id = Column(Integer, primary_key=True, index=True)
    commit_id = Column(String(40), ForeignKey("commits.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(40), nullable=False)
    file_size = Column(Integer)
    file_mode = Column(String(10))  # File permissions
    
    # Relationships
    commit = relationship("Commit", back_populates="files")
    file_object = relationship("FileObject", foreign_keys=[file_hash], primaryjoin="CommitFile.file_hash == FileObject.hash")

class FileObject(Base):
    __tablename__ = "file_objects"
    
    hash = Column(String(40), primary_key=True, index=True)  # SHA-1 hash of content
    content = Column(LargeBinary, nullable=False)  # Binary file content
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Content type detection
    mime_type = Column(String(100))

class RepositoryTag(Base):
    __tablename__ = "repository_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(String(16), ForeignKey("repositories.id"), nullable=False)
    name = Column(String(50), nullable=False)
    color = Column(String(7))  # Hex color code
    
    # Relationships
    repository = relationship("Repository", back_populates="tags")

class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(String(16), ForeignKey("repositories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    head_commit_id = Column(String(40), ForeignKey("commits.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_default = Column(Boolean, default=False)
    
    # Relationships
    repository = relationship("Repository")
    head_commit = relationship("Commit")

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    repository_id = Column(String(16), ForeignKey("repositories.id"))
    activity_type = Column(String(50), nullable=False)  # commit, create_repo, etc.
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User")
    repository = relationship("Repository")
