# Delta Music Score to MIDI

把你**有权使用**的 MIDI、清晰简谱、五线谱 PDF 或乐谱图片，转换为可复核的单旋律 MIDI；也可以生成一个先 `--dry-run`、再选择是否实际运行的 Delta 三八度播放器脚本。

> 这是一个给 AI Agent 使用的 Skill，不是一个双击就能把任意歌曲“完美转谱”的普通软件。它会保留不确定之处、要求复核，并拒绝把整首编曲的最高音盲目当作主旋律。

## 零基础最快开始（推荐）

你不需要先把文件复制到某个神秘的系统目录。

1. 安装并登录 **Codex**。
2. 在 GitHub 页面点击 **Code → Download ZIP**，解压到任意普通文件夹；不要直接在压缩包内打开。
3. 在 Codex 中打开解压后的**仓库根目录**（能看到 `.agents` 文件夹的那一层）。
4. 在聊天输入框键入 `$`，选择 **Delta 乐谱与 MIDI 转换**，或直接输入 `$delta-music-score-to-midi`。
5. 上传你的 MIDI、PDF、图片或简谱，然后从下方复制对应提示词发送。

Codex 会从当前项目向上查找 `.agents/skills`；所以“打开本仓库根目录”就是最少操作的安装方式。Skill 未出现时重启 Codex 后再试。详见 [OpenAI 官方 Skills 文档](https://developers.openai.com/codex/skills)。

> 本页是 Codex 的完整本机流程。使用 ChatGPT 网页/手机、DeepSeek 或豆包时，请看 [其他 AI 的使用方式](docs/06-other-ai-agents.md)；它们不能默认读取你电脑里的本地路径，也不能控制你的电脑。

## 它能做什么

- 查找 3–8 个正规乐谱/MIDI 候选来源，并把 MidiShow 等来源明确标为“技术备选、权利未知”。
- 审计你自己提供的 MIDI，先找可解释的旋律音轨，再生成严格单旋律 MIDI。
- 把清晰的单旋律简谱、五线谱 PDF 或图片转成“人工逐项复核”的 MIDI；不把 OCR 或视觉识别结果当事实。
- 生成审计报告、来源/处理清单和可编辑的 Delta 三八度播放器 Python 文件。

## 它不会做什么

- 不会替你登录、付费、下载、绕过付费墙、DRM、反爬或访问限制。
- 不会承诺模糊、缺页、复杂多声部乐谱的自动转写正确。
- 不会默认从钢琴或管弦总谱“抽最高音”冒充主旋律。
- 不会在权利不明确时把原曲 MIDI、改编 MIDI 或播放器脚本说成可以公开发布。
- 不会绕过游戏规则或反作弊机制；自动按键只应在你确认允许的场景中使用。

## 复制提示词开始使用

### 我已经有 MIDI

```text
使用 $delta-music-score-to-midi 处理这个文件：
C:\完整路径\曲目.mid

先审计 MIDI、判断结构类型，并列出最可能的旋律候选及理由。
不要默认提取最高音；旋律可能由多个音轨交替演奏。

先把处理方案、风险和需要我决定的事项发给我；
等我明确确认后，再生成单旋律 MIDI、正式审计报告、Delta 播放器 Python 文件和 manifest。
最后只做 dry-run，不要发送真实键盘或鼠标输入。
```

### 我已经有 PDF、图片或简谱

```text
使用 $delta-music-score-to-midi 处理这个乐谱：
C:\完整路径\乐谱.pdf

这是我有权用于私人使用的资料。请先按页、谱表和小节建立 reviewed_score.json 草稿，
列出所有不确定的音高、时值、休止、临时记号、反复、连音线和八度标记。

不要把 OCR 或推断当作已确认事实，也不要编译 MIDI；
等我明确确认转录内容后，再生成单旋律 MIDI、审计报告和 Delta 播放器 Python 文件。
```

### 我还没有乐谱，先帮我找来源

```text
使用 $delta-music-score-to-midi，为《[曲名]》寻找适合提取单旋律的乐谱或 MIDI。

优先公开、授权清楚、容易复核的来源。
MidiShow 可以作为权利情况未知的技术备用方案，不要直接排除。

对每个候选只提供：原始页面、格式、费用或访问条件、授权/权利状态、
技术适用性和不确定点。
不要替我下载、登录、付费，或绕过任何限制。找到后停下，等我自行取得文件。
```

## 最重要：应该导入哪个文件？

| 文件 | 用途 | 是否导入播放器的 MIDI 导入界面 |
| --- | --- | --- |
| `*_melody_only.mid` | 最终单旋律 MIDI | **是，优先选这个** |
| `*_three_octave_player.py` | 独立的自动按键脚本 | 否，单独运行 |
| `reviewed_score.json` | 乐谱转写复核中间文件 | 否 |
| `manifest.json`、`*_audit.*`、`*_report.*` | 来源与质量报告 | 否 |

如果你的三角洲音乐播放器有“导入 MIDI”界面，请选择 `*_melody_only.mid`。Python 文件不是 MIDI，不能导入到 MIDI 导入界面。

## 一键全局安装（可选）

如果你想在**任何** Codex 项目中都能调用它：解压本仓库后，双击 `scripts\Install-DeltaMusicSkill.cmd`。它会把 Skill 安装到：

```text
C:\Users\你的用户名\.agents\skills\delta-music-score-to-midi
```

旧版本会先被移动为带时间戳的备份，不会直接删除。安装后重启 Codex；以后在任意项目输入 `$delta-music-score-to-midi` 即可。

也可以让 Codex 安装器完成此事：

```text
使用 $skill-installer 从这个 GitHub 地址安装 Skill：
https://github.com/Songheng-HE/delta-music-score-to-midi/tree/main/.agents/skills/delta-music-score-to-midi
```

它会下载公开仓库的该目录并安装到 `$CODEX_HOME/skills`（通常是 `~/.codex/skills`）；这与本仓库一键脚本使用的 `%USERPROFILE%\.agents\skills` 是两条不同但都可被 Codex 使用的安装路径。安装完成后开一个新任务或重启 Codex。

## 验证是否可用

在打开**完整仓库**的路线中，双击 `scripts\Test-DeltaMusicSkill.cmd`，或让 Codex 运行：

```text
使用 $delta-music-score-to-midi 运行本仓库的无版权自检示例。
不要发送真实键盘或鼠标输入。
请告诉我：Skill 是否被识别、Python/MIDI 依赖是否可用、自动测试是否通过、生成文件在哪里，以及我下一步应导入哪个文件。
```

首次双击自检或无版权演示时，脚本会先询问你是否允许通过 Python pip 安装核心依赖 `mido`；选 `Y` 才会安装。你需要本机已安装 Python 3.10+。如果只是让 Codex 处理自己的文件，通常由当前 Agent 环境处理依赖，不必先手动安装这些包。

全局安装或 `$skill-installer` 安装只提供 Skill 本体与测试，不包含仓库根目录的双击演示入口；要运行无版权演示，请使用“打开完整仓库”路线。

自动测试通过说明工具链可以运行，不等于 AI 已经把某首真实乐谱抄对。真实曲目仍应逐小节试听、对照原谱，并先运行播放器的 `--dry-run`。

## 文档导航

- [从这里开始：第一次使用](docs/00-start-here-zh-CN.md)
- [Windows 安装与更新](docs/01-install-codex-windows.md)
- [提示词模板库](docs/02-prompt-library.md)
- [输出文件与三角洲播放器](docs/03-output-and-delta-player.md)
- [验证、验收与排错](docs/04-verify-and-troubleshoot.md)
- [版权、安全与能力边界](docs/05-copyright-safety-limits.md)
- [ChatGPT、DeepSeek 与普通聊天 AI](docs/06-other-ai-agents.md)
- [普通聊天 AI 的通用提示词](docs/08-generic-chat-ai.md)
- [开发、测试与贡献](docs/07-developer-guide.md)

## 依赖

- 核心 MIDI 工具：Python 3.10+ 和 [`mido`](requirements.txt)。
- 只有实际运行生成的自动按键播放器时，才额外需要 [`keyboard` 与 `pydirectinput`](requirements-player.txt)。`--dry-run` 不需要这两个包。

## 许可证与音乐版权

本仓库采用 [MIT License](LICENSE)，仅覆盖本仓库的代码和文档；**不覆盖**你上传的乐谱、MIDI、录音、歌曲作品或由它们生成的音乐性内容。发布真实曲目或改编结果前，请自行确认相应权利和许可。

### 隐私提醒

本仓库脚本不包含遥测功能；但生成的 `manifest` 和审计/转写报告可能含有本机绝对路径、文件 SHA-256、曲名和来源 URL。公开分享这些产物前先审查并脱敏。你上传给 AI 平台的文件如何处理，则受该平台自己的隐私政策和当前会话权限约束。

## 贡献

欢迎贡献清晰的 Bug 报告、测试、文档和明确许可的合成示例。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。不要提交未确认授权的乐谱、MIDI、录音或真实歌曲产物。
