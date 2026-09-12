# Windows 安装、更新与目录说明

## 先选路线

| 路线 | 适合谁 | 需要复制文件吗 |
| --- | --- | --- |
| A：打开下载后的仓库 | 第一次使用、只想马上处理一首歌 | 不需要，**推荐** |
| B：全局安装 | 经常在不同项目中使用 | 双击一次安装脚本 |
| C：让 Codex 安装器安装 | 已熟悉 Codex 的用户 | 让 AI 执行安装 |

## 路线 A：不安装，直接使用（推荐）

1. 下载 ZIP 并解压。
2. 在 Codex 打开解压后的仓库根目录。
3. 输入 `$delta-music-score-to-midi`。

仓库根目录内已经有：

```text
.agents\skills\delta-music-score-to-midi\SKILL.md
```

Codex 从当前工作目录向上扫描 `.agents/skills`，所以只要打开根目录，Skill 就能被发现。这个方法不修改你的用户目录，也最容易更新：下载新版 ZIP、解压、打开新版根目录即可。

## 路线 B：全局安装一次

全局安装后，你在任何本地 Codex 项目中都可以调用此 Skill。

1. 解压本仓库。
2. 打开其中的 `scripts` 文件夹。
3. 双击 `Install-DeltaMusicSkill.cmd`。
4. 看见“安装完成”后，完全退出并重新打开 Codex。
5. 在任意项目的聊天框输入 `$delta-music-score-to-midi`。

安装目标为：

```text
C:\Users\你的用户名\.agents\skills\delta-music-score-to-midi
```

这不是 `.codex\skills`。这是 Codex 官方文档列出的用户级本地 Skill 目录。[官方说明](https://developers.openai.com/codex/skills)

脚本只复制本仓库内的 Skill 指令、脚本、参考资料和测试；它不安装 Python 包，也不发送键盘/鼠标输入。如果目标已有旧版本，脚本会把旧目录改名为带时间戳的备份，而不是直接删除。Skill 会根据已加载的 `SKILL.md` 实际位置定位自己的工具，因此全局安装后不需要项目目录中再有 .agents\skills 副本。

根目录里的双击自检和合成演示入口只属于“完整仓库”路线；全局安装后，请让 Codex 使用已安装 Skill 自身的 tests/ 做验证，或重新打开完整仓库运行双击自检。

双击入口使用 `-ExecutionPolicy Bypass`，但它只作用于这一次启动的本地 PowerShell 进程，不会永久修改 Windows 的执行策略。你可以先用记事本打开 `.ps1` 查看脚本内容；它不会联网或自动安装 Python 包。

### 手动复制（安装脚本无法运行时）

在 PowerShell 中、仓库根目录下运行：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
Copy-Item -Recurse `
  ".\.agents\skills\delta-music-score-to-midi" `
  "$env:USERPROFILE\.agents\skills\"
```

然后重启 Codex。

## 路线 C：用 Codex 的 Skill 安装器

在 Codex 中发送下面这段文字：

```text
使用 $skill-installer 从这个 GitHub 地址安装 Skill：
https://github.com/Songheng-HE/delta-music-score-to-midi/tree/main/.agents/skills/delta-music-score-to-midi
```

这是可选方法。它会下载公开仓库的该目录并安装到 `$CODEX_HOME/skills`（默认通常为 `~/.codex/skills`）。这和路线 B 复制到 `%USERPROFILE%\.agents\skills` 不同；两者都可用于 Codex，但不要把它们误认为同一个目录。安装完成后开一个新任务或重启 Codex。

## 更新

- 路线 A：下载/解压新版，打开新版仓库根目录。
- 路线 B：下载/解压新版后，再次双击 `Install-DeltaMusicSkill.cmd`；旧全局版本会保留为备份。
- 路线 C：再次让 `$skill-installer` 安装新版；如果它提示目标已存在，请按提示更新或先保留旧版备份。

## 卸载或回退

全局安装的目录在：

```text
%USERPROFILE%\.agents\skills\delta-music-score-to-midi
```

若不再需要，可以在文件资源管理器中把这个目录移动到回收站，然后重启 Codex。若更新后想回退，把自动生成的 `.backup-日期时间` 目录改回原名即可。先确认目录名无误再操作。
