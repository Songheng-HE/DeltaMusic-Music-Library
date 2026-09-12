@echo off
chcp 65001>nul
setlocal
pushd "%~dp0.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-DeltaMusicSkill.ps1" %*
set "exitCode=%ERRORLEVEL%"
popd
echo.
if not "%exitCode%"=="0" echo 安装未完成。请阅读上面的错误信息，或查看 docs\01-install-codex-windows.md。
pause
exit /b %exitCode%
