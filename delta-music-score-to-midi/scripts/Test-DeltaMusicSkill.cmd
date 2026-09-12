@echo off
chcp 65001>nul
setlocal
pushd "%~dp0.."
echo 此自检不会发送键盘或鼠标输入。
echo 如果缺少核心 MIDI 依赖 mido，它会通过 Python pip 从 PyPI 安装 mido。
choice /C YN /N /M "是否继续"
if errorlevel 2 (
  popd
  exit /b 0
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Test-DeltaMusicSkill.ps1" -InstallCoreDependency %*
set "exitCode=%ERRORLEVEL%"
popd
echo.
if not "%exitCode%"=="0" echo 自检未完成。请阅读上面的错误信息，或查看 docs\04-verify-and-troubleshoot.md。
pause
exit /b %exitCode%
