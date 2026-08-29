@echo off
title Cloudflare Tunnel Launcher for Turnitin
echo ==================================================
echo   TURNING TURNITIN APPLICATION PUBLIC ONLINE
echo   Connecting to Cloudflare Tunnel (HTTPS)...
echo ==================================================
echo.

if not exist "cloudflared.exe" (
    echo Downloading Cloudflare Tunnel client...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
)

echo Starting HTTPS Public Tunnel on http://localhost:8000 ...
cloudflared.exe tunnel --url http://localhost:8000
pause
