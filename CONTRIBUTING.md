# 群友修谱投稿指南

欢迎提交只包含一个 `.mid` 的修订版。MIDI 本身可以作为投稿，但不要直接覆盖现有默认可演奏版，也不要把它放到其他人的曲目目录根部。

## 推荐流程

1. 在 GitHub Fork 本仓库。
2. 新建目录：`community/<曲目英文标识>/candidate-<你的 GitHub ID>-v<版本号>/`。
3. 上传你的 MIDI，并复制 [投稿模板](community/_template/) 中的 `submission.yml`。
4. 在 `submission.yml` 写清：曲目、版本、基于哪个输入/旧版、改动说明、导入设置、已试听平台、许可、是否有权公开。
5. 发起 Pull Request，标题使用：`投稿：<曲名> v<版本号>`。
6. 维护者审核音乐结构、文件来源、可演奏性和许可信息。通过后会标记为“已验证候选”，或由维护者将其指定为 [曲目目录](CATALOG.md) 中的默认可演奏版。

## 只用 GitHub 网页投稿（不用 Git 命令）

1. 点击仓库右上角 **Fork**，进入你自己的副本。
2. 点击 **Add file** → **Create new file**，在文件名栏一次输入完整路径，例如 `community/example-song/candidate-你的GitHub-ID-v1/submission.yml`，再按模板填写内容并提交。
3. 进入刚创建的目录，点击 **Add file** → **Upload files**，上传你的 `.mid` 文件并提交。
4. 回到你的仓库，点击 **Contribute** → **Open pull request**，按页面的投稿清单发起 PR。

提交前确认 MIDI 能正常播放，且 `submission.yml` 的 `midi_file` 与实际文件名完全一致。

## 导入设置必须说明

请不要只凭 MIDI 文件名让下载者猜设置。每份投稿都必须在 `submission.yml` 中如实填写实际试听过的导入参数：`pitch_offset_semitones`（音高偏移，单位为半音）、`tempo_multiplier`（速度倍率）、`other_import_settings`（其他设置；没有则写“无”）和 `tested_in`（已试听的平台或播放器）。即使使用默认值，也要明确写出，例如音高 `0`、速度 `1.0`。

文件名只用于提示非默认且会明显影响演奏结果的关键参数。推荐格式：

```text
中文曲名（版本说明·导入音高-12·速度1.10x）.mid
```

其中 `导入音高-12` 表示导入时降一个八度。完整且权威的设置以 `submission.yml`、[社区投稿目录](community/README.md) 和合并后的 [MIDI-MANIFEST.yml](MIDI-MANIFEST.yml) 为准；不确定的设置必须写“待确认”，不能擅自当作默认值。

## 飞书、抖音群等渠道投稿

不熟悉 GitHub 的群友，可以先复制 [群聊投稿模板](community/群聊投稿模板.md)，把 MIDI 连同完整说明发给维护者。维护者会保留原投稿文件，并在公开下载时创建清晰的中文命名副本；不会把候选版直接称为最终版。

## 只有 MIDI，怎样展示？

只要有下面两项就能清楚展示：

```text
community/<曲目英文标识>/candidate-<GitHub-ID>-v1/
├─ <曲目>_candidate.mid
└─ submission.yml
```

GitHub 页面会以“可下载二进制文件”展示 MIDI，不会自动播放。请在 `community/README.md` 的表格中登记下载链接、状态、导入设置、已试听平台和改动说明；必要时可另附有权公开的试听音频或钢琴卷帘截图，但不是强制要求。

## 投稿许可与安全

- 提交即表示你有权把该 MIDI 及说明以本仓库的 [CC BY 4.0](LICENSE-MUSIC-CC-BY-4.0.md) 条款公开。
- 不要提交账号、个人联系方式、授权书原件、本机路径或未获授权的输入材料。
- 对同一首曲目的不同修订，请保留旧版并说明差异；不要伪造“官方最终版”状态。
