# 《父亲》单线交接编配（私用）

## 输出

- MIDI：`father_single_line_arrangement_melody_only.mid`
- 去前奏空拍 MIDI：`father_single_line_arrangement_melody_start.mid`
- 去前奏空拍、1.11×速度 MIDI：`father_single_line_arrangement_melody_start_1.11x.mid`
- 去前奏空拍、1.11×速度、尾 7 音删除 MIDI：`father_single_line_arrangement_melody_start_1.11x_last7_removed.mid`
- 输入副本：`input/父亲——筷子兄弟.mid`
- 输入 SHA-256：`589a40d6deb5a823eeaf2ee08dd4f801e41d7ec75edae601993e20584a3a4571`
- 输出 SHA-256：`0F9653E58E0E655FF6C690493C4DEA3BB1CF5FCCDBC7D4CE686478C9CB2BD2BC`
- 去前奏空拍输出 SHA-256：`77634DD687A04C78A3ED3E376EC6FBE113FB5FFCA0D2C219422C0DC01D5F69DC`
- 1.11× 输出 SHA-256：`231B55A6DB2A20CBC3040F4578337C213739C6638F50A1CC8E64E059C2B135B4`
- 尾 7 音删除输出 SHA-256：`7B272251B4B87DD8E9C9F8754A688DC05D461F93FEC97651B4B7C4E7F3E19C48`

## 来源与使用范围

- 页面来源：<https://www.midishow.com/zh-tw/midi/33600.html>
- 权利记录：社区上传 MIDI；许可/改编与再发布权利 `unknown`。
- 仅限用户确认的私用技术处理；不能据此公开、分享或再发布 MIDI、编配或后续播放器。

## 编配决定

- 基线：原 MIDI 的 `Voice`（轨 1）全部 442 个音符。
- 已确认交接：在 `Voice` 的 tick 69984–72960 空段，加入 `Piano`（轨 2）于 tick 70080–72936 的完整九音短句。
- 这是用户选择的 **single-line arrangement（单线交接编配）**，不是声称原 MIDI 中有一条完整的唯一旋律轨。
- 没有转调或移调（0 半音）；保留原始 4 个速度事件、4/4 节拍、E 大调和完整 292.703 秒时间轴。
- `melody_start` 变体经用户明确要求，移除了起始 15360 ticks（约 29.5 秒）的前奏空拍；其第一音符在 tick 0，时长为 263.164 秒。所有后续音符与速度事件等距前移，音符时值和速度均未改变。
- `melody_start_1.11x` 变体在上述去前奏版本基础上，将**每个**原有速度点乘以 1.11，并不压平速度图：72.150072 → 69.930070 → 64.380031 → 58.830047 BPM。其时长为 237.085 秒，音符的 tick 位置、时值、音高和交接决定均未改变。
- `melody_start_1.11x_last7_removed` 变体经用户明确要求，从上述 1.11× 版本的末尾删除 7 个 `Voice` 音符（D5、D#5、E5、E5、E5、G#5、F#5）。保留前 444 个音符、所有速度点及原有 237.085 秒时间轴；删除后的尾部静音亦被保留，以免改变其他时间关系。

## 验证

- 输出轨名：`single_line_arrangement`
- 音符 / 起音：451 / 451
- 音域：B3–C#6
- 最大同时音符数：1
- 重叠音符数：0
- Delta 三八度按键范围及不可演奏音符：未评估；本次只按所选 B 方案生成并验证单旋律 MIDI，未生成自动播放器或执行任何游戏输入。

详情见：

- `reports/track_report.md`：原文件审计。
- `reports/melody_strategy_review.md`：交接依据与用户选择。
- `reports/arrangement_report.json`：精确来源轨、九个音符和接缝记录。
- `reports/melody_audit.md`：输出严格单音审计。
- `reports/melody_start_arrangement_report.json`：去前奏空拍的精确时间轴变更记录。
- `reports/melody_start_audit.md`：去前奏空拍版本的严格单音审计。
- `reports/melody_start_1.11x_arrangement_report.json`：1.11× 速度图及精确编配记录。
- `reports/melody_start_1.11x_audit.md`：1.11× 版本的严格单音审计。
- `reports/melody_start_1.11x_last7_removed_arrangement_report.json`：所删的七个音符及完整速度图记录。
- `reports/melody_start_1.11x_last7_removed_audit.md`：尾 7 音删除版本的严格单音审计。

若后续明确需要 Delta 播放器，先根据游戏实际音域确认可演奏比例和所有越界音符；随后先运行生成播放器的 `--dry-run`，再决定是否进行实际输入。
