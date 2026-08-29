@echo off
title Turnitin Engine + Cloudflare HTTPS Tunnel Watchdog
:loop
echo ======================================================================
echo   STARTING TURNITIN SERVER & CLOUDFLARE HTTPS TUNNEL
echo   Domain: https://cek.nasigorengmadura.web.id
echo ======================================================================

start "Cloudflare Tunnel Engine" /min cloudflared.exe tunnel --config config.yml run turnitin-app
python run.py
timeout /t 3
goto loop
