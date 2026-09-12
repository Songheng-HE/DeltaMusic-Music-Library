# 《He's a Pirate》乐谱 / MIDI 候选研究

检索日期：2026-09-11（Asia/Shanghai）  
识别曲名：用户所写 `he is a parite` 应为 **He's a Pirate / He Is a Pirate**，出自 *Pirates of the Caribbean: The Curse of the Black Pearl*。作曲署名在不同页面为 Klaus Badelt、Hans Zimmer、Geoff Zanelli。

## 结论

没有找到可核验、允许将该曲改编为可分享 MIDI 或播放器的 **Tier A（权利已明确许可）**候选。该曲是现代电影配乐；即使购买了正版个人乐谱，也通常不包含复制、改编或分发权。

若目标是**私下技术测试**，优先考虑含原始 MIDI 的 Piano Fun（格式最直接），其次是 Everyone Piano 或 MidiShow 的社区 MIDI。它们都是 **Tier B：权利状态 unknown**，只能在你自行通过原页面正常取得、且确认适合私用后再上传审计；不能据此发布 MIDI、Python 播放器或其他衍生物。

## 候选总览

| 排序 / 分级 | 原始页面与版本 | 价格 / 正常获取 | 格式 | 旋律转换适配度 | 权利与主要风险 |
| --- | --- | --- | --- | --- | --- |
| 1 · Tier B | [Piano Fun — easy piano](https://pianofun.edu.vn/san-pham/he-is-a-pirate-easy-piano-piano-sheet-midi-file/) | 50,000 越南盾（页面划线价 100,000 越南盾）；页面显示 PayPal、加入购物车 | 页面标题明确为 piano sheet + MIDI；乐谱具体文件格式未见清晰声明 | **中上**：有 MIDI，可直接审计；但 easy-piano 很可能是双手和声编配，未见命名 Melody/Vocal 轨 | 页面未见可用改编/再分发许可；权利状态 **unknown**。购买或可下载不等于可生成/分享衍生文件。 |
| 2 · Tier B | [Everyone Piano — original theme](https://www.everypiano.com/Music-7883-He-is-a-Pirate-The-Theme-Song-of-Pirates-of-the-Caribbean.html) | 页面称免费；是否需账户/地区限制未核实 | 页面列出五线谱、数字谱、PDF、MIDI | **中等**：有 MIDI，且版本更接近主题曲；未显示轨道名或是否完整 | 上传者为 EOP Editor，但页面未提供可验证的改编许可；权利状态 **unknown**。取得后必须审计是否为多声部钢琴 MIDI。 |
| 3 · Tier B | [MidiShow — He is a Pirate（wangzheng6281）](https://www.midishow.com/midi/71837.html) | 页面有“下载”入口；精确点数/登录要求未在该条目公开摘要中确认 | 标准 MIDI Type 1，6.26 KB，1:17，200 BPM，6/8 | **中低**：仅有乐器/数据轨信息，无 Melody/Vocal/Solo 命名轨；摘要显示一个有音符轨、两个通道、钢弦吉他，可能有和弦 | 社区上传；平台/上传者的权利主张不是独立保证，权利状态 **unknown**。如自取用于私用，审计时必须确认单音性、重叠、旋律是否完整。 |
| 4 · Tier C | [Musicnotes — piano instrumental solo](https://www.musicnotes.com/sheetmusic/pirates-of-the-caribbean-the-curse-of-the-black-pearl/hes-a-pirate/MN0056944_U7) | US$5.99（1 次打印 + app 内互动副本；额外打印 US$4.99） | 4 页钢琴独奏；互动数字谱，可额外加购 PDF；没有可取得的 MIDI | **低**：只有钢琴独奏谱，不能无损转 MIDI；双手写法还需人工选旋律 | 官方零售、来源可信，但其许可明确限个人使用，并要求对复制、改编、编配、传输取得书面同意；不适合本流程的 MIDI 衍生输出。 |
| 5 · Tier C | [Etsy / Hypernatural — intermediate piano](https://www.etsy.com/listing/1722800656/hes-a-pirate-piano-sheet-music) | 当前展示 US$1.35（原 US$1.80；价格随地区/促销变化） | 3 页 PDF + MIDI（另有参考 PDF 等数字文件） | **中等（纯技术层面）**：直接附 MIDI，但为钢琴编配、没有 Melody 轨证据 | 卖家明确 “All rights reserved”，也未展示上游授权或可改编许可；不建议取得用于衍生流程。 |

## 候选卡片与审计重点

### 1. Piano Fun — 推荐的私用技术候选

- **标题 / 版本 / 乐器：** *He is a Pirate (easy piano) piano sheet + midi file*；简易钢琴。
- **可见信息：** 页面明确标为 “File midi - Sheet”，且产品标题包含 MIDI；价格 50,000 越南盾。
- **完整性和旋律证据：** 页面有试听区，但没有显示曲长、轨道名、分轨或 `Melody` 证据；不能预断为单音旋律。
- **取得后应审计：** 音轨/通道名称、最大同时发音数、重叠音、左右手是否混在同一轨；若无独立旋律声部，不应默认按全曲最高音提取。
- **适用范围：** 仅在你确认其适合私人工作流时作为 Tier B 输入；不适合公开交付物。

### 2. Everyone Piano — 免费但权利不明的技术候选

- **标题 / 版本 / 乐器：** *He is a Pirate-The Theme Song of Pirates of the Caribbean*；Klaus Badelt / Hans Zimmer 署名，EOP Editor 上传。
- **可见信息：** 页面列出 PDF、MIDI、五线谱和数字谱，并称可免费获取。
- **完整性和旋律证据：** 没有轨道名或乐器分轨细节；MIDI 可能是完整钢琴编配。
- **取得后应审计：** 同上；并确认实际文件确为页面所列版本、不是试听或节选。

### 3. MidiShow — 社区 MIDI 备选

- **标题 / 上传者：** *He is a Pirate*；wangzheng6281，页面标注“加勒比海盗全谱”。
- **可见技术信息：** 1:17、700 个音符、Type 1、200 BPM、6/8；页面列一个有音符轨，音乐为钢弦吉他，范围 F2–C5，并使用弯音轮事件。
- **旋律证据：** 没有 `Melody`、`Lyrics`、`Vocal`、`Solo` 等命名的独立旋律轨；短时长也可能是缩编而非完整主题。
- **取得后应审计：** 先确认页内的普通获取条件；再检测和弦/重叠、踏板/弯音轮、是否存在可辩护的单一旋律声部。若只有密集吉他/钢琴和声，停止提取并人工确认。
- **权利提示：** 社区页面不能证明上传者拥有授权；只可作为 unknown-rights 的私用技术备选。

### 不进入转换队列的两个来源

- **Musicnotes：** 是可信的正版个人演奏乐谱来源，内容为 4 页钢琴独奏、D 小调原调（页面也提供移调）。但 Musicnotes 的 [权限说明](https://help.musicnotes.com/hc/en-us/articles/360054660151-Song-Permissions-FAQs) 明示购买者仅限个人使用，复制、改编、编配、传输须得到权利人和 Musicnotes 的书面同意。因此适合练奏，不适合据此制作本项目的衍生 MIDI。
- **Etsy：** 虽直接声称包含 MIDI，且价格低，但卖家仅写 “All rights reserved”，没有看到上游授权或衍生许可。不能把商品上架或可下载理解为权利清晰，故列为 Tier C。

## 建议的下一步（不含下载）

1. 若只做私用技术测试：在原页面自行选择并正常取得 **Piano Fun** 或 **Everyone Piano** 的 MIDI；优先选择文件明确为 `.mid` / `.midi` 的版本。
2. 上传你有权私下使用的原始 MIDI，并说明“仅私用”。我将先做只读审计，报告轨道、单音性、节奏、可演奏音域和是否存在可辩护的旋律轨；在审计完成前不提取、不生成播放器。
3. 若计划发布或分享任何 MIDI / 播放器，请先取得覆盖改编与再分发的明确书面许可；目前这些候选都不够。

本研究未登录、付款、使用点数、下载文件、截取预览或绕过任何访问限制。价格与库存会随地区和时间变化，以原页面结算/说明为准。
