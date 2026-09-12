# 《太阳照常升起》多轨主旋律单线改编（私人技术用途）

## 来源与权限

- **输入：** 用户提供的 `input/太阳照常升起.mid`。
- **输入 SHA-256：** `579063299d6052c9e4d4adf3d862c02453ae42c2ea6cbbc90e9993ff7e63d37f`。
- **来源页／授权：** 未由用户确认；权利状态 `unknown`。用户确认仅作私人技术使用。不得据此公开、上传或再分发 MIDI／衍生播放器。

## 输出

- **文件：** `taiyang-zhaochang-shengqi_single_line_arrangement.mid`
- **输出 SHA-256：** `a7d44d1a9fd2647f0c908776707030254715512eb80b0d1319a29c63bb2a05f5`
- **性质：** `single-line arrangement`，即依据已审阅的声部交接制作的单线改编；不是从原 MIDI 无损抽出的既有完整轨。
- **结果：** 268 个音符，C3–D6；`max_simultaneous_notes=1`、`overlapping_note_count=0`。
- **无空白尾段副本：** `taiyang-zhaochang-shengqi_single_line_trimmed.mid`。它在最后一个音符结束的 tick 134880（140.5 秒）结束；保留全部 268 个音符，仅移除了原文件由末尾元事件造成的约 44.5 秒静音。

## 已选择的旋律路线

1. 长号，轨 1：tick 480–33117，直接选择。
2. 高音弦乐，轨 4：tick 38880–88794；前段八度齐奏只保留上声部。
3. 大提琴，轨 6：tick 88800–129840；按用户选择的“以长笛收尾”方案，将最后 C4 从 tick 130560 截短至 129840。
4. 长笛，轨 7：tick 129840–134880，直接选择。

保留原文件的时间原点、速度图（120→127.66 BPM）、拍号（4/4→3/4）与调号变化（D minor→G minor→C minor）；未按全曲最高音抽取，未移调。尚未生成 Delta 播放器，故全局八度移位与不可演奏音符数量尚未评估。

## 证据与复现

- 结构审计：[track_report.md](reports/track_report.md)
- 旋律判断与交接选择：[analysis_report.md](reports/analysis_report.md)
- 改编路线与输出哈希：[arrangement_report.json](reports/arrangement_report.json)
- 输出复审：[melody_audit.md](reports/melody_audit.md) / [melody_audit.json](reports/melody_audit.json)
- 裁剪副本复审：[trimmed_melody_audit.md](reports/trimmed_melody_audit.md) / [trimmed_melody_audit.json](reports/trimmed_melody_audit.json)
- 可复现脚本：[build_selected_melody.py](scripts/build_selected_melody.py)
