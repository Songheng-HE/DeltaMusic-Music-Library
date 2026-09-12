# 《我不难过》私用单线编配

## 输出

- `wobu-nanguo_single-line_arrangement.mid`：521 音符的单音 MIDI；**这是按用户确认制作的单线编配，不是对原文件独立旋律轨的无损提取。**
- 原始文件：`input/ff14_wobu-nanguo_piano.mid`；SHA-256 `98d9a8aee56cd5e6c61178c35bba8cd95ce803b14b2b0941ccad91b8b5c393e9`。

## 来源和用途

- 原始页面：https://www.midishow.com/en/midi/ff14-midi-download-196894
- 原始上传版本：`[FF14] 我不难过 钢琴精修`，上传者月怜雪。
- 权利状态：`unknown` / Tier B。页面的上传者 CC0 标注不能单独证明现代原作可公开改编或分发。
- 用户确认用途：private。不要公开或分享此衍生 MIDI，除非另行取得适用的授权。

## 处理决定

- 输入仅有一条未命名钢琴轨，含 1,224 音符、最多 6 音同时，不能直接选取左右手或 `Melody` 轨。
- 用户确认制作按声部交接的单线编配后，使用此文件专属的力度层（`note_on` velocity ≥93）作为候选旋律层；它有 521 音符，范围 A#3–C6，最大同时音数 2。
- 唯一的相邻音重叠按已审核的 `isolated-melody` 候选层截至下一起音。没有移调、没有逐音八度折叠、没有裁剪前置时间。
- 输出保持 64 BPM、4/4、E♭ 调标记和源时间原点。

## 验证状态

- 机械审计通过：最终文件 `max_simultaneous_notes = 1` 且 `overlapping_note_count = 0`。
- 当前环境没有 MIDI 音频渲染器；尚未完成听觉复核。请先在常规 MIDI 播放器试听，重点检查第 8 小节和旋律休止/交接处。试听确认前，不要据此生成游戏输入播放器。

## 证据文件

- `reports/track_report.md`：原始钢琴轨审计。
- `reports/analysis_decision.md`：结构判断、交接编配理由和限制。
- `reports/velocity_layer_selection.json`、`reports/velocity_layer_audit.md`：候选声部的生成和审计。
- `reports/extraction_report.json`、`reports/melody_audit.md`：最终单音输出的提取与验证。

可选听检方式：在你常用的 MIDI 播放器中打开 `wobu-nanguo_single-line_arrangement.mid`，与原 MIDI 对比聆听。若发现某个完整乐句漏掉或误入伴奏，请指出时间位置，我会按乐句而非逐音调整并保留变更记录。
