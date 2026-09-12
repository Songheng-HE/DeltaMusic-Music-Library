# 验证、验收与常见问题

## 两种验证不是一回事

| 验证 | 它说明什么 | 它不说明什么 |
| --- | --- | --- |
| 自动自检 | 文件结构、Python、`mido` 和脚本能运行 | 某首真实乐谱一定抄对 |
| 真实曲目验收 | 当前曲目的旋律、节奏和播放路线可信 | 其他曲目必然同样简单 |

## 自动自检

双击：

```text
scripts\Test-DeltaMusicSkill.cmd
```

正常时会看到测试全部通过。双击脚本后会先询问你是否同意在缺少 `mido` 时通过 pip 安装它；按 `Y` 才会安装，按 `N` 不会安装任何包。

若你想在 PowerShell 中明确执行安装，打开仓库根目录后运行：

```powershell
& '.\scripts\Test-DeltaMusicSkill.ps1' -InstallCoreDependency
```

这个命令会通过正常的 Python pip 安装核心 MIDI 依赖，再跑测试。你需要 Python 3.10+；不要为了自检安装 `requirements-player.txt`，自动按键库不是核心转换所必需。

也可以双击：

```text
scripts\Run-Synthetic-Demo.cmd
```

它会用本仓库自制的无版权旋律完成一条端到端路线：创建 MIDI → 审计 → 提取 → 再审计 → 生成播放器 → `--dry-run`。输出在 `examples\synthetic\generated\run-时间戳-GUID`，不会被提交到 Git。这个双击演示只存在于完整仓库；全局安装只安装 Skill 本体与测试。

### 全局安装后的验证

如果你走的是全局安装或 `$skill-installer` 路线，根目录的双击自检脚本不会被复制过去。打开任意本地 Codex 项目后发送：使用 `$delta-music-score-to-midi` 运行已安装 Skill 自身的单元测试；若缺少 `mido`，先说明将安装的依赖并等我同意。Skill 会从已加载的 `SKILL.md` 实际目录定位 tests 和 requirements，不要求当前项目包含 `.agents`。

## 真实曲目验收清单

1. Agent 是否先展示了源和音轨/声部选择理由？
2. 是否拒绝对复杂钢琴、管弦或卡农总谱直接“全曲最高音提取”？
3. 是否保留了开头休止、重要停顿、重复和共同时间原点？
4. MIDI 是否是严格单旋律（最大同时音符数为 1，且无重叠）？
5. 乐谱转写是否列出了模糊符号，而不是猜测？
6. 你是否试听了 `*_melody_only.mid` 并与原谱逐小节比较？
7. 自动播放器是否先完成 `--dry-run`？

遇到复杂材料时，Skill 停下来要你确认是正确行为，不是失败。

## 常见问题

### `$` 菜单里没有 Skill

- 确认 Codex 打开的是仓库根目录，而不是 ZIP、父目录或 `.agents` 子目录。
- 确认路径中存在 `.agents\skills\delta-music-score-to-midi\SKILL.md`。
- 完全退出并重启 Codex。
- 若使用全局安装，确认目录是 `%USERPROFILE%\.agents\skills\delta-music-score-to-midi`。

### 提示找不到 Python

先安装来自 Python 官方渠道的 Python 3.10+，安装时勾选“Add Python to PATH”；或者让 Codex 使用其当前环境已配置的 Python。安装完成后关闭并重新打开 PowerShell。

### 提示没有 `mido`

运行：

```powershell
& '.\scripts\Test-DeltaMusicSkill.ps1' -InstallCoreDependency
```

若网络或公司策略不允许 pip，请把完整错误交给 Codex 或你的管理员；不要随意从陌生网站下载 `.whl` 或可执行文件。

### Python 播放器无法真实按键

先不要尝试规避问题。确认：

- 你已经成功运行 `--dry-run`；
- 你确认目标程序允许自动输入；
- `keyboard`、`pydirectinput` 已在运行该脚本的 Python 环境中安装；
- 目标窗口获得焦点，键位映射和权限正确。

如果目标程序不接受自动输入或其规则不允许，应停止自动输入，改用 MIDI 导入或手动按键提示。

### 为什么 Agent 不直接给我“最终 MIDI”？

因为它在避免把错误的音轨、模糊符号、重复段或伴奏音当作旋律。先做审计和待确认清单，最终能节省大量返工。
