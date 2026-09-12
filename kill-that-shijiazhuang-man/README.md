# 《杀死那个石家庄人》单旋律提取记录

- **原始页面：** https://www.midishow.com/en/midi/midi-midi-download-192154
- **权利／用途：** `unknown`（MidiShow 社区上传）；用户确认仅作私下用途。不得将本目录中的衍生 MIDI 作为获授权的公开或再分发版本。
- **原始文件：** `input/杀死那个石家庄人（单轨midi）.mid`
- **原始 SHA-256：** `0aee70f029977da56086a5c49d118c163eccfae51b09a0a45675498cbcc8de12`

## 提取决定

- 选定源轨：索引 `1`，名称 `Vocal`。
- 采用源时值，拒绝同起点和弦与重叠音；未进行选高／选低、截断、时值重建或前置休止裁剪。
- 输出：`kill-that-shijiazhuang-man_melody_only.mid`。

## 验证结果

- 输出 SHA-256：`3d867640834dcc78f3432241c29667edca9fe6a1308bf19cb2450b44e02e092e`
- 207 个音符；音域 A3–A4；93 BPM；PPQ 480。
- 严格单旋律：最大同时音 `1`；重叠音 `0`。
- 证据：[源轨审计](reports/track_report.md)、[提取报告](reports/extraction_report.json)、[输出审计](reports/melody_audit.md)。

未生成 Delta 播放器。

## 修剪版（私用改编）

- 输出：`kill-that-shijiazhuang-man_melody_trimmed.mid`
- 输出 SHA-256：`dbc63bb61a3f23cdcf5c18b215528a0948fda22fb7bdd2ea8842a0c17db3cc24`
- 删除前置休止 34,080 tick（45.806 秒），并删除 3 段分别为 17,040、16,800、30,240 tick 的长空白（22.903、22.581、40.645 秒）。
- 短乐句停顿均保留；修剪后时长为 161.613 秒。
- 复审结果：207 个音符、最大同时音 1、重叠音 0。证据：[空白删除报告](reports/rest_removal_report.json)、[修剪版审计](reports/trimmed_melody_audit.md)。

## 前半段休止压缩与尾音删除（私用改编）

- 输入：`input/杀死石家庄人.mid`（SHA-256 `dbc63bb61a3f23cdcf5c18b215528a0948fda22fb7bdd2ea8842a0c17db3cc24`）。
- 输出：`kill-that-shijiazhuang-man_melody_edited.mid`（SHA-256 `d4a90e6e5a29e9953b408f9b21055b485f58a77f20026d71d507276c5521b0ce`）。
- 将原时间线前 50% 内、完整位于该区间的 14 个正时值休止各压缩为原长度的一半，共删除 6,120 tick。
- 删除末尾音符，并在倒数第二个音结束处截断时间线；输出时长 151.452 秒。
- 复审结果：206 个音符、最大同时音 1、重叠音 0。证据：[编辑报告](reports/first_half_rests_and_last_note_edit_report.json)、[编辑版审计](reports/edited_melody_audit.md)。
