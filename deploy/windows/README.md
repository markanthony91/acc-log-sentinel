# Windows Release e Instalador

Este diretório descreve como gerar a entrega Windows do `acc_log_sentinel`.

## Fluxo recomendado

1. gerar o binário Windows
2. montar o pacote de release
3. opcionalmente gerar um instalador `.exe` com Inno Setup

## Gerar pacote de release

Na raiz do projeto:

```bash
make package-windows-release
```

Isso produz:

- `dist/windows/acc_log_sentinel/`
- `dist/windows/acc_log_sentinel-windows-amd64.zip`

Conteúdo do pacote:

- `sentinel.exe`
- `setup.bat`
- `sentinel.env.example`
- `INSTALL-WINDOWS.txt`

## Gerar instalador com Inno Setup

Pré-requisito:

- Inno Setup 6 instalado na máquina Windows
- comando `ISCC.exe` disponível

Arquivo do instalador:

- [installer.iss](/home/marcelo/Sistemas/acc_log_sentinel/deploy/windows/installer.iss)

Fluxo:

1. gere primeiro o pacote com `make package-windows-release`
2. copie ou abra o repositório em uma máquina Windows
3. execute o compilador do Inno Setup apontando para `deploy/windows/installer.iss`

Exemplo:

```bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" deploy\windows\installer.iss
```

Saída esperada:

- `dist\installer\LogSentinelSetup.exe`

## Observações

- o operador de loja não deve instalar Go
- o pacote de loja deve sempre vir com `sentinel.exe` pronto
- o `setup.bat` foi desenhado para operação de campo, não para build
