@echo off
title Connect to My Own Cloudflare Account
echo ==================================================
echo   HUBUNGKAN KE AKUN CLOUDFLARE & DOMAIN PRIBADI
echo ==================================================
echo.
echo Langkah-langkah:
echo 1. Login ke Dashboard Cloudflare Anda (https://dash.cloudflare.com)
echo 2. Buka Zero Trust -> Networks -> Tunnels
echo 3. Buat Tunnel Baru, masukkan domain Anda (misal: turnitin.domainanda.com)
echo 4. Salin TOKEN Tunnel dari Cloudflare Dashboard
echo.
set /p CLOUDFLARE_TOKEN=Masukkan Token Tunnel Cloudflare Anda: 

if "%CLOUDFLARE_TOKEN%"=="" (
    echo Token tidak boleh kosong!
    pause
    exit /b
)

echo Menjalankan Tunnel dengan Akun Cloudflare Anda...
cloudflared.exe tunnel run --token %CLOUDFLARE_TOKEN%
pause
