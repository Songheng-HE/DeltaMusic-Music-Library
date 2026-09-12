# Canon per 3 Violini e Basso — B 版主题交接试听候选

- 用户选择：B 版“主题交接”候选。
- 输出：`pachelbel-canon-in-d_theme_handoff_B_candidate.mid`
- 来源：用户提供 ZIP 中的 `violin_one_part.mid`、`violin_two_part.mid`、`violin_three_part.mid`；原件保留在 `input/mutopia-2047/`。
- 本产物是为试听制作的**新单线编排**，不是原总谱中的某一条原始声部；未生成 Delta 播放器。

## 选择规则

1. 从第 3 小节的首次 Violin I 进入开始，保留原曲前两小节的休止。
2. 把 4/4 总谱切成连续的两小节窗口（每窗 3072 ticks）。
3. 每个窗口比较 Violin I、II、III 在窗口内的**起音数**；选起音数最高者，表示该句更具连续旋律活动。
4. 起音数相同则比较覆盖时值；仍相同则保持上一个窗口的声部。仅在开头没有前一声部时按 I、II、III 的顺序决定。
5. 只取入选声部在该窗口内的音符。跨窗口持续的音会在交接边界截断并重新起音；这保留原音高和绝对时间，但产生 13 次明确可审计的重新起音。

这不是逐音选最高音，也不改变任何音高、速度、拍号、调号或总时长。

## 交接表

| 小节 | 选定声部 |
| --- | --- |
| 3–14 | Violin I |
| 15–16 | Violin II |
| 17–18 | Violin III |
| 19–22 | Violin I |
| 23–24 | Violin II |
| 25–26 | Violin III |
| 27–36 | Violin I |
| 37–38 | Violin II |
| 39–42 | Violin III |
| 43–46 | Violin I |
| 47–48 | Violin II |
| 49–50 | Violin III |
| 51–52 | Violin II |
| 53–57 | Violin I |

## 复审结果

- MIDI Type 1，PPQ 384，D 大调，4/4，55.000005 BPM，245.454525 秒。
- `theme_handoff_B`：817 个音符 / 817 个起音，严格单音；最大同时音 1，重叠 0，零长度/未匹配/未终止音符均为 0。
- 音域：G3–D6；保留原始第 3 小节开始的前导休止和第 57 小节终止。
- Delta 默认 C3–B5 的最佳全局八度放置为 `+0`：813 / 817 个事件可原样演奏，4 个超范围高音（C6 ×1、C#6 ×1、D6 ×2）。`-12` 会导致 22 个低音超范围；未采取任一放置或跳过决定。

审计文件：[Markdown](theme_handoff_B_audit.md) / [JSON](theme_handoff_B_audit.json)。

## 下一步质量门槛

请先试听这个候选，尤其留意 13 个交接边界是否自然。若你确认 B 版的听感，下一步才能决定 4 个高音是换源、换版本，还是由你明确接受跳过；在此之前不生成或运行 Delta 播放器。
