# 《红凯之歌》单旋律 MIDI

输出文件：`red-kai-song_melody_only.mid`

- 来源：用户提供的单页简谱，存档于 `input/red-kai-song-score.png`；其 SHA-256 记录在 `input/source.sha256`。
- 权利记录：用户提供的社区编配谱，许可未知；本产物按私人技术用途保存，不应用于公开再分发。
- 节拍／速度：4/4，88 BPM（谱面打印值）。
- 实际路线：`A → B → C → C → A → B → C → D → E`，共 69 个小节实例。
- C7 与 D7 的最后一拍为用户确认的一拍休止。A1–A3、B1–B3、E1–E3 的页内空白拍处理已在 `reports/transcription_decisions.md` 明确记录。
- 音域：C3–E5；验证结果为 303 个音符、最大同时发音数 1、重叠音符数 0。

审计记录：

- `reports/transcription_report.json`：源文件哈希、展开路线与编译验证。
- `reports/melody_audit.md` 与 `reports/melody_audit.json`：成品 MIDI 的结构审计。
- `transcription/reviewed_score.json`：可复查、可再编译的逐小节转写数据。

复现编译：

```powershell
$python = 'python'  # 也可改成你自己安装的 Python 解释器路径
& $python .agents\skills\delta-music-score-to-midi\scripts\compile_score_midi.py red-kai-song\transcription\reviewed_score.json red-kai-song\red-kai-song_melody_only.mid --report red-kai-song\reports\transcription_report.json
& $python .agents\skills\delta-music-score-to-midi\scripts\midi_tools.py audit red-kai-song\red-kai-song_melody_only.mid --json red-kai-song\reports\melody_audit.json --markdown red-kai-song\reports\melody_audit.md
```
