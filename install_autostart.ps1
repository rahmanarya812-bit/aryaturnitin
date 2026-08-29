$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = Join-Path $startupFolder "TurnitinAutoStart.lnk"

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "d:\aryaturnitin\start_background.vbs"
$shortcut.WorkingDirectory = "d:\aryaturnitin"
$shortcut.Save()

Write-Host "SUCCESS: Windows AutoStart Shortcut Installed in Startup Folder!"
