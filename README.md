# acc_log_sentinel

Plataforma centralizada de telemetria operacional para 134 lojas Burger King, com agente Windows em Go, backend central em FastAPI e visão agregada da frota.

## Resumo Executivo

`acc_log_sentinel` foi criado para reduzir o tempo entre um problema acontecer na loja e a operação central descobrir o que houve.

Hoje o projeto já cobre o núcleo do sistema:

- agente Go com coleta local e execução como Windows Service
- envio periódico de payloads por HTTP
- buffer SQLite local para períodos sem rede
- backend FastAPI com ingestão autenticada
- persistência central em PostgreSQL
- retenção de dados
- relatório agregado da frota
- endpoints de consulta operacional
- setup Windows simplificado para analistas juniores

O objetivo não é criar um SIEM completo. O objetivo é entregar observabilidade operacional suficiente para descobrir rapidamente:

- quais lojas estão silenciosas
- quais máquinas estão com erro crítico
- onde houve BSOD
- quais lojas estão com risco de disco, RAM ou instabilidade

## Problema que o Sistema Resolve

Em um ambiente distribuído de lojas, falhas locais normalmente chegam tarde ao time central. Muitas vezes o primeiro sinal vem por reclamação operacional, não por monitoramento.

Esse projeto cria um modelo simples:

1. a máquina da loja coleta os sinais locais mais importantes;
2. o agente envia isso para um backend central;
3. o backend consolida e resume a frota inteira;
4. a operação trabalha com alertas agregados, não com ruído bruto.

## Objetivos do Projeto

- monitorar a frota sem depender de mudanças do NOC em cada loja
- usar apenas tráfego de saída da loja para um endpoint central
- manter funcionamento mesmo com perda temporária de rede
- centralizar histórico e consulta operacional
- gerar resumo diário da frota com alto sinal
- manter baixo consumo local e footprint conservador no backend

## Estado Atual

Fases já implementadas:

- Fase 0: fundação do projeto e documentação base
- Fase 1: agente Windows MVP
- Fase 2: backend central MVP
- Fase 3: retenção e alertas agregados
- Fase 4: implantação piloto
- Fase 5 parcial: operação do agente como Windows Service e consultas básicas da frota

O que já funciona hoje:

- `POST /api/v1/events`
- `GET /api/v1/health`
- `GET /api/v1/fleet/summary`
- `GET /api/v1/machines/{hostname}`
- `python -m src.reporter`
- `python -m src.retention`
- `sentinel install|start|stop|status|run-once`
- `setup.bat` para instalação simplificada em Windows

## Arquitetura

### Visão Geral

```text
Loja Windows
  └─ acc_log_sentinel (Go)
     ├─ Event Log
     ├─ CPU / RAM / Disco / Uptime
     ├─ Reliability Index
     ├─ BSOD detection
     └─ SQLite buffer local
              |
              | HTTPS outbound
              v
Backend Central
  ├─ FastAPI
  ├─ PostgreSQL
  ├─ retenção
  ├─ relatório agregado
  └─ endpoints operacionais
              |
              v
Canal de entrega
  └─ Resend / email
```

### O que fica em cada camada

Na loja:

- agente Go
- coleta local de eventos e métricas
- buffer SQLite se o backend estiver indisponível

No backend central:

- API de ingestão
- PostgreSQL
- regras de retenção
- agregação da frota
- geração de relatório

Na nuvem:

- apenas o canal de entrega e, quando necessário, o mecanismo de exposição do backend
- exemplo: `Cloudflare Tunnel`

## Componentes do Sistema

### 1. Agente Windows

Responsabilidades:

- coletar Event Logs de `System` e `Application`
- filtrar eventos relevantes por severidade
- detectar BSOD
- coletar CPU, RAM, disco e uptime
- coletar índice de estabilidade
- montar payloads com `hostname`
- enviar ao backend central
- armazenar localmente quando o envio falhar

Características importantes:

- implementado em Go
- preparado para rodar como Windows Service com `kardianos/service`
- suporta execução pontual para diagnóstico com `run-once`
- suporta configuração local via `sentinel.env`

### 2. Buffer Local

Quando a loja perde conectividade, o agente não perde os dados imediatamente.

Ele grava payloads pendentes em SQLite:

- arquivo local simples
- WAL habilitado
- reenvio posterior quando a conexão volta

Isso evita depender de conectividade estável o tempo inteiro.

### 3. Backend Central

Responsabilidades:

- receber payloads autenticados
- validar estrutura dos dados
- persistir máquinas, eventos e métricas
- detectar lojas silenciosas
- agregar a saúde da frota
- gerar relatórios diários
- aplicar retenção para manter o banco leve

Stack:

- Python 3.11
- FastAPI
- asyncpg
- PostgreSQL

### 4. Relatório Agregado

O relatório não deve ser uma lista crua de eventos. Ele deve priorizar:

