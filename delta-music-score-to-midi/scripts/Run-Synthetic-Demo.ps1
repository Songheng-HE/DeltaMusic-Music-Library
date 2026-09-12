[CmdletBinding()]
param(
    [switch]$InstallCoreDependency
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$skillRoot = Join-Path $repoRoot ".agents\skills\delta-music-score-to-midi"
$exampleRoot = Join-Path $repoRoot "examples\synthetic"
$requirements = Join-Path $repoRoot "requirements.txt"

$py = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $py) {
    $pythonCommand = $py.Source
    $pythonPrefix = @("-3")
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) {
        throw "没有找到 Python。请先安装 Python 3.10+。"
    }
    $pythonCommand = $python.Source
    $pythonPrefix = @()
}

$pythonVersionText = (& $pythonCommand @pythonPrefix -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
if ($LASTEXITCODE -ne 0 -or [version]$pythonVersionText -lt [version]"3.10") {
    throw "需要 Python 3.10+；当前检测到：$pythonVersionText"
}

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory)]
        [string]$Step,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $pythonCommand @pythonPrefix @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Step 失败（Python 退出码：$LASTEXITCODE）。"
    }
}

& $pythonCommand @pythonPrefix -c "import mido" 2>$null
if ($LASTEXITCODE -ne 0) {
    if (-not $InstallCoreDependency) {
        Write-Host "缺少 mido。请运行：" -ForegroundColor Yellow
        Write-Host "  & '$PSCommandPath' -InstallCoreDependency"
        exit 2
    }
    & $pythonCommand @pythonPrefix -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) { throw "mido 安装失败。" }
}

$runRoot = Join-Path $exampleRoot ("generated\run-" + (Get-Date -Format 'yyyyMMdd-HHmmssfff') + "-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null

$inputMidi = Join-Path $runRoot "synthetic-demo-input.mid"
$trackReport = Join-Path $runRoot "track_report.json"
$trackMarkdown = Join-Path $runRoot "track_report.md"
$melodyMidi = Join-Path $runRoot "synthetic-demo_melody_only.mid"
$extractionReport = Join-Path $runRoot "extraction_report.json"
$melodyAudit = Join-Path $runRoot "melody_audit.json"
$melodyMarkdown = Join-Path $runRoot "melody_audit.md"
$player = Join-Path $runRoot "synthetic-demo_three_octave_player.py"
$manifest = Join-Path $runRoot "manifest.json"

Write-Host "创建无版权合成 MIDI……" -ForegroundColor Cyan
Invoke-PythonStep "创建无版权合成 MIDI" (Join-Path $exampleRoot "create_demo_midi.py") $inputMidi

Write-Host "审计、提取并构建演示结果……" -ForegroundColor Cyan
Invoke-PythonStep "审计合成 MIDI" (Join-Path $skillRoot "scripts\midi_tools.py") audit $inputMidi --json $trackReport --markdown $trackMarkdown
Invoke-PythonStep "提取单旋律" (Join-Path $skillRoot "scripts\midi_tools.py") extract $inputMidi $melodyMidi --track "Demo Melody" --report $extractionReport
Invoke-PythonStep "审计单旋律输出" (Join-Path $skillRoot "scripts\midi_tools.py") audit $melodyMidi --json $melodyAudit --markdown $melodyMarkdown
Invoke-PythonStep "生成演示播放器" (Join-Path $skillRoot "scripts\build_delta_player.py") $melodyMidi $player --song-title "Synthetic Demo" --manifest $manifest --audit-report $melodyAudit --extraction-report $extractionReport --source-page "synthetic example bundled with this repository" --license "CC0-1.0 synthetic example" --intended-use private

Write-Host "运行播放器 dry-run（不会发送真实按键或鼠标输入）……" -ForegroundColor Cyan
Invoke-PythonStep "播放器 dry-run" $player --dry-run

Write-Host ""
Write-Host "演示成功。输出目录：$runRoot" -ForegroundColor Green
Write-Host "可导入 MIDI 的文件：$melodyMidi"
Write-Host "没有发送任何真实键盘或鼠标输入。"
