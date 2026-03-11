# AGENTS.md - acc_log_sentinel

Este arquivo orienta agentes de código trabalhando em `/home/marcelo/Sistemas/acc_log_sentinel`.

## Objetivo do Projeto

`acc_log_sentinel` é um sistema de observabilidade operacional para lojas Burger King com:

- agente Go rodando em Windows 11
- coleta de Event Log, BSOD, métricas e estabilidade
- envio periódico para backend central
- backend Python com API, retenção, agregação e relatórios
- alertas agregados para a frota inteira

## Direção Arquitetural

- **Agente:** Go, instalado como Windows Service
- **Backend:** Python 3.11 + FastAPI
- **Banco central:** PostgreSQL
- **Buffer local do agente:** SQLite com WAL
- **Entrega de relatórios:** Resend
- **Conectividade preferencial:** Cloudflare Tunnel no homelab ou VPS pública
- **Ambiente local:** `nix-shell`
- **Configuração local do agente:** `sentinel.env` ao lado do executável

## Estrutura Esperada

```text
acc_log_sentinel/
├── AGENTS.md
├── README.md
├── GEMINI.md
├── CLAUDE.md
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
└── docs/
    └── plans/
```

## Regras de Implementação

1. Sempre incluir `hostname` em logs, payloads e respostas úteis de API.
2. Portas do projeto devem ficar no range `15000-35000`.
3. O agente deve continuar funcional sem rede usando buffer local.
4. O backend deve priorizar visão agregada da frota, não alertas ruidosos por evento isolado.
5. Dados antigos devem ter retenção explícita desde o MVP.
6. PostgreSQL deve ser configurado de forma conservadora para homelab.
7. O projeto precisa continuar utilizável a partir de `nix-shell`.
8. Instalação Windows deve privilegiar operação simples para analistas juniores com `setup.bat` e `sentinel.env`.

## Convenções de Código

### Go

- Arquivos em camelCase
- Logs com prefixo `[LogSentinel]`
- Erros tratados explicitamente
- Testes em `*_test.go`
- Preferir interfaces pequenas e structs simples

### Python

- Arquivos em snake_case ou compatíveis com o padrão já adotado no projeto
- Logs com prefixo `[LogSentinel-API]` ou `[LogSentinel-Report]`
- `pytest` para testes
- Módulos separados para API, banco, retenção e relatório

## Contratos Importantes

### Payload do Agente

Campos mínimos:

- `hostname`
- `collected_at`
- `events`
- `metrics`
- `bsod_detected`

### Prioridades de Alerta

Alertas imediatos apenas para:

- loja silenciosa por 2 janelas
- BSOD
- disco crítico
- pico anormal de erros críticos

Todo o restante deve entrar no relatório agregado diário.

## Matriz de Responsabilidade

### CLI do Agente

Usar para:

- instalação e remoção do serviço
- start/stop/status
- diagnóstico local com `run-once`

Não usar para:

- consultas agregadas da frota
- leitura operacional centralizada

### CLI do Backend

Usar para:

- retenção
- geração manual de relatório
- execução por scheduler

Não usar para:

- substituir a API de ingestão
- virar interface principal para lojas

### API do Backend

Usar para:

- ingestão dos payloads das lojas
- healthcheck
- futuros endpoints de consulta central

Não usar para:

- operar o serviço Windows local
- substituir comandos de suporte do agente

## Fluxo de Trabalho

1. implementar em fatias pequenas
2. adicionar ou ajustar testes
3. validar build do agente
4. validar testes do backend
5. atualizar `README.md`, `GEMINI.md` e `CLAUDE.md` se a arquitetura mudar

## Prática de Repositório

Seguir o padrão observado em `projeto_fast_drive`:

- repositório Git dedicado por projeto
- branch principal `main`
- branch de desenvolvimento `develop`
- commits em Conventional Commits
- documentação de contexto sincronizada com o código
- criação de repositório remoto via `gh`

### Regras de Git

1. criar o repositório remoto com `gh repo create`
2. manter `origin/main` e `origin/develop`
3. após mudanças arquiteturais, atualizar `README.md`, `GEMINI.md` e `CLAUDE.md`
4. antes de commit, rodar os testes relevantes do projeto
5. se a mudança for funcional, registrar também impacto no roadmap quando necessário

### Versionamento

- usar versionamento semântico quando o projeto passar a ter releases formais
- `fix` incrementa patch
- `feat` incrementa minor
- mudanças quebrando compatibilidade incrementam major

## Não Fazer

- não transformar PocketBase no backend principal deste projeto sem decisão explícita
- não expor PostgreSQL publicamente
- não depender de túneis de desenvolvimento como `localtunnel` em produção
- não misturar vários modelos de deploy sem fechar uma opção principal
