[CmdletBinding()]
param(
    [switch]$InstallCoreDependency
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$skillPath = Join-Path $repoRoot ".agents\skills\delta-music-score-to-midi"
$requirements = Join-Path $repoRoot "requirements.txt"

foreach ($required in @("SKILL.md", "scripts", "references", "tests")) {
    if (-not (Test-Path -LiteralPath (Join-Path $skillPath $required))) {
        throw "Skill 文件不完整，缺少：$required"
    }
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $py) {
    $pythonCommand = $py.Source
    $pythonPrefix = @("-3")
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) {
        throw "没有找到 Python。请先安装 Python 3.10+，然后重新运行此脚本。"
    }
    $pythonCommand = $python.Source
    $pythonPrefix = @()
}

$pythonVersionText = (& $pythonCommand @pythonPrefix -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
if ($LASTEXITCODE -ne 0 -or [version]$pythonVersionText -lt [version]"3.10") {
    throw "需要 Python 3.10+；当前检测到：$pythonVersionText"
}

& $pythonCommand @pythonPrefix -c "import mido" 2>$null
if ($LASTEXITCODE -ne 0) {
    if (-not $InstallCoreDependency) {
        Write-Host "缺少核心依赖 mido。" -ForegroundColor Yellow
        Write-Host "请在 PowerShell 运行："
        Write-Host "  & '$PSCommandPath' -InstallCoreDependency"
        Write-Host "这会通过 pip 安装 requirements.txt 中的 mido，然后重新测试。"
        exit 2
    }
    & $pythonCommand @pythonPrefix -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) {
        throw "mido 安装失败。请检查 Python/pip 和网络后重试。"
    }
}

Write-Host "正在运行自动测试……" -ForegroundColor Cyan
& $pythonCommand @pythonPrefix -B -m unittest discover -s (Join-Path $skillPath "tests") -v
if ($LASTEXITCODE -ne 0) {
    throw "自动测试失败。请保存完整输出并在 GitHub Issue 中提交。"
}

Write-Host ""
Write-Host "自检通过：Skill 结构、Python、mido 和自动测试均正常。" -ForegroundColor Green
Write-Host "这不代表 AI 已经把某首真实乐谱抄对；真实曲目仍需按小节复核并先 dry-run。"
