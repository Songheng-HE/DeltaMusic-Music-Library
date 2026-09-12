# 输出文件与三角洲播放器

## 导入哪个文件？

| 文件名模式 | 是什么 | 是否导入播放器的 MIDI 导入界面 |
| --- | --- | --- |
| `*_melody_only.mid` | 最终严格单旋律 MIDI | **是** |
| `*_three_octave_player.py` | 独立自动按键脚本 | **否** |
| `reviewed_score.json` | 人工复核乐谱的中间数据 | 否 |
| `manifest.json` | 来源、哈希和处理记录 | 否 |
| `*_audit.json` / `*_report.json` | 质量与审计报告 | 否 |

一句话：播放器有“MIDI 导入”按钮时，选择 `*_melody_only.mid`。

## `.py` 文件到底是什么？

`*_three_octave_player.py` 是一份独立 Python 程序。它根据 MIDI 的时间轴，模拟预设的键盘/鼠标按键；它不是 MIDI，不能导入到 MIDI 导入界面。

运行它前：

1. 先检查你使用的游戏或播放器是否允许自动输入。
2. 先运行 `--dry-run`。这个模式只输出计划，不按任何键。
3. 核对默认键位映射是否与你自己的三角洲音乐播放器一致。
4. 真正运行时保持游戏窗口焦点；按 `F10` 应停止并释放按键。

默认运行不会发送输入，只会显示安全提示。先检查：

```powershell
py .\曲名_three_octave_player.py --dry-run
```

只有在你确认规则允许、窗口焦点正确且 dry-run 已核对后，才运行：

```powershell
py .\曲名_three_octave_player.py --play
```

程序会再要求你在控制台精确输入 `PLAY`。没有 `--play`、没有交互确认、或输入任何其他内容时，均不会发送键盘或鼠标输入。

如果 `py` 找不到，请让 Codex 帮你找到可用 Python，而不是随意下载不明脚本。

## 真实自动按键前的额外依赖

仅在你决定实际运行 `.py` 脚本时，才需要：

```powershell
py -m pip install -r requirements-player.txt
```

这会安装 `keyboard` 和 `pydirectinput`。只导入 MIDI 或运行 `--dry-run` 时不需要它们。

## 你应该怎样验收

在导入前要求 Agent 或自己确认：

- 审计报告里的 `max_simultaneous_notes = 1`。
- 审计报告里的 `overlapping_note_count = 0`。
- 若来自乐谱转写，所有事件均已人工视觉复核。
- 开头休止、重要停顿、重复段和声部选择没有被静默改掉。
- 没有被悄悄逐音符移八度；任何不可演奏音都被报告出来。

这些结果说明 MIDI 的结构通过检查；仍建议试听并按小节对照原谱。
