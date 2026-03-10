# Log Sentinel - Pilot Deployment

**Date:** 2026-03-10
**Status:** Active

## Scope

This phase prepares the backend for a controlled pilot with 2 to 5 stores.

## Deliverables

- containerized FastAPI backend
- PostgreSQL service with conservative settings
- optional Cloudflare Tunnel service via Docker Compose profile
- `.env` contract for local or homelab deployment
- pilot checklist for validation

## Runtime Model

### Local components

- `db`: PostgreSQL 16
- `api`: FastAPI + asyncpg

### Optional ingress

- `cloudflared`: enabled only when using Cloudflare Tunnel

## Pilot Success Criteria

- health endpoint reachable
- authenticated payload ingestion working
- data persisted in PostgreSQL
- daily report generation working
- retention command executable
- no dependency on NOC changes in the stores

## Commands

```bash
cd acc_log_sentinel
docker compose up -d db api
docker compose --profile cloudflare up -d
```

## Notes

- Use Cloudflare Tunnel as the first pilot ingress option for homelab
- Keep PostgreSQL private
- Expose only the API
