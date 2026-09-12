# Canon per 3 Violini e Basso — 主旋律选择审计

- 审计日期：2026-09-11（Asia/Shanghai）
- 用户提供的原始压缩包：`input/mutopia-2047/Canon_per_3_Violini_e_Basso-mids.zip`
- ZIP SHA-256：`D05D47D19130688728D43476EE30D7E6C41DFC5369E40F2A1DD50A69D389B29C`
- 本报告仅分析用户提供的原件；未下载、购买、登录或改写任何源 MIDI。

## 结论

**默认主旋律候选：Violin I** — 总谱的轨道 #1（`violinI:`），对应分谱文件 `input/mutopia-2047/violin_one_part.mid` 的轨道 #1。

理由是结构性的，而不是“全曲最高音”规则：Violin I 是具名的第一个小提琴声部，并且最早进入卡农主题。Violin II 在它之后 **2 小节**进入，Violin III 在它之后 **4 小节**进入；它们在重叠的主题段中分别与 Violin I 的移位事件对齐 576/577 和 560/561 个。末尾的微小差异是终止句，不是另一条独立主旋律。

因此，如果目标是“一条完整、从第一次主题出现开始的卡农旋律”，选择 Violin I 是最可复核的默认方案。Violin II/III 是同一主题的延迟声部；Cello 是低音持续基础，不是主旋律。

## 审计范围与音乐结构

所有 MIDI 均为 Type 1、PPQ 384、55.000005 BPM、4/4、D 大调、总时长 245.454525 秒。每条有声音轨都严格单音、无重叠、无同起音和无报告异常。

| 总谱轨道 | 对应分谱 | 首次进入 | 音符数 | 音域 | 单音性 | 音乐职责 |
| ---: | --- | ---: | ---: | --- | --- | --- |
| #1 `violinI:` | `violin_one_part.mid` | tick 3072（第 3 小节起） | 593 | G3–D6 | 严格单音 | **第一次呈示卡农主题；默认主旋律** |
| #2 `violinII:` | `violin_two_part.mid` | tick 6144（比 Violin I 晚 2 小节） | 577 | G3–D6 | 严格单音 | 同主题的第二次进入 |
| #3 `violinIII:` | `violin_three_part.mid` | tick 9216（比 Violin I 晚 4 小节） | 561 | G3–D6 | 严格单音 | 同主题的第三次进入 |
| #4 `violoncello:` | `violoncellopart.mid` | tick 0 | 225 | D2–D3 | 严格单音 | 低音基础声部 |

总谱审计：[Markdown](canon_per_3_violini_e_basso.md) / [JSON](canon_per_3_violini_e_basso.json)。各分谱的独立审计文件与原件放在同一目录，方便复核。

## Delta 三八度预检（只报告，不生成播放器）

默认可奏范围为 C3–B5。对 Violin I 使用唯一保真的最佳全局八度放置 `+0` 时：

- 587 / 593 个音符可原样演奏；
- 6 个音符超出上限；
- 不能以单一全局 ±12 半音八度位移让全部 G3–D6 音符落入 C3–B5；
- Violin II/III 有相同的 G3–D6 音域，不能通过简单换到延迟声部来消除这一问题。

未进行每音折八度、转调、删音、提取 `melody-only` MIDI 或生成 Delta 播放器。若进入下一步，需要先试听 Violin I 分谱，并由用户决定：换用更窄音域的来源，还是明确接受这 6 个超范围事件的处理方案。
