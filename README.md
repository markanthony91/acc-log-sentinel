# acc_log_sentinel

Sistema centralizado de coleta de logs e telemetria para 134 lojas Burger King com agente Windows em Go e backend central em Python.

## Visão Geral

O projeto foi desenhado para resolver um problema operacional simples e recorrente: quando uma máquina da loja quebra, a equipe normalmente descobre tarde e sem contexto suficiente para agir rápido.

`acc_log_sentinel` cria uma camada mínima de observabilidade para essa frota:

- coleta Event Log do Windows
- detecta BSOD e eventos críticos
- mede CPU, RAM, disco e uptime
- registra índice de estabilidade do Windows
- envia dados para um backend central
- gera visão agregada da rede inteira
- produz alertas e relatórios com foco operacional

## Objetivos do MVP

- monitorar 134 lojas sem depender de mudanças do NOC em cada unidade
- receber payloads de telemetria via `HTTPS`
- manter retry local quando a conectividade falhar
- consolidar os dados em PostgreSQL
- gerar alertas agregados e relatório diário

## Arquitetura

### Na loja

Cada loja roda um agente local em Go como Windows Service.

Responsabilidades:

- ler Event Log de `System` e `Application`
- filtrar `Warning`, `Error` e `Critical`
- detectar BSOD por eventos conhecidos
- coletar métricas de recurso
- consultar índice de estabilidade
- salvar payload em SQLite local se o envio falhar

### No backend central

O backend central recebe os payloads, persiste os dados e gera a visão da frota.

Responsabilidades:

- expor API de ingestão
- validar payloads
- gravar eventos e métricas no PostgreSQL
- executar retenção diária
- detectar lojas silenciosas
- gerar relatório agregado diário

### Conectividade

A topologia preferencial para o MVP é:

- lojas enviando `POST` para um endpoint central único
- backend hospedado no homelab ou em VPS
- conectividade externa via `Cloudflare Tunnel` ou HTTPS público em VPS

`Tailscale Funnel` pode ser usado para validação, mas não é a opção principal de produção para a frota.

## Stack

| Componente | Tecnologia |
|-----------|-----------|
| Agente | Go 1.25+ |
| Service Windows | `kardianos/service` |
| Coleta de métricas | `gopsutil` |
| Buffer local | SQLite (`modernc.org/sqlite`) |
| Backend | Python 3.11 + FastAPI |
| Banco central | PostgreSQL |
| Relatórios | Resend |
| Testes Go | `go test` |
| Testes Python | `pytest` |

## Ambiente de Desenvolvimento

O projeto deve ser trabalhado preferencialmente via `nix-shell`.

```bash
cd acc_log_sentinel
nix-shell
```

Depois disso:

```bash
# agente Go
go test ./...
go build ./cmd/sentinel

# backend Python
cd server
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

## Estrutura Inicial

```text
acc_log_sentinel/
├── AGENTS.md
├── README.md
├── GEMINI.md
├── CLAUDE.md
├── docs/
│   └── plans/
├── cmd/
│   └── sentinel/
├── internal/
│   ├── buffer/
│   ├── collector/
│   ├── models/
│   └── sender/
└── server/
    ├── src/
    └── tests/
```

## Roadmap por Fases

### Fase 0 - Fundação do Projeto

- criar estrutura base do repositório
- definir contratos do payload
- documentar arquitetura, conectividade e retenção
- preparar convenções de testes e build

### Fase 1 - Agente Windows MVP

- implementar models do payload
- coletar Event Log com filtro por severidade
- coletar métricas de CPU, RAM, disco e uptime
- detectar BSOD
- obter reliability index
- enviar payload por HTTP
- persistir offline em SQLite local

### Fase 2 - Backend Central MVP

- criar API FastAPI de ingestão
- validar payload com Pydantic
- persistir `machines`, `events` e `metrics` em PostgreSQL
- inicializar banco automaticamente
- adicionar autenticação por token

### Fase 3 - Operação e Alertas

- implementar retenção de eventos e métricas
- detectar lojas silenciosas
- gerar relatório diário agregado
- criar buckets de risco por disco, RAM e reliability
- priorizar top offenders da frota

### Fase 4 - Implantação Piloto

- subir backend no homelab com Cloudflare Tunnel ou em VPS
- validar payloads reais de 2 a 5 lojas
- medir retry, latência e qualidade dos eventos
- ajustar thresholds antes do rollout completo

### Fase 5 - Escala para a Frota

- expandir para as 134 lojas
- acompanhar volume de ingestão e crescimento do banco
- ajustar retenção e índices
- adicionar grupos, regiões e visões gerenciais

### Fase 6 - Evolução Pós-MVP

- suporte a logs específicos de aplicativos
- WSL2 e serviços Linux locais
- dashboard web operacional
- alertas imediatos por WhatsApp ou Telegram
- rollups históricos e tendências

## Critérios de Sucesso

- todas as lojas conseguem enviar telemetria sem intervenção do NOC
- lojas silenciosas são detectadas automaticamente
- eventos críticos e BSOD aparecem no relatório diário
- banco permanece leve e com retenção controlada
- operação recebe visão agregada em vez de ruído bruto

## Decisões Atuais

- PostgreSQL continua sendo o banco central do projeto
- SQLite continua sendo apenas buffer local do agente
- Cloudflare Tunnel é a primeira opção para expor o backend no homelab
- túneis de desenvolvimento como `localtunnel` não serão usados em produção

## Próximos Passos Imediatos

1. criar o scaffold do agente Go
2. criar o scaffold do backend FastAPI
3. implementar o contrato do payload
4. validar ingestão ponta a ponta com payload simulado
