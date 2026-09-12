# 《贝加尔湖畔》单旋律 MIDI（私人流程）

## 来源与用途

- 原始文件：`input/贝加尔湖畔.mid`（用户从 MidiShow 正常取得）
- 来源页：<https://www.midishow.com/zh-tw/midi/42009.html>
- 权利/许可记录：社区上传 MIDI；下载页所示上传者条款为个人学习、编曲及 MIDI 技术研究，且原曲著作权仍须另行遵守。权利状态：`unknown` / Tier B。
- 预定用途：私人技术流程。未经覆盖改编与分享的许可，不得将本衍生 MIDI、播放器或乐谱公开发布/分发。

## 提取决定

- 已选来源轨：MIDI 轨道 7（MidiShow 页面列名“歌手”；源文件文字编码在通用解析中显示为乱码）。它使用 ch.5，原音色为 Piccolo。
- 源轨：213 个音符，C4--D6，含 6 处跨下一起音的连奏重叠；无同起音和弦，非 karaoke/guide 特征。
- 处理：`--track 7 --overlaps truncate --duration-mode source`。仅把每一处连奏的前音结束截断到下一音起点；保留源速度、音高、起始休止与后续休止。没有合并其他轨，没有从全编配取最高音，也没有移调或逐音换八度。

## 验证结果

- 输出：`beijiaerhu-pan_melody_only.mid`
- 输出 SHA-256：`fb704b857259f9607917b6b981321afb8f251b3cfd51d77e47bdc79dd4d30b77`
- 严格单音：`max_simultaneous_notes = 1`，`overlapping_note_count = 0`
- 音符/起音：213 / 213；音域 C4--D6；全局八度移位：0。
- 速度：单一约 62 BPM；输出时长 189.677 秒。没有为生成游戏播放器评估可演奏范围或跳过音符。

## 文件与下一步

- 输入审计：[reports/track_report.md](reports/track_report.md)
- 提取记录：[reports/extraction_report.json](reports/extraction_report.json)
- 输出审计：[reports/melody_audit.md](reports/melody_audit.md)

在生成任何游戏输入播放器前，请先试听 `beijiaerhu-pan_melody_only.mid` 并确认音乐性。播放器尚未生成，因此暂没有 `--dry-run` 命令。
