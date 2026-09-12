[CmdletBinding()]
param(
    [string]$DestinationRoot = (Join-Path $HOME ".agents\skills")
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$skillName = "delta-music-score-to-midi"
$source = Join-Path $repoRoot ".agents\skills\$skillName"
$destination = Join-Path $DestinationRoot $skillName

if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md") -PathType Leaf)) {
    throw "找不到 Skill 源文件：$source"
}

$sourceFull = (Resolve-Path -LiteralPath $source).Path.TrimEnd('\', '/')
$destinationFull = [System.IO.Path]::GetFullPath($destination).TrimEnd('\', '/')
if (
    $sourceFull.Equals($destinationFull, [System.StringComparison]::OrdinalIgnoreCase) -or
    $destinationFull.StartsWith($sourceFull + "\\", [System.StringComparison]::OrdinalIgnoreCase) -or
    $sourceFull.StartsWith($destinationFull + "\\", [System.StringComparison]::OrdinalIgnoreCase)
) {
    throw "安装目标不能与本仓库 Skill 源目录重叠：$destinationFull"
}

New-Item -ItemType Directory -Path $DestinationRoot -Force | Out-Null
$staging = Join-Path $DestinationRoot (".$skillName.staging-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $staging | Out-Null

foreach ($item in @("SKILL.md", "agents", "scripts", "references", "tests", "requirements.txt")) {
    $from = Join-Path $source $item
    if (-not (Test-Path -LiteralPath $from)) {
        throw "安装包缺少必要内容：$from"
    }
    Copy-Item -LiteralPath $from -Destination (Join-Path $staging $item) -Recurse -Force
}

if (-not (Test-Path -LiteralPath (Join-Path $staging "SKILL.md") -PathType Leaf)) {
    throw "暂存安装包校验失败：$staging"
}

$backup = $null
try {
    if (Test-Path -LiteralPath $destination) {
        $backup = "$destination.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Move-Item -LiteralPath $destination -Destination $backup
    }
    Move-Item -LiteralPath $staging -Destination $destination
} catch {
    if ($null -ne $backup -and -not (Test-Path -LiteralPath $destination) -and (Test-Path -LiteralPath $backup)) {
        Move-Item -LiteralPath $backup -Destination $destination
    }
    throw
}

if ($null -ne $backup) {
    Write-Host "已保留旧版本备份：$backup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "安装完成。" -ForegroundColor Green
Write-Host "Skill 位置：$destination"
Write-Host ""
Write-Host "下一步："
Write-Host "1. 完全关闭后重新打开 Codex。"
Write-Host "2. 新建或打开任意本地项目。"
Write-Host "3. 在聊天框输入：`$delta-music-score-to-midi"
Write-Host ""
Write-Host "提示：本安装脚本不安装 Python 依赖，也不发送任何键盘/鼠标输入。"
