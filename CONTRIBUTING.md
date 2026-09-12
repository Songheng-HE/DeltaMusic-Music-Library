# 群友修谱投稿指南

欢迎提交只包含一个 `.mid` 的修订版。MIDI 本身可以作为投稿，但不要直接覆盖现有默认可演奏版，也不要把它放到其他人的曲目目录根部。

## 推荐流程

1. 在 GitHub Fork 本仓库。
2. 新建目录：`community/<曲目英文标识>/candidate-<你的 GitHub ID>-v<版本号>/`。
3. 上传你的 MIDI，并复制 [投稿模板](community/_template/) 中的 `submission.yml`。
4. 在 `submission.yml` 写清：曲目、版本、基于哪个输入/旧版、改动说明、许可、是否有权公开。
5. 发起 Pull Request，标题使用：`投稿：<曲名> v<版本号>`。
6. 维护者审核音乐结构、文件来源、可演奏性和许可信息。通过后会标记为“已验证候选”，或由维护者将其指定为 [曲目目录](CATALOG.md) 中的默认可演奏版。

## 只用 GitHub 网页投稿（不用 Git 命令）

1. 点击仓库右上角 **Fork**，进入你自己的副本。
2. 点击 **Add file** → **Create new file**，在文件名栏一次输入完整路径，例如 `community/example-song/candidate-你的GitHub-ID-v1/submission.yml`，再按模板填写内容并提交。
3. 进入刚创建的目录，点击 **Add file** → **Upload files**，上传你的 `.mid` 文件并提交。
4. 回到你的仓库，点击 **Contribute** → **Open pull request**，按页面的投稿清单发起 PR。

提交前确认 MIDI 能正常播放，且 `submission.yml` 的 `midi_file` 与实际文件名完全一致。

## 只有 MIDI，怎样展示？

只要有下面两项就能清楚展示：

```text
community/<曲目英文标识>/candidate-<GitHub-ID>-v1/
├─ <曲目>_candidate.mid
└─ submission.yml
```

GitHub 页面会以“可下载二进制文件”展示 MIDI，不会自动播放。请在 `community/README.md` 的表格中登记下载链接、状态和改动说明；必要时可另附有权公开的试听音频或钢琴卷帘截图，但不是强制要求。

## 投稿许可与安全

- 提交即表示你有权把该 MIDI 及说明以本仓库的 [CC BY 4.0](LICENSE-MUSIC-CC-BY-4.0.md) 条款公开。
- 不要提交账号、个人联系方式、授权书原件、本机路径或未获授权的输入材料。
- 对同一首曲目的不同修订，请保留旧版并说明差异；不要伪造“官方最终版”状态。
