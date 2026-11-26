@echo off
REM =====================================================================
REM install_deps.bat - Instala dependencias de sistema no Windows
REM FFmpeg, yt-dlp (via pip), Node.js (para yt-dlp JS runtime)
REM =====================================================================

setlocal enabledelayedexpansion

echo.
echo =====================================================================
echo  INSTALADOR DE DEPENDENCIAS - Windows
echo =====================================================================
echo.

REM ---------------------------------------------------------------------
REM Verificar se e administrador (necessario para winget/choco)
REM ---------------------------------------------------------------------
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [AVISO] Execute como Administrador para instalacao automatica completa.
    echo.
)

REM ---------------------------------------------------------------------
REM FFmpeg - via winget (Windows 10/11) ou download manual
REM ---------------------------------------------------------------------
echo [1/3] Verificando FFmpeg...
where ffmpeg >nul 2>&1
if %errorLevel% eq 0 (
    echo [OK] FFmpeg ja instalado: %~$PATH:ffmpeg
) else (
    echo [INFO] FFmpeg nao encontrado. Tentando instalar via winget...
    winget install --id Gyan.FFmpeg --source winget --accept-source-agreements --accept-package-agreements 2>nul
    if %errorLevel% eq 0 (
        echo [SUCESSO] FFmpeg instalado via winget.
    ) else (
        echo [AVISO] Falha no winget. Tentando Chocolatey...
        choco install ffmpeg -y 2>nul
        if %errorLevel% eq 0 (
            echo [SUCESSO] FFmpeg instalado via Chocolatey.
        ) else (
            echo [ERRO] Instalacao automatica falhou.
            echo.
            echo Por favor, instale o FFmpeg manualmente:
            echo 1. Acesse: https://www.gyan.dev/ffmpeg/builds/
            echo 2. Baixe "ffmpeg-git-full.7z" (ou "essentials")
            echo 3. Extraia e adicione a pasta 'bin' ao PATH do sistema
            echo.
            echo Pressione qualquer tecla para continuar mesmo assim...
            pause >nul
        )
    )
)

REM ---------------------------------------------------------------------
REM yt-dlp - via pip (ja gerenciado pelo script Python)
REM ---------------------------------------------------------------------
echo.
echo [2/3] Verificando yt-dlp (Python)...
python -c "import yt_dlp" 2>nul
if %errorLevel% eq 0 (
    echo [OK] yt-dlp ja instalado no ambiente Python.
) else (
    echo [INFO] yt-dlp nao encontrado. Sera instalado automaticamente pelo script Python.
    echo [INFO] Ou instale manualmente: python -m pip install -U yt-dlp
)

REM ---------------------------------------------------------------------
REM Node.js - necessario para extractor JS do yt-dlp (YouTube/Instagram)
REM ---------------------------------------------------------------------
echo.
echo [3/3] Verificando Node.js (para extractor JS do yt-dlp)... 
where node >nul 2>&1
if %errorLevel% eq 0 (
    echo [OK] Node.js ja instalado: %~$PATH:node
) else (
    echo [INFO] Node.js nao encontrado. Tentando instalar via winget...
    winget install --id OpenJS.NodeJS.LTS --source winget --accept-source-agreements --accept-package-agreements 2>nul
    if %errorLevel% eq 0 (
        echo [SUCESSO] Node.js instalado via winget.
        echo [AVISO] Reinicie o terminal para atualizar o PATH.
    ) else (
        echo [AVISO] Falha no winget. Tentando Chocolatey...
        choco install nodejs-lts -y 2>nul
        if %errorLevel% eq 0 (
            echo [SUCESSO] Node.js instalado via Chocolatey.
            echo [AVISO] Reinicie o terminal para atualizar o PATH.
        ) else (
            echo [AVISO] Instalacao automatica falhou.
            echo.
            echo Por favor, instale o Node.js manualmente (versao LTS):
            echo 1. Acesse: https://nodejs.org/
            echo 2. Baixe e instale a versao LTS
            echo 3. Reinicie o terminal
            echo.
        )
    )
)

echo.
echo =====================================================================
echo  Verificacao final...
echo =====================================================================
echo.

where ffmpeg >nul 2>&1 && echo [OK] FFmpeg: OK || echo [FALTA] FFmpeg: NAO ENCONTRADO
python -c "import yt_dlp; print('[OK] yt-dlp:', yt_dlp.version.__version__)" 2>nul || echo [FALTA] yt-dlp: NAO ENCONTRADO
where node >nul 2>&1 && echo [OK] Node.js: OK || echo [FALTA] Node.js: NAO ENCONTRADO

echo.
echo Se tudo estiver OK, voce pode executar: python main.py "URL"
echo.
pause