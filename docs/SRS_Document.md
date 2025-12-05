# Software Requirements Specification (SRS)
# FoxNest - Distributed Version Control System

**Document Version:** 1.0  
**Date:** December 3, 2025  
**Project Name:** FoxNest  
**Prepared By:** FoxNest Development Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features and Requirements](#3-system-features-and-requirements)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [System Architecture](#5-system-architecture)
6. [Database Design](#6-database-design)
7. [API Specifications](#7-api-specifications)
8. [Security Requirements](#8-security-requirements)
9. [Performance Requirements](#9-performance-requirements)
10. [Quality Attributes](#10-quality-attributes)
11. [User Interface Requirements](#11-user-interface-requirements)
12. [Deployment and Installation](#12-deployment-and-installation)
13. [Appendices](#13-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a comprehensive description of the FoxNest Distributed Version Control System. It details the functional and non-functional requirements, system architecture, database design, API specifications, and deployment guidelines for the complete platform.

FoxNest is designed to be a lightweight, enterprise-ready version control solution with Git-like functionality, team collaboration features, and a modern web-based administration interface.

### 1.2 Scope

FoxNest is a complete distributed version control platform consisting of three main components:

1. **Fox CLI Client**: A command-line tool for local version control operations
2. **FoxNest Server**: A centralized FastAPI-based backend with SQL database storage
3. **FoxNest Frontend**: A React/Vite-based web dashboard for repository management and administration

The system enables:
- Local repository initialization and management
- Push/pull operations with central server synchronization
- Team-based access control with developer/team lead hierarchy
- Commit approval workflows
- Repository archiving and metadata management
- Cross-platform support (Linux, Windows)

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| VCS | Version Control System |
| CLI | Command Line Interface |
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| REST | Representational State Transfer |
| SHA-1 | Secure Hash Algorithm 1 |
| JWT | JSON Web Token |
| CORS | Cross-Origin Resource Sharing |
| ORM | Object-Relational Mapping |
| SQLite | Lightweight relational database |
| PostgreSQL | Enterprise-grade relational database |
| Zlib | Compression library |
| Delta Encoding | Storing differences between file versions |
| Pack Files | Consolidated storage for multiple objects |

### 1.4 References

- Git Documentation: https://git-scm.com/doc
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://www.sqlalchemy.org/
- React Documentation: https://react.dev/
- Vite Documentation: https://vitejs.dev/

### 1.5 Document Overview

This SRS document is organized into 13 sections covering all aspects of the FoxNest system:
- Sections 1-2: Introduction and system overview
- Section 3: Detailed functional requirements
- Sections 4-7: Technical specifications
- Sections 8-10: Quality and performance requirements
- Sections 11-12: UI and deployment specifications
- Section 13: Appendices with additional technical details

---

## 2. Overall Description

### 2.1 Product Perspective

FoxNest is a standalone version control platform designed as an alternative to Git for organizations requiring:
- Simplified version control workflows
- Built-in approval processes
- Centralized repository management
- Role-based access control
- Custom metadata tracking

The system operates in a client-server architecture where the Fox CLI communicates with the FoxNest Server over HTTP/HTTPS.

### 2.2 Product Functions

#### 2.2.1 Fox CLI Client Functions
- Repository initialization (`fox init`)
- File staging and tracking (`fox add`)
- Commit creation (`fox commit`)
- Remote synchronization (`fox push`, `fox pull`)
- Status and history viewing (`fox status`, `fox log`)
- Repository optimization (`fox gc`)
- Origin configuration (`fox set origin`)

#### 2.2.2 FoxNest Server Functions
- User management (create, update, delete users)
- Repository hosting and metadata storage
- Commit storage with file content management
- Permission and access control
- Pending commit approval workflow
- Pending repository approval workflow
- Activity logging and auditing
- File serving and download

#### 2.2.3 FoxNest Frontend Functions
- Dashboard with system statistics
- Repository browsing and management
- User management interface
- Permission assignment
- Pending approval reviews
- Archive management
- Code viewing/editing

### 2.3 User Classes and Characteristics

#### 2.3.1 Developer
- **Description**: Regular team member who commits code
- **Role Code**: `developer`
- **Permissions**: 
  - Initialize and commit to repositories
  - Push commits (requires approval)
  - Pull latest changes
  - View repository files
- **Characteristics**: Requires team lead assignment; all commits require approval

#### 2.3.2 Team Lead
- **Description**: Senior team member with approval authority
- **Role Code**: `team_lead`
- **Permissions**:
  - All developer permissions
  - Direct push without approval
  - Approve/reject developer commits
  - Approve/reject repository creation requests
  - Create repositories directly
  - Manage team member permissions
- **Characteristics**: Can own repositories; manages developer team

#### 2.3.3 Administrator
- **Description**: System administrator with full access
- **Permissions**:
  - All team lead permissions
  - User creation and deletion
  - System configuration
  - Database management
  - Server maintenance

### 2.4 Operating Environment

#### 2.4.1 Server Environment
- **Operating System**: Linux (Ubuntu 20.04+, Debian 10+), Windows Server 2019+
- **Runtime**: Python 3.8+
- **Database**: SQLite (development), PostgreSQL 12+ (production)
- **Web Server**: Uvicorn ASGI server
- **Port**: 5000 (default, configurable)

#### 2.4.2 Client Environment
- **Operating System**: Linux, Windows, macOS
- **Runtime**: Python 3.8+
- **Dependencies**: requests, pathlib, zlib

#### 2.4.3 Frontend Environment
- **Runtime**: Node.js 16+
- **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Build Tool**: Vite 4+
- **Port**: 5173 (development)

### 2.5 Design and Implementation Constraints

1. **HTTP-based Protocol**: All client-server communication uses HTTP/HTTPS
2. **JSON Data Format**: All API requests/responses use JSON
3. **SHA-1 Hashing**: Commit and file identification uses SHA-1 hashes
4. **Zlib Compression**: File content compressed at level 6
5. **Base64 Encoding**: Binary file transfer uses Base64 encoding
6. **MD5 Repository IDs**: Repository IDs are 16-character MD5 hashes
7. **Single Branch**: Initial version supports single branch (main)

### 2.6 Assumptions and Dependencies

#### Assumptions
1. Users have network access to the FoxNest server
2. Users have Python 3.8+ installed for CLI operations
3. Modern web browsers are used for frontend access
4. Sufficient disk space for repository storage

#### Dependencies
- Python packages: FastAPI, SQLAlchemy, Uvicorn, requests, python-dotenv
- Node.js packages: React, Vite, react-icons, tailwindcss
- System libraries: zlib (usually pre-installed)

---

## 3. System Features and Requirements

### 3.1 Repository Management

#### 3.1.1 FR-RM-001: Repository Initialization
- **Description**: Users can initialize a new Fox repository in any directory
- **Input**: Username, repository name, optional server URL
- **Process**:
  1. Create `.fox` directory structure
  2. Initialize configuration file with metadata
  3. Create empty commits file
  4. Create staging, objects, and packs directories
- **Output**: Initialized local repository ready for operations
- **Priority**: High

#### 3.1.2 FR-RM-002: Remote Repository Creation
- **Description**: Create repository on the central server
- **Input**: Username, repository name, optional description
- **Process**:
  1. Validate user exists and is active
  2. Generate unique repository ID (MD5 hash)
  3. For developers: create pending request for team lead approval
  4. For team leads: create repository immediately
  5. Create default branch (main)
- **Output**: Repository ID or pending request ID
- **Priority**: High

#### 3.1.3 FR-RM-003: Repository Listing
- **Description**: List all repositories or filter by user
- **Input**: Optional username filter
- **Output**: Array of repository objects with metadata
- **Priority**: High

#### 3.1.4 FR-RM-004: Repository Deletion
- **Description**: Permanently delete a repository and all its data
- **Input**: Repository ID
- **Validation**: User must have admin permission
- **Output**: Success confirmation
- **Priority**: Medium

#### 3.1.5 FR-RM-005: Repository Archiving
- **Description**: Archive a repository to mark it as inactive
- **Input**: Repository ID, optional archive reason
- **Process**:
  1. Set `is_archived` flag to true
  2. Record `archived_at` timestamp
  3. Store archive reason
- **Output**: Updated repository object
- **Priority**: Medium

### 3.2 Version Control Operations

#### 3.2.1 FR-VC-001: File Staging
- **Description**: Add files to the staging area for next commit
- **Input**: File paths (supports wildcards) or `--all` flag
- **Process**:
  1. Read file content
  2. Calculate SHA-1 hash
  3. Compress content using zlib
  4. Store in objects directory with subdirectory structure
  5. Update staging index
- **Output**: List of staged files with status
- **Priority**: High

#### 3.2.2 FR-VC-002: Commit Creation
- **Description**: Create a new commit from staged changes
- **Input**: Commit message, optional author override
- **Process**:
  1. Collect all staged files
  2. Calculate tree hash
  3. Generate commit ID (SHA-1)
  4. Record parent commit reference
  5. Store commit metadata and file references
  6. Clear staging area
  7. Update HEAD pointer
- **Output**: Commit ID and summary
- **Priority**: High

#### 3.2.3 FR-VC-003: Push Operation
- **Description**: Send local commits to remote server
- **Input**: Repository ID, commit data, optional archive flag
- **Process**:
  1. Validate user permissions
  2. Check repository status (archived check)
  3. For developers: create pending commit
  4. For team leads: merge directly
  5. Store file objects in database
  6. Update repository HEAD
  7. Log activity
- **Output**: Commit ID and status (merged/pending_approval)
- **Priority**: High

#### 3.2.4 FR-VC-004: Pull Operation
- **Description**: Retrieve commits from remote server
- **Input**: Repository ID, optional since-commit hash
- **Process**:
  1. Query server for new commits
  2. Download commit metadata
  3. Download file contents (Base64 encoded)
  4. Decompress and store locally
  5. Update local commits file
  6. Update local HEAD
- **Output**: List of new commits applied
- **Priority**: High

#### 3.2.5 FR-VC-005: Status Check
- **Description**: Display current repository status
- **Input**: Optional short format flag
- **Output**: 
  - Staged files
  - Modified files
  - Untracked files
  - Current branch/HEAD information
- **Priority**: High

#### 3.2.6 FR-VC-006: Commit History
- **Description**: View commit log
- **Input**: Optional oneline format, count limit
- **Output**: List of commits with:
  - Commit ID
  - Author
  - Date
  - Message
  - Parent reference
- **Priority**: High

#### 3.2.7 FR-VC-007: Garbage Collection
- **Description**: Optimize repository storage
- **Input**: None
- **Process**:
  1. Identify unreferenced objects
  2. Create pack files for loose objects
  3. Remove orphaned files
  4. Compact storage
- **Output**: Storage savings statistics
- **Priority**: Medium

### 3.3 User Management

#### 3.3.1 FR-UM-001: User Creation
- **Description**: Create new user account
- **Input**: 
  - Username (required)
  - Email (optional)
  - Full name (optional)
  - Role: 'developer' or 'team_lead'
  - Team lead ID (required for developers)
- **Validation**:
  - Username must be unique
  - If developer, team lead must exist and have team_lead role
- **Output**: Created user object
- **Priority**: High

#### 3.3.2 FR-UM-002: User Listing
- **Description**: List all users with their details
- **Output**: Array of users including:
  - ID, username, email, full name
  - Role and team lead assignment
  - Created date
  - Active status
  - Repository count
- **Priority**: High

#### 3.3.3 FR-UM-003: User Update
- **Description**: Update user information
- **Input**: Username, fields to update (email, full_name, is_active)
- **Output**: Updated user object
- **Priority**: Medium

#### 3.3.4 FR-UM-004: User Deletion
- **Description**: Delete user account
- **Input**: Username
- **Validation**: User must not own any repositories
- **Output**: Success confirmation
- **Priority**: Medium

### 3.4 Permission Management

#### 3.4.1 FR-PM-001: Grant Permission
- **Description**: Grant user access to a repository
- **Input**:
  - Username
  - Repository ID
  - Permission level: 'read', 'write', 'team_lead', 'admin'
  - Optional: granted_by username
- **Output**: Permission object
- **Priority**: High

#### 3.4.2 FR-PM-002: Update Permission
- **Description**: Change user's permission level
- **Input**: Username, Repository ID, new permission level
- **Output**: Updated permission object
- **Priority**: Medium

#### 3.4.3 FR-PM-003: Revoke Permission
- **Description**: Remove user's access to repository
- **Input**: Username, Repository ID
- **Output**: Success confirmation
- **Priority**: Medium

#### 3.4.4 FR-PM-004: List Repository Permissions
- **Description**: Get all permissions for a repository
- **Input**: Repository ID
- **Output**: Array of permission objects
- **Priority**: Medium

#### 3.4.5 FR-PM-005: List User Permissions
- **Description**: Get all permissions for a user
- **Input**: Username
- **Output**: Array of permission objects with repository details
- **Priority**: Medium

### 3.5 Approval Workflow

#### 3.5.1 FR-AW-001: Pending Commit Management
- **Description**: Manage commits awaiting approval
- **Process**:
  1. Developer pushes commit
  2. System creates pending commit record
  3. Team lead reviews in frontend
  4. Approve: merge commit to repository
  5. Reject: mark as rejected with comment
- **Output**: Status updates and notifications
- **Priority**: High

#### 3.5.2 FR-AW-002: Pending Repository Management
- **Description**: Manage repository creation requests
- **Process**:
  1. Developer requests new repository
  2. System creates pending repository record
  3. Team lead reviews in frontend
  4. Approve: create actual repository
  5. Reject: mark as rejected with comment
- **Output**: Repository or rejection status
- **Priority**: High

#### 3.5.3 FR-AW-003: Review Filtering
- **Description**: Filter pending items by team lead
- **Input**: Team lead username
- **Output**: Filtered list of pending items for that team
- **Priority**: Medium

### 3.6 Repository Metadata

#### 3.6.1 FR-MD-001: G1 Coordinator Assignment
- **Description**: Assign G1 coordinator to repository
- **Input**: Repository ID, coordinator name
- **Output**: Updated repository object
- **Priority**: Medium

#### 3.6.2 FR-MD-002: Testing Status
- **Description**: Mark repository testing status
- **Input**: Repository ID, tested boolean
- **Output**: Updated repository object
- **Priority**: Medium

#### 3.6.3 FR-MD-003: Instruction Manual Upload
- **Description**: Upload PDF instruction manual
- **Input**: Repository ID, PDF file
- **Validation**: File must be PDF format
- **Process**:
  1. Save file to uploads directory
  2. Update repository with file path
  3. Store original filename
- **Output**: Upload confirmation
- **Priority**: Medium

#### 3.6.4 FR-MD-004: Instruction Manual Download
- **Description**: Download repository's instruction manual
- **Input**: Repository ID
- **Output**: PDF file download
- **Priority**: Medium

### 3.7 Activity Logging

#### 3.7.1 FR-AL-001: Activity Recording
- **Description**: Log all significant actions
- **Events Logged**:
  - Repository creation
  - Commit pushes
  - Pending commit creation
  - Approval/rejection actions
  - User actions
- **Data Recorded**:
  - User ID
  - Repository ID (if applicable)
  - Activity type
  - Description
  - Timestamp
- **Priority**: Medium

#### 3.7.2 FR-AL-002: Activity Retrieval
- **Description**: Get recent system activities
- **Input**: Optional limit (default 20)
- **Output**: Array of activity objects
- **Priority**: Medium

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 Command Line Interface (CLI)

**Fox Client Commands:**

```
Usage: fox <command> [options]

Commands:
  init          Initialize a new repository
  add           Stage files for commit
  commit        Create a new commit
  push          Push commits to server
  pull          Pull commits from server
  status        Show repository status
  log           Show commit history
  set           Configure repository settings
  gc            Optimize repository storage
  version       Show version information
  help          Show help information

Options:
  --username    Specify username for operations
  --repo-name   Specify repository name
  --server      Specify server URL
  --all, -A     Add all files (with 'add' command)
  --message, -m Commit message (with 'commit' command)
  --archive     Archive after push (with 'push' command)
  --oneline     Compact log format (with 'log' command)
  --short       Short status format (with 'status' command)
```

#### 4.1.2 Web Interface

The FoxNest Frontend provides the following pages:

| Page | Path | Description |
|------|------|-------------|
| Dashboard | `/` | Overview with statistics and recent activity |
| Repositories | `/repositories` | Browse and manage active repositories |
| Archive | `/archive` | View and manage archived repositories |
| Users | `/users` | View user statistics and information |
| Users Management | `/users-management` | Create, edit, and manage users |
| Pending Approvals | `/pending-approvals` | Review pending commits |
| Pending Repositories | `/pending-repositories` | Review repository requests |

### 4.2 Hardware Interfaces

No specific hardware interfaces are required. The system operates on standard computing hardware with network connectivity.

### 4.3 Software Interfaces

#### 4.3.1 Database Interface
- **Type**: SQLAlchemy ORM
- **Databases Supported**: SQLite, PostgreSQL
- **Connection**: Via DATABASE_URL environment variable

#### 4.3.2 File System Interface
- **Server Storage**: `/tmp/foxnest_server/repositories/`
- **Upload Storage**: `/tmp/foxnest_uploads/`
- **Client Storage**: `.fox/` directory in repository root

### 4.4 Communication Interfaces

#### 4.4.1 HTTP/HTTPS Protocol
- **Base URL**: `http://<server>:5000`
- **API Base**: `/api`
- **Content-Type**: `application/json`
- **File Upload**: `multipart/form-data`

#### 4.4.2 CORS Configuration
```python
allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers = ["*"]
allow_credentials = True
```

---

## 5. System Architecture

### 5.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FoxNest Platform                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐     HTTP/JSON     ┌────────────────────────────────┐  │
│  │  Fox CLI     │◄────────────────► │      FoxNest Server           │  │
│  │  Client      │                   │      (FastAPI)                 │  │
│  └──────────────┘                   │                                │  │
│                                     │  ┌───────────────────────────┐ │  │
│  ┌──────────────┐     HTTP/JSON     │  │   Business Logic Layer   │ │  │
│  │  FoxNest     │◄────────────────► │  │   - Repository CRUD      │ │  │
│  │  Frontend    │                   │  │   - Commit Management     │ │  │
│  │  (React)     │                   │  │   - User Management       │ │  │
│  └──────────────┘                   │  │   - Permission Control    │ │  │
│                                     │  │   - Approval Workflow     │ │  │
│                                     │  └───────────────────────────┘ │  │
│                                     │              │                  │  │
│                                     │  ┌───────────────────────────┐ │  │
│                                     │  │   Data Access Layer       │ │  │
│                                     │  │   (SQLAlchemy ORM)        │ │  │
│                                     │  └───────────────────────────┘ │  │
│                                     │              │                  │  │
│                                     │  ┌───────────────────────────┐ │  │
│                                     │  │   Database                │ │  │
│                                     │  │   (SQLite/PostgreSQL)     │ │  │
│                                     │  └───────────────────────────┘ │  │
│                                     └────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Component Descriptions

#### 5.2.1 Fox CLI Client
- **Technology**: Python 3.8+
- **Key Files**: `client/fox.py`
- **Responsibilities**:
  - Local repository management
  - File staging and compression
  - Commit creation
  - Server communication
  - Object storage management

**Internal Structure:**
```
FoxClient Class
├── Configuration Management
│   ├── load_config() / save_config()
│   ├── load_global_config() / save_global_config()
│   └── get_origin_url() / set_origin()
├── Repository Operations
│   ├── init()
│   ├── add()
│   ├── commit()
│   └── status()
├── Remote Operations
│   ├── push()
│   ├── pull()
│   └── create_remote_repository()
├── Storage Optimization
│   ├── compress_data() / decompress_data()
│   ├── calculate_delta() / apply_delta()
│   └── gc() (garbage collection)
└── Helper Functions
    ├── calculate_file_hash()
    ├── get_object_path()
    └── should_ignore()
```

#### 5.2.2 FoxNest Server
- **Technology**: FastAPI (Python)
- **Key Files**: `server/server.py`
- **Responsibilities**:
  - RESTful API endpoints
  - Business logic execution
  - Database operations
  - File storage management

**Directory Structure:**
```
server/
├── server.py           # Main application and API routes
├── database/
│   ├── database.py     # Database connection setup
│   ├── models.py       # SQLAlchemy ORM models
│   └── crud.py         # Data access functions
├── init_database.py    # Database initialization script
└── .env                # Environment configuration
```

#### 5.2.3 FoxNest Frontend
- **Technology**: React 18+ with Vite
- **Key Files**: `foxnestFrontend/src/`
- **Responsibilities**:
  - User interface rendering
  - API communication
  - State management
  - User interactions

**Directory Structure:**
```
foxnestFrontend/src/
├── App.jsx             # Main application component
├── main.jsx            # Entry point
├── index.css           # Global styles (Tailwind)
├── components/
│   ├── ui/             # Reusable UI components
│   │   ├── Badge.jsx
│   │   ├── Button.jsx
│   │   └── GlassCard.jsx
│   ├── layout/         # Layout components
│   │   ├── Header.jsx
│   │   ├── Layout.jsx
│   │   ├── Navigation.jsx
│   │   └── Sidebar.jsx
│   └── CodeEditor.jsx  # Code viewing component
├── pages/
│   ├── Dashboard.jsx
│   ├── Repositories.jsx
│   ├── Archive.jsx
│   ├── Users.jsx
│   ├── UsersManagement.jsx
│   ├── PendingApprovals.jsx
│   └── PendingRepositories.jsx
├── hooks/
│   ├── useApi.js       # API hook abstractions
│   └── useCustomHooks.js
└── utils/
    ├── api.js          # API client class
    └── helpers.js      # Utility functions
```

### 5.3 Data Flow Diagrams

#### 5.3.1 Commit Push Flow (Developer)
```
Developer          Fox CLI           Server          Database
    │                 │                 │                │
    │ fox push        │                 │                │
    │────────────────►│                 │                │
    │                 │ POST /push      │                │
    │                 │────────────────►│                │
    │                 │                 │ Check user role│
    │                 │                 │───────────────►│
    │                 │                 │◄───────────────│
    │                 │                 │                │
    │                 │                 │ Create pending │
    │                 │                 │───────────────►│
    │                 │                 │◄───────────────│
    │                 │◄────────────────│                │
    │                 │ pending_approval│                │
    │◄────────────────│                 │                │
    │ "Awaiting       │                 │                │
    │  team lead"     │                 │                │
```

#### 5.3.2 Commit Approval Flow
```
Team Lead         Frontend          Server          Database
    │                 │                 │                │
    │ View pending    │                 │                │
    │────────────────►│                 │                │
    │                 │ GET /pending    │                │
    │                 │────────────────►│                │
    │                 │                 │───────────────►│
    │                 │◄────────────────│◄───────────────│
    │◄────────────────│                 │                │
    │                 │                 │                │
    │ Click approve   │                 │                │
    │────────────────►│                 │                │
    │                 │POST /review     │                │
    │                 │────────────────►│                │
    │                 │                 │ Merge commit   │
    │                 │                 │───────────────►│
    │                 │                 │◄───────────────│
    │                 │◄────────────────│                │
    │◄────────────────│ Success         │                │
```

---

## 6. Database Design

### 6.1 Entity-Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   User      │       │   Repository    │       │   Commit    │
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ id (PK)     │◄──┐   │ id (PK)         │◄──┐   │ id (PK)     │
│ username    │   │   │ name            │   │   │ repository_id│
│ email       │   │   │ description     │   │   │ author_id   │
│ full_name   │   │   │ owner_id (FK)   │───┘   │ parent_id   │
│ role        │   │   │ head_commit_id  │◄──────│ message     │
│ team_lead_id│───┘   │ is_archived     │       │ tree_hash   │
│ created_at  │       │ g1_coordinator  │       │ created_at  │
│ is_active   │       │ tested          │       └─────────────┘
└─────────────┘       │ manual_path     │              │
       │              └─────────────────┘              │
       │                     │                         │
       ▼                     │                         ▼
┌─────────────┐              │              ┌─────────────────┐
│ UserPerm    │              │              │  CommitFile     │
├─────────────┤              │              ├─────────────────┤
│ id (PK)     │              │              │ id (PK)         │
│ user_id(FK) │              │              │ commit_id (FK)  │
│ repo_id(FK) │──────────────┘              │ file_path       │
│ perm_level  │                             │ file_hash (FK)  │
│ granted_by  │                             │ file_size       │
│ granted_at  │                             └─────────────────┘
└─────────────┘                                    │
                                                   ▼
┌─────────────────┐    ┌─────────────────┐  ┌─────────────┐
│ PendingCommit   │    │ PendingRepo     │  │ FileObject  │
├─────────────────┤    ├─────────────────┤  ├─────────────┤
│ id (PK)         │    │ id (PK)         │  │ hash (PK)   │
│ repository_id   │    │ repo_name       │  │ content     │
│ author_id       │    │ requested_by_id │  │ size        │
│ message         │    │ owner_id        │  │ mime_type   │
│ status          │    │ status          │  │ created_at  │
│ reviewed_by_id  │    │ reviewed_by_id  │  └─────────────┘
│ files_data      │    │ review_comment  │
└─────────────────┘    └─────────────────┘
```

### 6.2 Table Specifications

#### 6.2.1 Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'developer',
    team_lead_id INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 6.2.2 Repositories Table
```sql
CREATE TABLE repositories (
    id VARCHAR(16) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    head_commit_id VARCHAR(40) REFERENCES commits(id),
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at DATETIME,
    archived_reason TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    language VARCHAR(50),
    size_bytes INTEGER DEFAULT 0,
    g1_coordinator VARCHAR(100),
    tested BOOLEAN DEFAULT FALSE,
    instruction_manual_path VARCHAR(500),
    instruction_manual_filename VARCHAR(255)
);
```

#### 6.2.3 Commits Table
```sql
CREATE TABLE commits (
    id VARCHAR(40) PRIMARY KEY,
    repository_id VARCHAR(16) NOT NULL REFERENCES repositories(id),
    author_id INTEGER NOT NULL REFERENCES users(id),
    parent_commit_id VARCHAR(40) REFERENCES commits(id),
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    tree_hash VARCHAR(40)
);
```

#### 6.2.4 CommitFiles Table
```sql
CREATE TABLE commit_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_id VARCHAR(40) NOT NULL REFERENCES commits(id),
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(40) NOT NULL,
    file_size INTEGER,
    file_mode VARCHAR(10)
);
```

#### 6.2.5 FileObjects Table
```sql
CREATE TABLE file_objects (
    hash VARCHAR(40) PRIMARY KEY,
    content BLOB NOT NULL,
    size INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    mime_type VARCHAR(100)
);
```

#### 6.2.6 UserPermissions Table
```sql
CREATE TABLE user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    repository_id VARCHAR(16) NOT NULL REFERENCES repositories(id),
    permission_level VARCHAR(20) NOT NULL,
    granted_by_id INTEGER REFERENCES users(id),
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, repository_id)
);
```

#### 6.2.7 PendingCommits Table
```sql
CREATE TABLE pending_commits (
    id VARCHAR(40) PRIMARY KEY,
    repository_id VARCHAR(16) NOT NULL REFERENCES repositories(id),
    author_id INTEGER NOT NULL REFERENCES users(id),
    parent_commit_id VARCHAR(40),
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by_id INTEGER REFERENCES users(id),
    reviewed_at DATETIME,
    review_comment TEXT,
    tree_hash VARCHAR(40),
    files_data TEXT
);
```

#### 6.2.8 PendingRepositories Table
```sql
CREATE TABLE pending_repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name VARCHAR(100) NOT NULL,
    description TEXT,
    requested_by_id INTEGER NOT NULL REFERENCES users(id),
    owner_id INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by_id INTEGER REFERENCES users(id),
    reviewed_at DATETIME,
    review_comment TEXT
);
```

#### 6.2.9 Activities Table
```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    repository_id VARCHAR(16) REFERENCES repositories(id),
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. API Specifications

### 7.1 Base Configuration

| Property | Value |
|----------|-------|
| Base URL | `http://<server>:5000` |
| API Prefix | `/api` |
| Content-Type | `application/json` |
| Authentication | None (future: JWT) |

### 7.2 Repository Endpoints

#### POST /api/repository/create
Create a new repository.

**Request Body:**
```json
{
  "username": "string (required)",
  "repo_name": "string (required)",
  "description": "string (optional)"
}
```

**Response (Success - Direct Creation):**
```json
{
  "success": true,
  "repo_id": "string (16 char)",
  "owner": "string",
  "message": null
}
```

**Response (Success - Pending Approval):**
```json
{
  "success": true,
  "status": "pending_approval",
  "team_lead": "string",
  "pending_id": "integer",
  "message": "string"
}
```

#### GET /api/repository/list
List repositories for a user.

**Query Parameters:**
- `username` (required): User's username
- `repo_name` (optional): Specific repository name

**Response:**
```json
{
  "success": true,
  "repositories": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "owner": "string",
      "created_at": "ISO 8601 datetime",
      "commits": ["commit_id_1", "commit_id_2"],
      "head": "commit_id",
      "is_archived": false,
      "g1_coordinator": "string",
      "tested": false
    }
  ]
}
```

#### GET /api/repositories/all
List all repositories.

**Response:** Same as `/api/repository/list`

#### GET /api/repository/{repo_id}
Get repository details.

**Response:**
```json
{
  "success": true,
  "repository": { /* repository object */ }
}
```

#### DELETE /api/repository/{repo_id}
Delete a repository permanently.

**Response:**
```json
{
  "success": true,
  "message": "Repository deleted successfully"
}
```

#### POST /api/repository/{repo_id}/push
Push a commit to repository.

**Request Body:**
```json
{
  "commit": {
    "id": "sha1_hash",
    "author": "username",
    "message": "commit message",
    "parent": "parent_commit_id",
    "timestamp": "ISO 8601 datetime",
    "tree_hash": "sha1_hash",
    "files": {
      "file_path": "base64_content"
    }
  },
  "archive": false
}
```

**Response (Direct Merge):**
```json
{
  "success": true,
  "commit_id": "string",
  "status": "merged"
}
```

**Response (Pending Approval):**
```json
{
  "success": true,
  "commit_id": "string",
  "status": "pending_approval",
  "team_lead": "string",
  "message": "Your commit has been submitted for review..."
}
```

#### GET /api/repository/{repo_id}/pull
Pull commits from repository.

**Query Parameters:**
- `since_commit` (optional): Get commits after this ID

**Response:**
```json
{
  "success": true,
  "commits": [
    {
      "id": "string",
      "author": "string",
      "message": "string",
      "timestamp": "ISO 8601 datetime",
      "files": { "path": "base64_content" }
    }
  ],
  "head": "commit_id"
}
```

#### GET /api/repository/{repo_id}/commits
Get commit history.

**Query Parameters:**
- `full` (optional, boolean): Include file contents

**Response:**
```json
{
  "success": true,
  "commits": [ /* commit objects */ ]
}
```

#### GET /api/repository/{repo_id}/files
Get repository files from latest commit.

**Response:**
```json
{
  "success": true,
  "files": {
    "path/to/file.txt": {
      "content": "string",
      "is_binary": false,
      "size": 1234,
      "hash": "sha1"
    }
  },
  "folders": ["path", "path/to"],
  "commit_id": "string",
  "commit_message": "string"
}
```

#### PUT /api/repository/{repo_id}/details
Update repository metadata.

**Request Body:**
```json
{
  "g1_coordinator": "string (optional)",
  "tested": "boolean (optional)"
}
```

#### POST /api/repository/{repo_id}/upload-manual
Upload instruction manual PDF.

**Request:** `multipart/form-data` with PDF file

**Response:**
```json
{
  "success": true,
  "message": "Instruction manual uploaded successfully",
  "filename": "original_filename.pdf"
}
```

#### GET /api/repository/{repo_id}/download-manual
Download instruction manual.

**Response:** PDF file download

### 7.3 User Endpoints

#### GET /api/users
List all users.

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "username": "string",
      "email": "string",
      "full_name": "string",
      "role": "developer|team_lead",
      "team_lead_id": 2,
      "team_lead_name": "string",
      "created_at": "ISO 8601 datetime",
      "is_active": true,
      "repository_count": 5
    }
  ]
}
```

#### POST /api/users/create
Create new user.

**Request Body:**
```json
{
  "username": "string (required)",
  "email": "string (optional)",
  "full_name": "string (optional)",
  "role": "developer|team_lead (default: developer)",
  "team_lead_id": "integer (required for developers)"
}
```

#### PUT /api/users/{username}
Update user.

**Request Body:**
```json
{
  "email": "string (optional)",
  "full_name": "string (optional)",
  "is_active": "boolean (optional)"
}
```

#### DELETE /api/users/{username}
Delete user (fails if user owns repositories).

### 7.4 Permission Endpoints

#### POST /api/permissions/create
Grant permission.

**Request Body:**
```json
{
  "username": "string",
  "repo_id": "string",
  "permission_level": "read|write|team_lead|admin",
  "granted_by": "string (optional)"
}
```

#### PUT /api/permissions/update
Update permission (same as create, upserts).

#### DELETE /api/permissions/revoke
Revoke permission.

**Query Parameters:**
- `username`: User's username
- `repo_id`: Repository ID

#### GET /api/permissions/repository/{repo_id}
Get all permissions for repository.

#### GET /api/permissions/user/{username}
Get all permissions for user.

### 7.5 Pending Items Endpoints

#### GET /api/pending-commits
Get pending commits.

**Query Parameters:**
- `status`: pending|approved|rejected (default: pending)
- `team_lead_username`: Filter by team lead

#### GET /api/repository/{repo_id}/pending-commits
Get pending commits for specific repository.

#### POST /api/pending-commits/{commit_id}/review
Review pending commit.

**Request Body:**
```json
{
  "reviewer_username": "string (required)",
  "action": "approve|reject (required)",
  "comment": "string (optional)"
}
```

#### GET /api/pending-repositories
Get pending repository requests.

**Query Parameters:**
- `status`: pending|approved|rejected
- `team_lead_username`: Filter by team lead

#### POST /api/pending-repositories/{pending_id}/review
Review pending repository request.

**Request Body:** Same as commit review

### 7.6 Activity Endpoints

#### GET /api/activities
Get recent activities.

**Query Parameters:**
- `limit`: Number of activities (default: 20)

**Response:**
```json
{
  "success": true,
  "activities": [
    {
      "id": 1,
      "user": "username",
      "repository": "repo_name",
      "activity_type": "push_commit",
      "description": "string",
      "created_at": "ISO 8601 datetime"
    }
  ]
}
```

### 7.7 Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing the issue"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (validation error)
- `403`: Forbidden (permission denied)
- `404`: Not Found
- `500`: Internal Server Error

---

## 8. Security Requirements

### 8.1 Authentication

#### 8.1.1 Current Implementation
- Username-based identification
- No password authentication (planned for future)
- User must exist in database before operations

#### 8.1.2 Planned Enhancements
- JWT-based authentication
- Password hashing with bcrypt
- Session management
- API key support for CLI

### 8.2 Authorization

#### 8.2.1 Role-Based Access Control (RBAC)

| Permission | Developer | Team Lead | Admin |
|------------|-----------|-----------|-------|
| View repositories | ✓ | ✓ | ✓ |
| Create repository | Pending | ✓ | ✓ |
| Push commits | Pending | ✓ | ✓ |
| Approve commits | ✗ | ✓ | ✓ |
| Manage users | ✗ | ✗ | ✓ |
| Delete repository | ✗ | ✓ (own) | ✓ |

#### 8.2.2 Repository Permissions

| Level | Capabilities |
|-------|-------------|
| read | View repository, pull commits |
| write | read + push commits (with approval) |
| team_lead | write + approve commits, direct push |
| admin | team_lead + delete repository, manage permissions |

### 8.3 Data Protection

#### 8.3.1 Input Validation
- All user inputs sanitized
- File type validation for uploads (PDF only for manuals)
- Username and repository name format validation

#### 8.3.2 SQL Injection Prevention
- SQLAlchemy ORM parameterized queries
- No raw SQL string concatenation

#### 8.3.3 CORS Protection
- Configurable allowed origins
- Credentials restricted to allowed domains

### 8.4 Network Security

#### 8.4.1 Current
- HTTP communication (development)
- CORS middleware

#### 8.4.2 Production Recommendations
- HTTPS with TLS 1.2+
- Reverse proxy (nginx/Apache)
- Rate limiting
- IP whitelist for admin functions

---

## 9. Performance Requirements

### 9.1 Response Time

| Operation | Target | Maximum |
|-----------|--------|---------|
| Health check | < 50ms | 100ms |
| Repository listing | < 200ms | 500ms |
| Single repository fetch | < 100ms | 300ms |
| Commit push | < 500ms | 2s |
| Commit pull | < 300ms | 1s |
| File upload (5MB) | < 2s | 5s |

### 9.2 Throughput

| Metric | Target |
|--------|--------|
| Concurrent users | 50 |
| API requests/second | 100 |
| Commits/minute | 30 |
| File uploads/minute | 10 |

### 9.3 Storage Optimization

#### 9.3.1 Compression
- Zlib compression level 6
- Expected reduction: ~50% for text files
- Pack file threshold: 20 objects

#### 9.3.2 Deduplication
- Content-addressable storage (SHA-1 hash)
- Identical files stored once
- Delta encoding infrastructure ready

### 9.4 Scalability

#### 9.4.1 Horizontal Scaling
- Stateless API design
- Database connection pooling
- Load balancer compatible

#### 9.4.2 Database Scaling
- SQLite for development (single user)
- PostgreSQL for production
- Connection pooling supported

---

## 10. Quality Attributes

### 10.1 Reliability

#### 10.1.1 Availability Target
- Uptime: 99.5%
- Planned maintenance windows: < 4 hours/month

#### 10.1.2 Fault Tolerance
- Graceful error handling
- Transaction rollback on failure
- Error logging for debugging

#### 10.1.3 Data Integrity
- SHA-1 hash verification
- Database transactions
- Foreign key constraints

### 10.2 Maintainability

#### 10.2.1 Code Organization
- Separation of concerns (MVC-like)
- Modular component design
- Consistent naming conventions

#### 10.2.2 Documentation
- Inline code comments
- API documentation (Swagger/OpenAPI)
- README files in each directory

### 10.3 Portability

#### 10.3.1 Platform Support
- Linux (primary)
- Windows (supported)
- macOS (supported)

#### 10.3.2 Database Portability
- SQLite for development
- PostgreSQL for production
- ORM abstraction layer

### 10.4 Usability

#### 10.4.1 CLI Usability
- Git-like familiar commands
- Helpful error messages
- Extended help documentation

#### 10.4.2 Web Interface Usability
- Intuitive navigation
- Responsive design
- Loading state indicators
- Error state handling

### 10.5 Testability

#### 10.5.1 Unit Testing
- Individual function testing
- CRUD operation testing
- API endpoint testing

#### 10.5.2 Integration Testing
- Client-server communication
- Database operations
- End-to-end workflows

---

## 11. User Interface Requirements

### 11.1 General UI Guidelines

#### 11.1.1 Design System
- **Color Scheme**: Dark theme with glass morphism effects
- **Primary Colors**: 
  - Background: Dark gradients (#1a1a2e → #16213e)
  - Primary: Blue (#3b82f6)
  - Success: Green (#22c55e)
  - Warning: Yellow (#eab308)
  - Danger: Red (#ef4444)
- **Typography**: System fonts, clear hierarchy
- **Spacing**: Consistent padding and margins (Tailwind scale)

#### 11.1.2 Responsive Design
- Desktop-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Grid layouts adapt to screen size

### 11.2 Component Library

#### 11.2.1 GlassCard
```jsx
<GlassCard className="p-6">
  {/* Content with glass morphism effect */}
</GlassCard>
```
- Backdrop blur
- Semi-transparent background
- Border with transparency

#### 11.2.2 Button
```jsx
<Button variant="primary|secondary|ghost" size="sm|md|lg">
  Click me
</Button>
```
- Variants: primary (solid), secondary (outline), ghost (text)
- Sizes with consistent padding
- Hover and active states

#### 11.2.3 Badge
```jsx
<Badge variant="success|warning|danger|info|secondary">
  Status
</Badge>
```
- Color-coded status indicators
- Pill-shaped design
- Icon support

### 11.3 Page Layouts

#### 11.3.1 Dashboard Page
- Welcome message with server status
- Statistics cards (4-column grid)
- Top repositories list
- Recent activity feed

#### 11.3.2 Repositories Page
- Header with title and action buttons
- Statistics bar (4-column grid)
- Repository grid/list view toggle
- Repository cards with:
  - Name and description
  - Language badge
  - Commit count
  - Last update
  - Action buttons (edit, delete, archive)

#### 11.3.3 Users Management Page
- Header with Add User button
- User grid (3-column responsive)
- User cards with:
  - Avatar with initial
  - Username and full name
  - Email and join date
  - Role badge
  - Team lead info (for developers)
  - Delete button
- Permissions panel (expandable)
- Modals for:
  - Add new user
  - Grant permission
  - Edit permission

#### 11.3.4 Pending Approvals Page
- Header with pending count badge
- Reviewer username input (sticky)
- Team lead filter
- Pending commit cards with:
  - Repository name
  - Author info
  - Commit message
  - Date submitted
  - Approve/Reject buttons
- Comment input for review

### 11.4 Interaction Patterns

#### 11.4.1 Loading States
- Skeleton loaders for content
- Spinner for actions
- Progress indicators for uploads

#### 11.4.2 Error States
- Inline error messages
- Toast notifications
- Error page fallbacks

#### 11.4.3 Success Feedback
- Success alerts/toasts
- Automatic list refresh
- Modal close on success

---

## 12. Deployment and Installation

### 12.1 Server Deployment

#### 12.1.1 Prerequisites
```bash
# System requirements
- Python 3.8+
- pip (Python package manager)
- 1GB+ RAM
- 10GB+ disk space

# For PostgreSQL (production)
- PostgreSQL 12+
```

#### 12.1.2 Installation Steps
```bash
# 1. Clone repository
git clone <repository-url>
cd FoxNest/server

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r ../requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Initialize database
python init_database.py

# 6. Start server
python server.py
```

#### 12.1.3 Environment Variables
```bash
# Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=True

# Database
DATABASE_URL=sqlite:///./foxnest.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:pass@host:5432/foxnest

# CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

#### 12.1.4 Production Deployment
```bash
# Using Gunicorn with Uvicorn workers
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000

# Using systemd service
sudo cp foxnest.service /etc/systemd/system/
sudo systemctl enable foxnest
sudo systemctl start foxnest
```

### 12.2 Frontend Deployment

#### 12.2.1 Development Setup
```bash
cd foxnestFrontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 12.2.2 Production Build
```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Deploy dist/ folder to web server
```

#### 12.2.3 Configuration
Edit `src/utils/api.js`:
```javascript
const API_BASE_URL = 'http://your-server:5000/api'
```

### 12.3 CLI Client Installation

#### 12.3.1 Linux Installation (DEB Package)
```bash
cd installers/linux

# Build package
./build-deb.sh

# Install
sudo dpkg -i foxnest-1.0.0.deb

# Verify
fox --version
fox-server --version
```

#### 12.3.2 Windows Installation
```powershell
cd installers/windows

# Build with PyInstaller
python -m PyInstaller foxnest.spec

# Or run setup
python setup.py install

# For NSIS installer
# Build using build-windows.bat
```

#### 12.3.3 Manual Python Installation
```bash
# Install system-wide
pip install -e client/

# Or use directly
python client/fox.py <command>
```

### 12.4 Configuration Files

#### 12.4.1 Server Configuration (`server/.env`)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/foxnest
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=False
CORS_ORIGINS=https://your-domain.com
```

#### 12.4.2 Client Global Config (`~/.foxnest/credentials.json`)
```json
{
  "username": "your_username",
  "origin_url": "http://server:5000"
}
```

#### 12.4.3 Repository Local Config (`.fox/config.json`)
```json
{
  "username": "your_username",
  "repo_name": "repository_name",
  "server_url": "http://server:5000",
  "repo_id": "abc123def456",
  "origin_url": "http://server:5000",
  "initialized_at": "2025-12-03T10:00:00"
}
```

---

## 13. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| Blob | Binary Large Object - raw file content |
| Commit | Snapshot of repository state at a point in time |
| HEAD | Pointer to the current/latest commit |
| Hash | Cryptographic fingerprint of content (SHA-1) |
| Index | Staging area for files to be committed |
| Object | Any stored item (blob, commit, tree) |
| Origin | Default remote repository URL |
| Pack | Compressed archive of multiple objects |
| Repository | Collection of files and version history |
| Staging | Process of marking files for next commit |
| Tree | Directory structure representation |

### Appendix B: File Formats

#### B.1 Commit File Structure
```json
{
  "id": "sha1_hash_40_chars",
  "author": "username",
  "message": "Commit message",
  "timestamp": "2025-12-03T10:30:00.000Z",
  "parent": "parent_commit_hash",
  "tree_hash": "sha1_of_tree",
  "files": {
    "sha1_file_hash": "base64_encoded_content"
  }
}
```

#### B.2 Repository Metadata
```json
{
  "id": "16_char_md5_hash",
  "name": "repository_name",
  "description": "Repository description",
  "owner": "username",
  "created_at": "2025-12-03T10:00:00",
  "updated_at": "2025-12-03T15:30:00",
  "head_commit_id": "sha1_hash",
  "is_archived": false,
  "g1_coordinator": "Coordinator Name",
  "tested": true,
  "instruction_manual_filename": "manual.pdf"
}
```

### Appendix C: Error Codes

| Code | Message | Resolution |
|------|---------|------------|
| 400 | Username and repo_name required | Provide required fields |
| 403 | User does not exist | Create user account first |
| 403 | User does not have permission | Request access from admin |
| 404 | Repository not found | Verify repository ID |
| 404 | User not found | Verify username |
| 500 | Internal server error | Check server logs |

### Appendix D: API Rate Limits (Planned)

| Endpoint Category | Limit |
|-------------------|-------|
| Read operations | 1000/hour |
| Write operations | 100/hour |
| File uploads | 20/hour |
| Authentication | 10/minute |

### Appendix E: Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-03 | FoxNest Team | Initial release |

---

**End of Document**

*This SRS document is maintained by the FoxNest Development Team. For questions or updates, please contact the project maintainers.*
