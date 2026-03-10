# Log Sentinel - Initial Roadmap

**Date:** 2026-03-10
**Status:** Active

## Fase 0 - Fundação

- criar repositório e documentação base
- consolidar arquitetura e conectividade
- definir payload e convenções

## Fase 1 - Agente Windows

- models
- Event Log
- métricas
- BSOD
- reliability
- sender HTTP
- buffer SQLite
- service Windows

## Fase 2 - Backend Central

- config
- schema
- API FastAPI
- persistência PostgreSQL
- autenticação de ingestão

## Fase 3 - Operação

- retenção
- detecção de silêncio
- relatório diário agregado
- top offenders

## Fase 4 - Piloto

- backend exposto por Cloudflare Tunnel ou VPS
- validação com poucas lojas
- ajustes de thresholds

## Fase 5 - Escala

- rollout para toda a frota
- tuning de banco
- visão por região ou grupo
