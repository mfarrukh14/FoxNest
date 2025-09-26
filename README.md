## FoxNest Project

This repository contains the FoxNest version control platform:

- Fox (CLI client) – lightweight Git-inspired local VCS with push/pull
- FoxNest Server (FastAPI + SQL backend) – central coordination + metadata store
- Admin / Archive Frontend (React + Vite) – repository visibility & domain fields (G1 Coordinator, Tested status, Instruction Manual PDF)

### Key Documents

- [FoxNest vs Git & GitHub Comparison](./COMPARISON.md)
- `installers/README.md` – platform-specific packaging

### Quick Start (CLI)

```f
fox init --username alice --repo-name demo
echo "Hello" > hello.txt
fox add hello.txt
fox commit -m "Initial commit"
fox set origin 192.168.15.237:5000
fox push
```

### Server
Runs on FastAPI (port 5000 by default) with SQLite fallback (PostgreSQL target). Provides JSON endpoints under `/api/`.

### Frontend
React/Vite dashboard for repository listing and editing custom metadata fields.

See the comparison document for strategic positioning and roadmap.
