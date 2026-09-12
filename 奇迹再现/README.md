# 《奇迹再现》私用单旋律 MIDI

## 范围与权利

- 输入是用户提供的 `<用户本机下载目录>\奇迹再现.mid`，项目内保留副本于 `input/奇迹再现_source.mid`。
- 该来源对应研究报告所列的权利状态 `unknown` 的社区 MIDI。它只可作为私下技术处理记录；不代表获准公开、分享、再分发或制作公开播放器。
- 原件 SHA-256：`07f9778b2ac2676d1602cf19405977c41ab944a172411ee86c21868f0379f0c4`。

## 输出

- 保留前置静音版本：`奇迹再现_melody_only.mid`（SHA-256 `b353caf49ed06d7e372d1249bbbcd7a9d12a0a61f3823d39a828790329c248fe`）。
- **从首音开始版本：`奇迹再现_melody_from_first_note.mid`**（SHA-256 `53a06475bce5e5c0de8b481b73462259727fe984ac43882513c58a03f4fd9e3b`）。
- **从首音开始且删除中间超长静音版本：`奇迹再现_melody_no_long_pause.mid`**（SHA-256 `09ad386880f2ea5a4ea1dfa59884d97ac6ac5104ebd140392fc83d28e2e83326`）。
- **提速版本：`奇迹再现_1.5x_240bpm.mid`**（SHA-256 `c3ce53673e042fe0d905656052acc9be07a2529c1e92253b9eb35a354be95562`）。
- **提速版本（1.3×）：`奇迹再现_1.3x_208bpm.mid`**（SHA-256 `992870abc5e0786ef920aaf782a3fd563de4eab9383ed0d80634dbb727ed0900`）。
- **1.3× 且短休止减半版本：`奇迹再现_1.3x_short_rests_halved.mid`**（SHA-256 `2dcb1de2920aef98ebd5bd0d32b1aacbb113c22cc3d069f4148991d51e8e0509`）。
- **1.3×、短休止减半且前 30 秒休止再减半版本：`奇迹再现_1.3x_first30s_rests_halved.mid`**（SHA-256 `d5930c3beb03fbe172de8c29e1cae788b4f76014b4c955650bda61d6b1f1a8e2`）。
- **1.17×、保留全部休止压缩的版本：`奇迹再现_1.17x_first30s_rests_halved.mid`**（SHA-256 `3e8e9909c3ea787b96d7a69d9662d33cac26a5c1659572b8e665a7f7032ff2c9`）。
- 三个版本均为 422 个音符、F#4–G#5、160 BPM、4/4；从首音开始版本裁去了 1063 ticks（约 4.152 秒）前置静音，首音位于 tick 0。
- 最后一个版本在此基础上删除了唯一显著的内部静音（tick 30528–42908；12,380 ticks、约 48.359 秒），总长为 166.883 秒；其余短休止均保留。
- 提速版本基于用户指定的 `奇迹再现.mid`，仅把单一速度事件从 160 BPM 改为 **240 BPM（1.5×）**；音符时间、音高和结构未变，时长从 166.883 秒降至 111.255 秒。
- 1.3× 版本同样基于 `奇迹再现.mid`，速度为 **208 BPM**（MIDI 精确值约 207.9997 BPM），时长 128.372 秒；音符、音高与单音结构不变。
- 短休止减半版本基于 1.3× 版本：把轨 1 中时长 96–192 ticks（约 1–2 个四分音符）的 24 处内部无声间隔各缩短一半，共移除 1,525 ticks；更长的停顿未改。速度仍为 208 BPM，时长 123.789 秒，422 个音符的单音结构不变。
- 最后一个版本在该文件基础上，将前 30 秒范围（208 BPM 时 tick 0–9984）内的 21 处内部休止各再缩短一半，其中包括仍偏长的 480 与 528 tick 休止；共再移除 934 ticks。30 秒后的休止保持不变，时长为 120.983 秒。
- 1.17× 版本保留全部上述休止压缩，只将速度调为 **187.2 BPM**（MIDI 精确值约 187.1999 BPM）；时长为 134.425 秒，仍为 422 个音符的严格单音 MIDI。
- 输出审计均通过：最大同时音符数 1、重叠数 0。

## 提取决定与证据

- 选定原件轨 6：`FL Keys (MIDI) (MIDI)`。保留静音版分类为 `independent-melodic-part`；从首音开始版经复核为 `isolated-melody`，因为其他轨没有同步音符。
- 两处重复同音 B4 的重叠以 `--same-onset highest --overlaps truncate` 作最小修复；没有进行全曲取最高音、移调或移除前置静音。
- 审计与提取详情见 `reports/track_report.md`、`reports/extraction_decisions.md`、`reports/extraction_report.json`、`reports/melody_audit.md`、`reports/first_note_extraction_report.json`、`reports/first_note_melody_audit.md`、`reports/internal_silence_removal.json`、`reports/no_long_pause_melody_audit.md`、`reports/tempo_1.5x_report.json`、`reports/tempo_1.5x_audit.md`、`reports/tempo_1.3x_report.json`、`reports/tempo_1.3x_audit.md`、`reports/short_rests_halved_report.json`、`reports/short_rests_halved_audit.md`、`reports/first30s_rests_halved_report.json`、`reports/first30s_rests_halved_audit.md`、`reports/tempo_1.17x_report.json` 与 `reports/tempo_1.17x_audit.md`。

未生成 Delta 自动播放器，也没有试听或确认乐曲版本；如需下一步，应先确认该结果符合你取得文件的私人使用范围。
