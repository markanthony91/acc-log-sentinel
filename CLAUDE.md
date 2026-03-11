# CLAUDE.md - acc_log_sentinel Context

Este arquivo fornece contexto operacional para trabalhar no `acc_log_sentinel`.

## Visão Geral do Projeto

**acc_log_sentinel** é um sistema de monitoramento centralizado para 134 lojas Burger King, composto por:

- **Agente:** Go 1.25+ rodando como Windows Service
- **Backend:** Python 3.11 + FastAPI
- **Banco de Dados:** PostgreSQL central
- **Buffer do Agente:** SQLite com WAL
- **Integrações:** Resend para relatórios; Cloudflare Tunnel ou VPS para conectividade

## Estrutura do Projeto

```text
acc_log_sentinel/
├── cmd/
│   └── sentinel/
├── internal/
│   ├── buffer/
│   ├── collector/
│   ├── models/
│   └── sender/
├── server/
│   ├── src/
│   └── tests/
├── docs/
│   └── plans/
├── README.md
├── AGENTS.md
├── GEMINI.md
└── CLAUDE.md
```

## Comandos Esperados

```bash
# Ambiente
nix-shell

# Go
go test ./...
go build ./cmd/...
GOOS=windows GOARCH=amd64 go build -o bin/sentinel.exe ./cmd/sentinel/

# Python
pytest server/tests/ -v
python -m compileall server/src
```

## Convenções

- logs Go com prefixo `[LogSentinel]`
- logs Python com prefixo `[LogSentinel-API]` ou `[LogSentinel-Report]`
- `hostname` em payloads, logs e respostas relevantes
- porta da API no range do workspace, preferencialmente `16100`

## Direção de Deploy

- backend central preferencial em homelab com `Cloudflare Tunnel`
- alternativa: VPS pública pequena com HTTPS
- `Tailscale Funnel` apenas para validação ou laboratório
- não usar `localtunnel` em produção

## Regras de Implementação

1. O agente precisa continuar operando sem rede.
2. O backend deve processar ingestão com pool pequeno e footprint conservador.
3. A retenção precisa existir desde o MVP.
4. Relatórios devem priorizar resumo da frota.
5. Alertas imediatos devem ser reservados a condições de alto sinal.

## Separação de Interfaces

- CLI do agente: operação local e suporte em loja
- CLI do backend: jobs operacionais e manutenção
- API do backend: integração entre agentes e central

Evitar duplicar a mesma responsabilidade nas três superfícies.

## Próximos Passos Sugeridos

- scaffold do módulo Go
- scaffold do backend Python
- testes do payload
- ingestão simulada
- piloto com 2 a 5 lojas
