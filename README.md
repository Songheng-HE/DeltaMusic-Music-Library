# DeltaMusic 音乐资料库与修谱工作台

这是一个面向 DeltaMusic 的公开音乐资料库：包含已授权的原始输入 MIDI、修谱过程、审计报告、可复现脚本，以及可直接导入播放器的最终单旋律 MIDI。

普通玩家可以直接下载最终版 MIDI；想继续修谱的贡献者可以从每首曲目的 `input/`、`reports/` 和脚本开始复核与改进。

## 快速入口

- [逐首下载推荐最终 MIDI](CATALOG.md)
- [下载全部推荐最终 MIDI（ZIP）](https://github.com/Songheng-HE/DeltaMusic-Music-Library/releases/latest/download/DeltaMusic-final-midi-latest.zip)
- [在 Codex、ChatGPT、Deep Code、豆包或 DeepSeek 中使用](PLATFORM_GUIDE.md)
- [复制提示词开始修谱](PROMPTS.md)
- [群友投稿、审核和展示规则](CONTRIBUTING.md)
- [音乐资料的权利与许可](RIGHTS.md)

## 目录结构

```text
findMusic/
├─ delta-music-score-to-midi/       # 推荐使用的完整 Skill 包与工具文档
│  ├─ .agents/skills/.../           # 新版 Skill
│  ├─ docs/                         # 详细使用、排错和版权边界
│  ├─ scripts/                      # 安装、测试与演示入口
│  └─ examples/                     # 合成、无版权测试示例
├─ .agents/skills/...               # 较早的根目录 Skill 副本，仅作兼容/历史参考
├─ <曲目目录>/
│  ├─ input/                        # 已授权的源 MIDI、谱面或源材料
│  ├─ reports/                      # 审计、提取、编配与哈希记录
│  ├─ scripts/                      # 曲目专用处理脚本（部分曲目）
│  ├─ transcription/                # 人工逐小节转录数据（部分曲目）
│  └─ *.mid                         # 成品、候选或历史变体
└─ community/                       # 群友投稿模板与公开候选目录
```

推荐在 AI Agent 中打开 `delta-music-score-to-midi` 目录使用新版 Skill。根目录的旧 `.agents` 副本仍被保留，方便追溯历史，但不是首选入口。

## 普通玩家：下载哪个文件？

只想演奏时，请下载每首曲目在 [曲目目录](CATALOG.md) 中标为“推荐最终版”的 MIDI。不要把 `input/` 中的原始材料、带有 `candidate` 的候选文件或报告文件误当作最终演奏版。

有些曲目内部的历史报告仍使用旧文件名；请以顶层 [曲目目录](CATALOG.md) 和对应文件的哈希/说明为准。

## 修谱者：从哪里开始？

1. 下载完整仓库，而不是只下载最终 MIDI。
2. 进入目标曲目目录，先阅读 `README.md`（如有）和 `reports/`。
3. 从 `input/` 中的授权源材料开始，保留原始输入，不要覆盖。
4. 使用 `delta-music-score-to-midi` Skill 审计结构、记录选择依据，再生成候选单旋律 MIDI。
5. 将自己的候选文件按 [投稿规则](CONTRIBUTING.md) 提交，不要直接覆盖现有推荐最终版。

## 群友修谱如何展示？

GitHub 不会直接播放 MIDI。每个群友投稿即使只有一个 `.mid`，也应同时有一个简短的 `submission.yml`：写清曲名、版本、提交者 GitHub ID、基于哪个输入、修改内容、许可和审核状态。

在 [社区投稿目录](community/README.md) 中会以表格显示“曲目、提交者、状态、版本、直接下载 MIDI、说明”。待审核候选与“推荐最终版”分开存放，避免普通玩家误下载尚未复核的文件。

## 许可与权利

本仓库采用分项许可：

- Skill、Python、测试和文档代码部分：采用 [MIT 许可证](licenses/MIT.txt)。
- MIDI、输入谱面、转录数据、审计报告和与音乐内容直接相关的资料：采用 [CC BY 4.0](LICENSE-MUSIC-CC-BY-4.0.md)，除非具体文件另有标注。

维护者声明：已取得向公众公开、分发和在本仓库许可下使用所需的权利或授权。授权原件可能包含隐私或保密信息，因此不随仓库公开；详情见 [RIGHTS.md](RIGHTS.md)。

## 安全与边界

- 只在游戏、平台和服务器规则允许的情况下使用自动输入功能。
- 先运行 `--dry-run`，不要把测试通过当作音乐转写必然正确。
- 公开新作品前，请确认自己拥有相应的公开分发与改编权利。
- 请勿提交账号资料、授权书原件、私人联系方式、本机绝对路径或未获授权的音乐资料。
