# 《当年情》已提供 MIDI：高音旋律层判断

分析日期：2026-09-12（Asia/Shanghai）  
输入：`input/当年情.mid`  
SHA-256：`c13aa6ee5edbf05d5d18ddab5da9be45ec3dd62dc99b13188cd0a8d92b07505f`

## 结论

“高音钢琴层”是最有力的主旋律候选：**通道 1（Bright Acoustic Piano）与通道 2（Acoustic Grand Piano）含完全相同的 63 个音符事件**，均严格单音（最大同时音 1），音域 A♯4–D♯6。这是一个明确的、可单独选择的旋律候选层；二者只是叠加音色，最终只能保留其中一个，不能把两个一起作为一条单旋律。

但不能把整个 Type 0 混合 MIDI 的“当刻最高音”当作旋律。通道 7（Rock Organ）也是严格单音、音域 G4–D♯6，含 49 个高音事件；它是另一条独立声部，尚未经过听感／乐谱复核来确定其音乐职能。高音钢琴的 63 个事件中，38 个在与风琴重叠时低于风琴；所以全局 `highest` 会在两个声部间跳换，变成新的编配，而不是可靠地恢复原旋律。

因此当前分类为：**候选通道 1 或 2 = `independent-melodic-part`（待听感／乐谱复核）**。可以作为私下技术审计的下一候选，但在没有明确许可时不应用于公开或再分发的衍生 MIDI／播放器。

## 审计事实

| 通道 | 程序 | 音符／起音 | 最大同时音 | 音域 | 判断 |
| --- | --- | ---: | ---: | --- | --- |
| 1 | Bright Acoustic Piano (1) | 63 / 63 | 1 | A♯4–D♯6 | 候选旋律层 |
| 2 | Acoustic Grand Piano (0) | 63 / 63 | 1 | A♯4–D♯6 | 与通道 1 完全重复；不另取 |
| 7 | Rock Organ (18) | 49 / 49 | 1 | G4–D♯6 | 另一条高音独立声部；不宜与钢琴按音高混选 |
| 3 | Drawbar Organ (16) | 74 / 33 | 3 | G3–G4 | 和弦性伴奏 |
| 4 | Fretless Bass (35) | 61 / 61 | 1 | G1–D♯3 | 低音伴奏 |
| 6 | Accordion (21) | 108 / 108 | 1 | G3–D♯4 | 中低声部伴奏 |
| 10 | Percussion | 161 / 111 | 2 | C2–C3 | 打击乐 |

文件整体为 Type 0、480 PPQ、4/4、约 79.97 BPM、42.025 秒；只有一个容器轨，混合了 8 个通道。整体包含 598 个音符、最大同时音 9，故不能直接按轨道提取。

## 已执行的选择

用户选择了**通道 1**。已单独导出其 63 个事件并重新审计：最大同时音为 1、重叠为 0、音域为 A♯4–D♯6。输出与审计分别见 `../dang-nian-qing_melody_only.mid`、[extraction_report.md](extraction_report.md) 和 [melody_audit.md](melody_audit.md)。没有采用“从全曲选最高音”的规则，也没有将通道 2 的重复音同时保留。

参见事实审计：[track_report.md](track_report.md) 与 [track_report.json](track_report.json)。