- quantas lojas estão reportando normalmente
- quantas estão silenciosas
- quantas tiveram erro crítico
- quantas apresentaram BSOD
- quais lojas concentram mais problemas

Esse é o modelo mais útil para operação central.

## Fluxo de Dados

1. O agente roda na loja em intervalo configurado.
2. Ele coleta eventos e métricas locais.
3. Monta um payload com `hostname`, `collected_at`, `events`, `metrics` e `bsod_detected`.
4. Tenta enviar via `HTTPS` para o backend central.
5. Se falhar, grava o payload no SQLite local.
6. No próximo ciclo, tenta reenviar o backlog antes do payload atual.
7. O backend persiste os dados e atualiza a visão agregada da frota.
8. Jobs operacionais executam retenção e relatório.

## Modelo de Conectividade

O sistema foi desenhado para evitar dependência do NOC nas lojas.

Modelo preferencial:

- a loja faz apenas tráfego de saída para um endpoint central em `HTTPS`
- o backend central fica no homelab ou em uma VPS
- o PostgreSQL fica privado
- somente a API é exposta

Opções aceitas:

- `Cloudflare Tunnel` no homelab
- VPS pública com HTTPS

Opções apenas para laboratório:

- `Tailscale Funnel`

Opções não recomendadas para produção:

- `localtunnel`
- túneis efêmeros de desenvolvimento

## Estrutura do Repositório

```text
acc_log_sentinel/
├── AGENTS.md
├── README.md
├── GEMINI.md
├── CLAUDE.md
├── shell.nix
├── setup.bat
├── sentinel.env.example
├── docker-compose.yml
├── deploy/
│   ├── pilot-checklist.md
│   └── windows/
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
    ├── tests/
    ├── Dockerfile
    ├── requirements.txt
    └── .env.example
```

## Ambientes e Ferramentas

### Desenvolvimento

O projeto deve ser trabalhado preferencialmente com `nix-shell`.

```bash
cd acc_log_sentinel
nix-shell
```

### Go

```bash
go test ./...
go build ./cmd/sentinel
GOOS=windows GOARCH=amd64 go build -o bin/sentinel.exe ./cmd/sentinel
```

### Python

