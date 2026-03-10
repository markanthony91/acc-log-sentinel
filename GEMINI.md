# acc_log_sentinel - GEMINI.md
**Codinome: HERMES LOGOS**

`acc_log_sentinel` é o projeto de telemetria e monitoramento centralizado de logs Windows para a rede de lojas Burger King.

## Visão Geral

- **Agente:** Go 1.25+ em Windows Service
- **Backend:** Python 3.11 + FastAPI
- **Banco:** PostgreSQL central + SQLite local no agente
- **Conectividade:** Cloudflare Tunnel no homelab ou VPS pública
- **Objetivo:** observabilidade operacional leve para 134 lojas

## Funcionalidades Alvo

- [ ] coleta de Event Log `System` e `Application`
- [ ] filtro por `Warning`, `Error` e `Critical`
- [ ] detecção de BSOD
- [ ] métricas de CPU, RAM, disco e uptime
- [ ] reliability index do Windows
- [ ] retry offline com SQLite
- [ ] ingestão central em FastAPI
- [ ] persistência em PostgreSQL
- [ ] retenção automática
- [ ] relatório agregado diário
- [ ] detecção de lojas silenciosas

## Roadmap

### Fase 1 - Fundamentos
- [ ] scaffolding do repositório
- [ ] modelos de payload
- [ ] contrato de API
- [ ] documentação inicial

### Fase 2 - Agente
- [ ] Event Log
- [ ] métricas
- [ ] BSOD
- [ ] reliability
- [ ] sender
- [ ] buffer

### Fase 3 - Backend
- [ ] API de ingestão
- [ ] schema PostgreSQL
- [ ] autenticação
- [ ] persistência e queries

### Fase 4 - Operação
- [ ] retenção
- [ ] alertas agregados
- [ ] relatório diário
- [ ] piloto com poucas lojas

### Fase 5 - Escala
- [ ] rollout para 134 lojas
- [ ] tuning de thresholds
- [ ] visão por grupos e regiões

## Regras Arquiteturais

- `hostname` é obrigatório
- backend deve operar com footprint conservador
- PostgreSQL não deve ser exposto diretamente
- alertas precisam ser agregados
- conectividade deve evitar dependência do NOC loja a loja
