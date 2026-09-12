# 《卡农》合法乐谱候选研究

> **2026-09-11 刷新说明：** 以下“当前短名单”取代本报告后续的旧排名作为这次决策依据。它将 MidiShow 明确列入 Tier B 技术备选，而非因无法独立核验授权就静默排除。旧研究内容保留在后文，供核查历史结论。

- 本轮范围：只查看公开商品/条目页的可见元数据；**未下载、登录、付费、消耗积分、绕过访问限制或从预览重建任何文件。**
- 目标：为 Delta 寻找可以变成一条可听旋律线的《D 大调卡农》版本。原作是三把小提琴加通奏低音，未天然指定唯一“主旋律”；多声部版本需要在本地审计后由用户选择具体声部。
- 用途：用户尚未声明私用或公开发布。Tier B 文件只能在用户自行按正常流程取得、并确认适合私用后再审计；不得据此制作可公开分享的衍生 MIDI 或播放器。
- 价格：均为本次页面可见值；会随地区、税费、会员和结账流程变化。

## 当前短名单（按授权层级与 Delta 适配度）

| 推荐 | 层级 / 权利状态 | 候选 | 页面价格 / 正常取得要求 | 可见格式 | Delta 适配度 |
| --- | --- | --- | --- | --- | --- |
| 1 | Tier A / `cleared` | [Mutopia — Canon in D（Violin）](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1700) | 未标价；页面可见下载链接，未见登录或付款字段 | MIDI、LilyPond、A4/Letter PDF | **高**：明确单小提琴 + 原生 MIDI |
| 2 | Tier A / `cleared` | [Mutopia — Canon per 3 Violini e Basso](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2047) | 未标价；页面可见下载链接，未见登录或付款字段 | 压缩 MIDI、LilyPond、A4/Letter PDF | **中**：原始编制更完整，但必须选定一个小提琴声部 |
| 3 | Tier A / `cleared`（限非商业许可范围） | [IMSLP — For Violin (Fine)，#527417](https://imslp.org/wiki/Canon_and_Gigue_in_D_major_(Pachelbel,_Johann)) | 未显示单件价格；本轮未触发具体取得流程 | 2 页 PDF | **中**：明确独奏小提琴，但 PDF 不能承诺无损转换 |
| 4 | Tier B / `unknown` | [MidiShow — 卡农（简易版）](https://www.midishow.com/en/midi/70211.html) | 未标价；可见 Download，登录/积分要求未核实 | MIDI Type 1；单一有声钢琴轨 | **中高**：上传者称已去除左手与右手多指和弦；仍须审计单音性和范围 |
| 5 | Tier B / `unknown` | [MidiShow — canon（Right Hand / Left Hand）](https://www.midishow.com/en/midi/canon-midi-download-186795) | 未标价；可见 Download，登录/积分要求未核实 | MIDI Type 1；具名右手/左手轨 | **中**：`Right Hand` 是可辩护的起点，但 F#3–F#6 无法整体装入默认三八度 |
| 6 | Tier C / 仅合规购买，不清除衍生权 | [Musicnotes — Canon in D - Violin，MN0068638](https://www.musicnotes.com/sheetmusic/johann-pachelbel/canon-in-d-violin/MN0068638) | 本地区页面显示 ¥794 或 1 Pro Credit | 2 页可打印/互动数字小提琴谱；未显示原生 MIDI/MusicXML | **音乐高、转换低**：独奏线清楚，但不可默认转成 MIDI/player |
| 7 | Tier C / 仅合规购买，不清除衍生权 | [Virtual Sheet Music — Violin & Piano](https://www.virtualsheetmusic.com/score/CanonVlPf.html) | $7.99，或会员包含 | PDF、互动谱、MIDI、MP3、视频；会员可 MusicXML 导出 | **技术高、授权不适用**：有具名 violin part，但同时含钢琴与 Gigue |

### 1. Tier A 首选：Mutopia 单小提琴版

- **版本 / 格式：** Johann Pachelbel，`Instrument(s): Violin`；页面列出 MIDI、LilyPond 和两种 PDF。
- **可用许可：** 该特定版本标为 CC BY 3.0；可在遵守署名、许可链接及修改说明的条件下改编和分享。
- **适配判断：** 最适合先取得再审计：既有独奏乐器提示，又有可确定性审计的 MIDI。页面本身未证明轨道名、完整性或严格单音性，所以仍须本地审计与试听。

### 2. Tier A 多声部备选：Mutopia 三小提琴 + 大提琴

- **版本 / 格式：** 原始编制方向的三把小提琴与大提琴；有压缩 MIDI、LilyPond 和 PDF。
- **可用许可：** 页面标为 CC BY 4.0；公开衍生时须正确署名、附许可和修改说明。
- **适配判断：** 想保留卡农的声部结构时更好；但不应从全曲自动取最高音。上传后需要先比较 Violin 1/2/3，且可能要做 A/B 听感选择。

### 3. Tier A（非商业范围）：IMSLP 的 Fine 小提琴独奏谱

- **版本 / 格式：** IMSLP 同页 `For Violin (Fine)`，资产 #527417，2 页 PDF。
- **可用许可：** 页面标注 CC BY-NC-SA 4.0：允许在非商业、署名、相同方式分享的范围内改编；若用途涉及商业或不希望采用相同许可，不应选择。
- **适配判断：** 乐器角色清晰；但 PDF 只能作为人工核对的谱面来源，不能承诺无损 OCR/自动转 MIDI。

### 4. Tier B 技术首选：MidiShow《卡农（简易版）》

- **可见技术证据：** 上传者 qpr666 说明已去掉左手和右手多指和弦，称适合初学者掌握旋律；页面显示 3:53、72 BPM、一个有声钢琴轨、554 个 notes/chords、G3–C6。
- **适配判断：** 对单线 Delta 比完整钢琴编曲更有希望；不过页面的“单轨”不是严格单音证明，C6 也比默认 B5 高一个半音。取得后先检查和弦/重叠、实际可演比例和试听，不会静默折八度。
- **权利状态：** `unknown`。未显示可用许可证；仅可作为用户自行取得后的私用技术备选。

### 5. Tier B 有声部名备选：MidiShow《canon》

- **可见技术证据：** 上传者 TOY5021；页面显示 `Right Hand` 与 `Left Hand` 两个有声轨，右手为 388 个 notes/chords、F#3–F#6，且显示上传者选择的 CC0/Public Domain。
- **适配判断：** `Right Hand` 是明确、可审计的候选声部，优于从全曲盲选最高音；但 F#3–F#6 不可能以一个全局八度位移全部落入默认 C3–B5，预期需要用户接受跳过事件或换源。
- **权利状态：** `unknown`。MidiShow 的条款说明条目授权由上传者选择、平台不保证准确性；因此 CC0 仅记录为上传者声明，不视为独立清权或公开衍生许可。

### 6. Tier C：Musicnotes 小提琴独奏版（购买/演奏候选）

- **版本 / 格式 / 价格：** Paul Shin 编曲，D 大调、约 q=80、2 页，Violin `Instrumental Part`；本地区页面显示 ¥794 或 1 Pro Credit，提供可打印及互动数字乐谱，没有可见原生 MIDI/MusicXML。
- **适配判断：** 乐器线条最清楚的一类购买乐谱；若仅作演奏/阅读很合适。对本工作流却不是可直接转换的格式，PDF/互动谱不可承诺无损转写。
- **为何不是转换源：** Musicnotes 的查看器许可禁止修改或制作其 Music 的衍生作品；“演出和录音权利”不是改编/生成 MIDI 的许可。因此除非另获书面许可，不进入 MIDI/player 转换队列。

### 7. Tier C：Virtual Sheet Music 小提琴 + 钢琴版（格式强，但不清除衍生权）

- **版本 / 格式 / 价格：** Exclusive Arrangement，16 页，含 Canon 和 Gigue；页面标为 violin & piano、$7.99 或会员包含。可见 PDF、互动谱、MIDI、MP3、视频，会员可经 Playground 导出 MusicXML；其中 violin part 为 3 页。
- **适配判断：** 从纯技术格式看是商业候选中最有利的一个，因为明确包含 MIDI 和小提琴声部；但取得后仍必须审计小提琴是否独立、是否严格单音，并确认只处理 Canon 而不是不透明地丢弃 Gigue。
- **为何不是转换源：** 其公开条款限制修改、提取到新文件、媒介转换及再分发；购买是合法取得，不是生成或分享新 MIDI/player 的授权。需要权利方书面许可才可进入该转换流程。

## 推荐与下一步

1. **想要最稳妥且最容易做成好听的 Delta 单旋律：** 选 Mutopia 单小提琴版（候选 1）。
2. **想优先试一个实用、简化的社区 MIDI：** 选 MidiShow《卡农（简易版）》（候选 4）；它是这次明确保留的 Tier B 技术备选，不是被排除项。
3. **想做接近原始卡农的某一声部：** 选 Mutopia 三小提琴版（候选 2），上传后先决定/试听 Violin 1、2 或 3。
4. **只想购买小提琴谱演奏：** Musicnotes 或 Virtual Sheet Music 都可比较；在未获得衍生许可前，不能拿其文件做 melody-only MIDI/player。

请从原始页面按正常流程自行取得所选文件，并上传你有权用于目标用途的副本。我会先审计轨道、单音性、休止、速度和三八度范围；不会下载、绕过限制，也不会默认从多声部编曲取最高音。

- 检索日期：2026-09-11（Asia/Shanghai）
- 范围：仅检索原始来源页面的可见元数据、价格和许可；**没有下载、购买、登录、绕过限制或提取任何乐谱/MIDI。**
- 目标版本：Johann Pachelbel，*Canon and Gigue in D major*, P.37（常称《D 大调卡农》或《卡农》）。
- 重要音乐事实：原作是三把小提琴与通奏低音的卡农；并不存在无需音乐选择就能称作“唯一主旋律”的原始声部。独奏改编是最适合 Delta 单线输入的来源；完整原作则必须在审计后由用户指定 `Violin 1`、`Violin 2` 或 `Violin 3`，不得从全曲自动取最高音。
- 用途状态：尚未声明私用或公开发布。下文的“可取得”不等于“可再发布衍生 MIDI/播放器”。

## 排名概览

| 排名 | 候选 | 权利清晰度 | 可见格式 | Delta 单旋律适配度 | 当前结论 |
| ---: | --- | --- | --- | --- | --- |
| 1 | Mutopia：单小提琴版 | 明示 CC BY 3.0 | MIDI、LilyPond、PDF | 高 | 首选；可改编但须署名 |
| 2 | Mutopia：3 小提琴 + 大提琴版 | 明示 CC BY 4.0 | MIDI/LilyPond/PDF 压缩包 | 中 | 结构化多声部候选；须先选声部 |
| 3 | IMSLP：Seiffert 1929 历史版 | 精确条目标为 Public Domain | PDF 总谱/分谱 | 低–中 | 最保守的公版阅读源；无对应结构化文件承诺 |
| 4 | Musicnotes：小提琴独奏版 | 商业出版页清晰；衍生许可未展示 | 可打印/互动数字乐谱 | 中 | 可购买演奏；不宜默认进入转换队列 |
| 5 | Virtual Sheet Music：长笛独奏版 | 商业来源清晰；衍生/发布权利未明且受限 | PDF、MIDI、互动、会员 MusicXML | 技术高、权利需核实 | 私用转换或公开发布均不可默认允许 |
| 6 | Mel Bay：小提琴独奏版 | 官方出版商；衍生许可未展示 | 数字标准五线谱 | 中低 | 低价演奏乐谱，不是首选转换源 |

## 候选卡

### 1. Mutopia — Canon in D（Violin）

- **作曲 / 版本 / 乐器：** Johann Pachelbel；Mutopia 2009/09/07-1700；页面明示 `Instrument(s): Violin`，来源为 Jim Paterson / mfiles.co.uk（`with permission`）。
- **原始页面：** [Mutopia: Canon in D](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1700)
- **可见格式：** LilyPond 源文件、MIDI、A4 PDF、Letter PDF。
- **完整性：** 页面标题为 `Canon in D`，未就“完整/节选”另作声明；取得后应通过 MIDI 审计确认结构和时长。
- **可见旋律证据：** 明示为单一 Violin 乐器版本，且有 MIDI；这比总谱更接近单线候选，但仍不能仅凭“一件乐器/MIDI”假定严格单音。
- **授权 / 许可：** 页面明确为 [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)。这份**特定排版/改编**可复制、改编和再发布（包括商业用途），条件是适当署名、附许可链接并说明修改；没有 NC 或 ND 限制。
- **价格 / 注册 / 地区：** 页面显示下载链接，未显示价格或账户要求；实际访问政策与地区可用性未触发验证。
- **适配度：** **高，首选。** 有明确单乐器范围、结构化 MIDI 和可改编许可。适合由用户从原页取得并上传后做轨道审计。
- **风险：** 它是现代单小提琴改编，不应声称等同于原作三声部；任何公开衍生物须保留 CC BY 所需署名和许可信息。

### 2. Mutopia — Canon per 3 Violini e Basso（三小提琴 + 大提琴多声部）

- **作曲 / 版本 / 乐器：** Johann Pachelbel；Mutopia 2015/09/02-2047；`3 Violins, Cello`，来源 IMSLP，维护人 Michael Fischer v. Mollard。
- **原始页面：** [Mutopia: Canon per 3 Violini e Basso](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2047)
- **可见格式：** 压缩的 LilyPond 文件、MIDI 文件、A4/Letter PDF 文件。
- **完整性：** 页面明示三把小提琴和大提琴编制，但没有把该刻谱标为 urtext、手稿版或“完整原作”。它是结构化多声部候选，而非单线简化版；实际段落范围应在取得后审计。
- **可见旋律证据：** 页面没有 `Melody`/`Lead` 标签，只显示 `3 Violins, Cello` 和多个 MIDI/LilyPond 文件；实际文件的声部名、MIDI 轨名和单音性仍须审计。
- **授权 / 许可：** 页面明确为 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，可改编和再发布（包括商业用途），但必须署名、链接许可并说明修改。
- **价格 / 注册 / 地区：** 页面显示下载格式，未列价格或账户要求；实际访问政策与地区可用性未触发验证。
- **适配度：** **中。** 若目标是三小提琴加低音乐器的多声部版本，这是权利和格式都清晰的候选；取得后必须由用户确认想要的具体 violin 声部，不能默认取最高音或拼接声部。
- **风险：** 页面不证明这是唯一或最忠实的历史原版；多声部卡农也没有客观唯一的“主旋律”。若要让不同声部在休止处交接，需先由用户确认音乐方案，再生成可审计的 A/B 版本。

### 3. IMSLP — Canon and Gigue in D major, P.37（Seiffert 1929 历史版）

- **作曲 / 版本 / 乐器：** Johann Pachelbel；Max Seiffert 编辑并作通奏低音实现，Organum / Kistner & Siegel，1929；原作编制为 3 violins + continuo，含 Canon（57 小节）和 Gigue（20 小节）。
- **原始页面：** [IMSLP: Canon and Gigue in D major, P.37](https://imslp.org/wiki/Canon_and_Gigue_in_D_major_(Pachelbel,_Johann))
- **可见格式：** 精确资产 #44549 为 11 页 PDF 总谱；同一历史版本还列有具名的 Violin 1、Violin 2、Violin 3 与 Continuo PDF 分谱。
- **完整性：** 精确的公版 Seiffert #44549 总谱及同组分谱位于页面的 `Complete` 分类，包含 Canon 与 Gigue。该条目并未同时展示一个独立的 Canon-only 数字资产；若只需要 Canon，先确认所取得资产与处理范围，不能悄然丢弃 Gigue。
- **可见旋律证据：** 有明确分谱名，但无 `Melody`/`Lead` 标签；三条小提琴均是卡农声部。
- **授权 / 许可：** 页面针对 #44549 和同组分谱明确标注 `Public Domain`。这不自动涵盖同页其他现代改编、录音或 MIDI；每个拟取得的独立资产都应单独核对其版权标签和用户所在地规则。
- **价格 / 注册 / 地区：** 页面未列资产价格；本研究未触发下载步骤，因此不对等待、注册或地区流程作保证。
- **适配度：** **低–中。** 权利链对精确历史 PDF 很清楚，但只有 PDF，后续需人工逐小节核对或先取得获授权的 MIDI/MusicXML。
- **风险：** 不应把工作页中任何 `Synthesized/MIDI` 条目自动视为这个公版版本；同页的 MIDI/现代排版分别有 CC BY-NC-SA、CC BY 等不同许可。

### 4. Musicnotes — Canon in D - Violin（Paul Shin 编曲）

- **作曲 / 版本 / 乐器：** Johann Pachelbel；Musicnotes Edition，Paul Shin 编曲；`Instrumental Part` / Violin，D major，2 页，页面所示速度约 q=80。
- **原始页面：** [Musicnotes: Canon in D - Violin（MN0068638）](https://www.musicnotes.com/sheetmusic/johann-pachelbel/canon-in-d-violin/MN0068638)
- **可见格式：** 可打印的数字乐谱和互动、可下载数字文件；页面另显示可加购高分辨率 PDF。没有展示原生 MIDI 或 MusicXML。
- **完整性：** 页面未明确标记完整或节选。
- **可见旋律证据：** 明示 Violin `Instrumental Part`，是较强的单线乐器候选，但仍须对用户供给的实际文件审计。
- **授权 / 许可：** 由 Musicnotes, Inc. 出版/管理；商品页宣传“演出与录音权利”和无限打印。该页面**没有**明示把其现代编曲转换、改编或公开再发布为新 MIDI/播放器的许可。
- **价格 / 注册 / 地区：** 2026-09-11 当前地区页面显示 `¥794`（或 1 Pro Credit）；价格、币种、税费和结账条件可能变化。
- **适配度：** **中。** 音乐上很适合独奏线，但格式不是确定性转换的首选，且衍生权利需另获确认。
- **风险：** 原作公版并不会让 Paul Shin/Musicnotes 的现代编曲自动可再发布。可作为合规购买与个人演奏候选；公开衍生 MIDI/播放器前应向权利方取得书面许可。

### 5. Virtual Sheet Music — Canon in D and Gigue（Flute Solo）

- **作曲 / 版本 / 乐器：** Johann Pachelbel；Virtual Sheet Music 的 `Exclusive Arrangement`；Flute Solo，D major，4/4，Canon + Gigue，页面列 8 页（实际音乐 4 页）和 6:49。
- **原始页面：** [Virtual Sheet Music: flute solo](https://www.virtualsheetmusic.com/score/CanonFlSolo.html)
- **可见格式：** PDF、互动乐谱、MIDI、MP3、视频；会员可经 Playground 导出 MusicXML；购买或会员访问后可下载单一 ZIP。
- **完整性：** 包含 Canon 与 Gigue；页面未使用“完整原作”标签，应按提供文件审计实际内容。
- **可见旋律证据：** 明示 `flute solo`，是最清晰的单乐器商业候选之一。
- **授权 / 许可：** 该来源具有明确商业提供者。其[服务条款](https://www.virtualsheetmusic.com/aboutus/legal.html)对下载的 PDF 乐谱只允许个人打印、演出、学习或教学，并禁止修改、复制到新文件、再授权、分发和 `media translation`；条款也一般性禁止将下载的音乐披露、发布、出售或交给第三方，并声明其乐谱为 `All Copyrights Reserved`。商品页同时列出随 ZIP 提供的 MIDI，但条款没有单独界定该 MIDI 的私用转换范围。
- **价格 / 注册 / 地区：** 单次购买页面显示 `$4.99`，或会员免费访问；需账户/付款或会员资格。价格、会员费、税费与地区可用性应在原页确认。
- **适配度：** **技术上高，衍生权利需核实。** 它的 MIDI/MusicXML 路线理想，但不能把购买、会员访问或已含 MIDI 自动视为转换/发布新 MIDI 或 player 的许可。
- **风险：** 私用审计或转换前，应先确认购买/授权覆盖计划用途；任何公开、再分发、修改或媒介转换的输出都应先取得 Virtual Sheet Music 的书面许可。

### 6. Mel Bay — Canon in D（Katherine Curatolo 编曲，小提琴独奏）

- **作曲 / 版本 / 乐器：** Johann Pachelbel；Katherine Curatolo 编曲；Mel Bay Publications, Inc.；Violin Solo，标准五线谱，中高级，2 页。
- **原始页面：** [Mel Bay: Canon in D（30206S9）](https://www.melbay.com/Products/30206S9/canon-in-d.aspx)
- **可见格式：** `Digital Sheet Music` / 标准五线谱；页面未展示原生 MIDI 或 MusicXML。
- **完整性：** 页面未明确标记完整或节选。
- **可见旋律证据：** 明示 `VIOLIN SOLO`，适合从音乐功能上作为单线候选；只凭 PDF 不能保证没有双音或附加声部。
- **授权 / 许可：** 官方出版商商品页明确列出出版信息，但商品页未显示可改编、转换或公开再发布的许可。
- **价格 / 注册 / 地区：** 页面所示 `$2.99`；经商店或当地经销商购买，库存/可用性随地区而变。
- **适配度：** **中低。** 是低价、清晰的独奏乐谱获取候选；但无结构化格式，且衍生许可不明。
- **风险：** 不应从预览或 PDF 做无授权自动转写；若日后要构建可共享的 MIDI/player，先索取权利方许可或改用候选 1。

## 推荐与用户交接

1. **第一选择：Mutopia 单小提琴版。** 它同时满足明确单乐器、MIDI、可编辑源文件和 CC BY 改编许可；请从其原始页面自行取得所需文件，并保留作者、来源、CC BY 3.0 与任何修改说明。
2. **结构化多声部备选：Mutopia 三小提琴 + 大提琴版。** 若你想使用该三小提琴加低音乐器版本，请先决定是要哪个声部，或在审计后比较多个合法候选声部。
3. **不要以商业购买替代衍生许可。** Musicnotes、Virtual Sheet Music 和 Mel Bay 都是合规购买线索；Virtual Sheet Music 的公开条款尤其限制 PDF 修改、媒介转换和公开再分发，同时未单独界定其随附 MIDI 的私用转换。它们适合获得演奏乐谱，不自动适合制作或分享新 MIDI/player。

我没有替你下载或购买任何文件。请从选定的原始页面自行获得已授权的 `.mid`/`.midi`（优先）或明确允许转换的结构化文件，并上传到项目中。随后需要你确认：所选版本、目标声部、使用是私用还是公开；我会先审计文件，再决定是否能提取旋律，不会默认从多声部编曲取最高音。
