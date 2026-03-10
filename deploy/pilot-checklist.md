# Log Sentinel Pilot Checklist

## Objetivo

Validar a operacao do backend central com 2 a 5 lojas antes do rollout completo.

## Topologia alvo

- `db` e `api` sobem via Docker Compose
- `cloudflared` e opcional no perfil `cloudflare`
- lojas fazem `POST` para o endpoint central unico

## Pre-requisitos

1. Copiar `server/.env.example` para `server/.env`
2. Preencher:
   - `API_SHARED_TOKEN`
   - `RESEND_API_KEY`
   - `EMAIL_SENDER`
   - `EMAIL_RECIPIENT`
   - `CLOUDFLARE_TUNNEL_TOKEN` se usar Cloudflare Tunnel
3. Confirmar que o dominio/tunnel do Cloudflare ja aponta para a API

## Subida local

```bash
cd acc_log_sentinel
docker compose up -d db api
docker compose ps
curl http://127.0.0.1:16100/api/v1/health
```

## Subida com Cloudflare Tunnel

```bash
cd acc_log_sentinel
docker compose --profile cloudflare up -d
```

## Validacao inicial

1. Verificar `GET /api/v1/health`
2. Enviar payload de teste autenticado
3. Confirmar insercao em `machines`, `events` e `metrics`
4. Rodar retencao sem efeito destrutivo relevante em base vazia
5. Gerar relatorio HTML local antes de enviar email

## Criterios do piloto

- ingestao recebida de pelo menos 2 lojas reais
- retry do agente funcionando quando endpoint fica indisponivel
- detecao de loja silenciosa em ate 2 janelas
- relatorio diario contendo top offenders e alertas de recurso
- nenhum crescimento anormal de CPU/RAM no homelab

## Medicoes minimas

- latencia media de ingestao
- quantidade de payloads recebidos por hora
- payloads perdidos ou reenviados
- total de eventos por loja por dia
- tamanho do banco apos 3 a 7 dias

## Proximo passo apos piloto

Se o piloto estiver estavel, expandir para um grupo maior e revisar thresholds de:

- disco
- RAM
- reliability
- janela de silencio
