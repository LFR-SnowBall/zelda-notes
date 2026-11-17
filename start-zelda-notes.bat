@echo off
title Zelda Notes — Purah Pad Companion
cd /d "%~dp0"

REM 1. Usar el runtime portable oficial embebido si existe (Zero-Install)
if exist "%~dp0runtime\python.exe" (
    "%~dp0runtime\python.exe" server.py
    goto end
)

REM 2. Fallback a Python del sistema en PATH
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python server.py
    goto end
)

REM 3. Fallback a Python de TotK-Recomp si esta instalado
if exist "%LOCALAPPDATA%\Programs\TotK-Recomp\python\python.exe" (
    "%LOCALAPPDATA%\Programs\TotK-Recomp\python\python.exe" server.py
    goto end
)

REM 4. Auto-descarga en 5 segundos del runtime portable oficial si no existe nada
echo [INFO] No se detecto Python instalado en el sistema.
echo [INFO] Descargando entorno portable oficial de Python (10 MB, sin instalacion)...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%~dp0python-embed.zip' -UseBasicParsing; Expand-Archive -Path '%~dp0python-embed.zip' -DestinationPath '%~dp0runtime' -Force; Remove-Item -Path '%~dp0python-embed.zip' -Force"

if exist "%~dp0runtime\python.exe" (
    echo [OK] Entorno portable configurado con exito.
    "%~dp0runtime\python.exe" server.py
    goto end
)

echo [ERROR] No se pudo iniciar el servidor.
pause

:end