```bash
cd server
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

### Docker

```bash
cd acc_log_sentinel
cp server/.env.example server/.env
docker compose up -d db api
curl http://127.0.0.1:16100/api/v1/health
```

### Release Windows

```bash
make package-windows-release
```

Isso gera:

- `dist/windows/acc_log_sentinel/`
- `dist/windows/acc_log_sentinel-windows-amd64.zip`

Opcionalmente, o time técnico pode gerar um instalador Windows com Inno Setup usando [installer.iss](/home/marcelo/Sistemas/acc_log_sentinel/deploy/windows/installer.iss).

## Contrato do Payload

Campos principais:

- `hostname`
- `collected_at`
- `events`
- `metrics`
- `bsod_detected`

Esse contrato é a base entre loja e central. `hostname` é obrigatório para correlação operacional.

## Endpoints da API

Atuais:

- `POST /api/v1/events`
- `GET /api/v1/health`
- `GET /api/v1/fleet/summary`
- `GET /api/v1/machines/{hostname}`

Papéis:

- ingestão de payloads das lojas
- healthcheck operacional
- resumo agregado da frota
- detalhe por máquina

## Operação do Agente

O agente suporta dois modos: diagnóstico e serviço.

### Diagnóstico

```bash
go run ./cmd/sentinel run-once
LOG_SENTINEL_STDOUT=1 go run ./cmd/sentinel run-once
```

### Serviço

```bash
go run ./cmd/sentinel install
go run ./cmd/sentinel start
go run ./cmd/sentinel status
go run ./cmd/sentinel stop
go run ./cmd/sentinel uninstall
```

### Configuração do Agente

Variáveis aceitas:

- `SENTINEL_ENDPOINT`
- `SENTINEL_API_TOKEN`
- `SENTINEL_BUFFER_PATH`
- `SENTINEL_INTERVAL_MINUTES`

O agente também carrega automaticamente `sentinel.env`:

- primeiro no diretório atual
- depois no diretório do executável

Isso é importante para o Windows Service, porque a configuração fica local ao pacote instalado.

## Instalação em Windows para Analistas Juniores

O fluxo recomendado em loja é usar um pacote com:

- `sentinel.exe`
- `setup.bat`
- `sentinel.env.example`

### O que o `setup.bat` faz

- localiza `sentinel.exe`
- cria a pasta `data\`
- solicita endpoint, token e intervalo
- grava `sentinel.env`
- instala o serviço
- inicia o serviço
- mostra o status ao final

Ele não tenta instalar Go nem compilar o projeto. Esse trabalho fica com o time técnico durante a geração da release.

### Passo a passo

1. Baixar o pacote para uma pasta local, por exemplo `C:\Aiknow\acc_log_sentinel`.
2. Abrir `Prompt de Comando` como Administrador.
3. Entrar na pasta do projeto.
4. Executar `setup.bat`.
5. Informar a URL da API central.
6. Informar o token da API.
7. Informar o intervalo de coleta.
8. Confirmar o status do serviço.

### O que é necessário para funcionar

- o backend central precisa estar online
- a loja precisa ter saída para `HTTPS`
- o token precisa ser válido
- a instalação deve ser feita com privilégios de administrador

### Arquivos gerados localmente

- `sentinel.env`
- `data\buffer.db`

### Comandos de suporte local

```bat
sentinel.exe status
sentinel.exe run-once
sentinel.exe stop
sentinel.exe start
```

## Empacotamento para Distribuição

O fluxo de distribuição recomendado é:

1. gerar `sentinel.exe` para Windows
2. montar o pacote zipado de release
3. opcionalmente gerar `LogSentinelSetup.exe`

Arquivos criados para isso:

- [package_windows_release.sh](/home/marcelo/Sistemas/acc_log_sentinel/scripts/package_windows_release.sh)
- [INSTALL-WINDOWS.txt](/home/marcelo/Sistemas/acc_log_sentinel/deploy/windows/INSTALL-WINDOWS.txt)
- [installer.iss](/home/marcelo/Sistemas/acc_log_sentinel/deploy/windows/installer.iss)
- [deploy/windows/README.md](/home/marcelo/Sistemas/acc_log_sentinel/deploy/windows/README.md)

Isso separa claramente:

- operação de loja: instalar e configurar
- time técnico: build, empacotamento e geração do instalador

## Operação do Backend

### API

Subida local:

```bash
cd acc_log_sentinel
cp server/.env.example server/.env
docker compose up -d db api
```

### Relatório

```bash
cd acc_log_sentinel
docker compose exec -T api python -m src.reporter
```

### Retenção

```bash
cd acc_log_sentinel
docker compose exec -T api python -m src.retention
```

## Estratégia de Alertas

O sistema foi pensado para evitar ruído.

Alertas imediatos devem ser reservados para:

- loja silenciosa por duas janelas
- BSOD
- disco crítico
- pico anormal de erros críticos

Todo o restante deve ir para resumo agregado diário.

## Critérios de Sucesso

- as lojas enviam payload sem depender do NOC
- falhas temporárias de rede não causam perda imediata dos dados
- a operação sabe quais lojas estão silenciosas
- eventos críticos e BSOD aparecem de forma agregada
- o PostgreSQL permanece com footprint controlado
- o time central consegue priorizar lojas com maior risco

## Testes

Validações já executadas no projeto:

- `go test ./...`
- `go build ./cmd/sentinel`
- build cruzado Windows do agente
- `pytest` no backend
- integração local com `docker compose`
- smoke de ingestão ponta a ponta

## Roadmap

### Fase 0 - Fundação

- estrutura do repositório
- documentação base
- decisões de arquitetura

### Fase 1 - Agente Windows MVP

- models
- coleta de Event Log
- métricas
- BSOD
- reliability
- sender HTTP
- buffer SQLite
- Windows Service

### Fase 2 - Backend Central MVP

- FastAPI
- schema inicial
- PostgreSQL
- autenticação de ingestão

### Fase 3 - Operação

- retenção
- detecção de lojas silenciosas
- relatório agregado
- top offenders

### Fase 4 - Piloto

- `docker-compose.yml`
- `Dockerfile`
- checklist de piloto
- opção com `Cloudflare Tunnel`

### Fase 5 - Escala

- rollout para 134 lojas
- visão por região e grupo
- tuning de retenção e índices
- observabilidade do próprio backend

### Fase 6 - Evolução

- dashboard web operacional
- alertas adicionais por mensageria
- suporte a novas fontes de log
- históricos e tendências

## Decisões Arquiteturais Atuais

- PostgreSQL é o banco central do sistema
- SQLite é somente buffer local do agente
- `Cloudflare Tunnel` é a primeira opção para expor o backend no homelab
- `Tailscale Funnel` fica restrito a validação e laboratório
- o backend continua em FastAPI, não em PocketBase

## Referências Internas

- [AGENTS.md](/home/marcelo/Sistemas/acc_log_sentinel/AGENTS.md)
- [CLAUDE.md](/home/marcelo/Sistemas/acc_log_sentinel/CLAUDE.md)
- [pilot-checklist.md](/home/marcelo/Sistemas/acc_log_sentinel/deploy/pilot-checklist.md)
- [2026-03-10-log-sentinel-roadmap.md](/home/marcelo/Sistemas/acc_log_sentinel/docs/plans/2026-03-10-log-sentinel-roadmap.md)
- [2026-03-10-log-sentinel-pilot.md](/home/marcelo/Sistemas/acc_log_sentinel/docs/plans/2026-03-10-log-sentinel-pilot.md)
