# FoxNest - Distributed Version Control System

FoxNest is a custom distributed version control system with client-server architecture.

## Features

- Local repository initialization with `fox init`
- Push changes to central server with `fox push`
- Pull changes from server with `fox pull`
- Commit tracking and history
- User authentication and repository management
- Central server for hosting repositories

## Architecture

- **Client**: Local Fox CLI tool for version control operations
- **Server**: Central FoxNest server for repository hosting
- **Protocol**: HTTP-based communication between client and server

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python server/foxnest_server.py

# Use the client
python client/fox.py init
python client/fox.py push
```

## Commands

- `fox init` - Initialize a new repository
- `fox add <files>` - Add files to staging
- `fox commit -m "message"` - Commit changes
- `fox push` - Push changes to server
- `fox pull` - Pull changes from server
- `fox status` - Show repository status
- `fox log` - Show commit history
