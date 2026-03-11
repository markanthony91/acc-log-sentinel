@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"

echo ============================================================
echo Log Sentinel - Setup do Agente Windows
echo ============================================================
echo.
echo Este script instala e inicia o servico do agente.
echo Execute como Administrador.
echo.

set "ROOT_DIR=%~dp0"
set "SENTINEL_EXE="
set "SERVICE_NAME=LogSentinelAiknow"

if exist "%ROOT_DIR%sentinel.exe" set "SENTINEL_EXE=%ROOT_DIR%sentinel.exe"
if not defined SENTINEL_EXE if exist "%ROOT_DIR%bin\sentinel.exe" set "SENTINEL_EXE=%ROOT_DIR%bin\sentinel.exe"

if not defined SENTINEL_EXE (
    echo [ERRO] Nao encontrei sentinel.exe neste pacote.
    echo.
    echo Caminhos verificados:
    echo   %ROOT_DIR%sentinel.exe
    echo   %ROOT_DIR%bin\sentinel.exe
    echo.
    echo Para operacao em loja, este pacote deve vir pronto com o binario.
    echo Solicite ao time tecnico a release Windows oficial.
    echo.
    pause
    exit /b 1
)

for %%I in ("%SENTINEL_EXE%") do set "SENTINEL_DIR=%%~dpI"
set "ENV_FILE=%SENTINEL_DIR%sentinel.env"
set "DEFAULT_BUFFER=%SENTINEL_DIR%data\buffer.db"

if not exist "%SENTINEL_DIR%data" mkdir "%SENTINEL_DIR%data" >nul 2>nul

echo Binario localizado em:
echo   %SENTINEL_EXE%
echo.

sc query "%SERVICE_NAME%" >nul 2>nul
if not errorlevel 1 (
    echo O servico ja existe nesta maquina.
    echo.
    echo Opcoes:
    echo   1. Atualizar configuracao e reiniciar o servico
    echo   2. Cancelar
    echo.
    set "ACTION=1"
    set /p ACTION=Escolha [1]: 
    if "%ACTION%"=="" set "ACTION=1"
    if not "%ACTION%"=="1" (
        echo Operacao cancelada.
        pause
        exit /b 0
    )
)

if exist "%ENV_FILE%" (
    echo Ja existe um arquivo de configuracao:
    echo   %ENV_FILE%
    echo.
    echo O setup vai sobrescrever este arquivo.
    echo.
)

echo Informe os dados do backend central.
echo.

set "API_ENDPOINT="
set /p API_ENDPOINT=Endpoint da API (ex.: https://log-sentinel.seudominio.com/api/v1/events): 
if "%API_ENDPOINT%"=="" (
    echo [ERRO] O endpoint nao pode ficar vazio.
    pause
    exit /b 1
)

set "API_TOKEN="
set /p API_TOKEN=Token da API: 
if "%API_TOKEN%"=="" (
    echo [ERRO] O token nao pode ficar vazio.
    pause
    exit /b 1
)

set "INTERVAL_MINUTES=60"
set /p INTERVAL_MINUTES=Intervalo em minutos [60]: 
if "%INTERVAL_MINUTES%"=="" set "INTERVAL_MINUTES=60"

> "%ENV_FILE%" echo SENTINEL_ENDPOINT=%API_ENDPOINT%
>> "%ENV_FILE%" echo SENTINEL_API_TOKEN=%API_TOKEN%
>> "%ENV_FILE%" echo SENTINEL_INTERVAL_MINUTES=%INTERVAL_MINUTES%
>> "%ENV_FILE%" echo SENTINEL_BUFFER_PATH=%DEFAULT_BUFFER%

echo.
echo Arquivo de configuracao gravado em:
echo   %ENV_FILE%
echo.

sc query "%SERVICE_NAME%" >nul 2>nul
if errorlevel 1 (
    echo Instalando servico Windows...
    "%SENTINEL_EXE%" install
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel instalar o servico.
        echo Tente abrir o Prompt como Administrador e executar novamente.
        pause
        exit /b 1
    )
    echo.
) else (
    echo Parando servico atual para aplicar a nova configuracao...
    "%SENTINEL_EXE%" stop >nul 2>nul
    echo.
)

echo Iniciando servico...
"%SENTINEL_EXE%" start
if errorlevel 1 (
    echo [ERRO] Nao foi possivel iniciar o servico.
    echo Tente abrir o Prompt como Administrador e executar novamente.
    pause
    exit /b 1
)

echo.
echo Verificando status...
"%SENTINEL_EXE%" status

echo.
echo Setup concluido.
echo Proximos passos:
echo   1. Confirmar se a loja tem saida HTTPS para o endpoint informado.
echo   2. Rodar "%SENTINEL_EXE%" run-once se precisar validar manualmente.
echo   3. Em caso de falha de rede, verificar o arquivo de buffer em:
echo      %DEFAULT_BUFFER%
echo.
pause
