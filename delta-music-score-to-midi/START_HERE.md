# 从这里开始（第一次使用）

这份说明只做一件事：让完全没接触过 AI Skill 的人，在几分钟内知道下一步点哪里、输入什么。

## 你需要准备

- 已安装并登录的 Codex。
- 一份你有权使用的 MIDI，或清晰、完整的单旋律简谱/PDF/图片。

没有乐谱也没关系：Skill 能帮你找正规来源页面，但你要自己在原页面购买、下载或取得许可。

本页是 Codex 的完整流程。若你使用 ChatGPT 网页/手机、DeepSeek 或普通豆包聊天，请改看 [其他 AI 的使用方式](docs/06-other-ai-agents.md) 和 [通用提示词](docs/08-generic-chat-ai.md)。

## 三步开始

1. 把 GitHub 下载的 ZIP 解压到普通文件夹。
2. 用 Codex 打开这个文件夹的根目录；你应当能看到 `.agents`、`docs` 和 `README.md`。
3. 在 Codex 聊天框输入 `$delta-music-score-to-midi`，上传文件并粘贴 [提示词模板](docs/02-prompt-library.md)。

如果在 `$` 菜单中看不到它，请确认你打开的是解压后的仓库根目录，而不是 ZIP 或它的父文件夹，然后重启 Codex。

## 不知道选哪种提示词？

- 你有 `.mid` / `.midi` 文件：选“已有 MIDI”。
- 你有 PDF、图片、简谱：选“已有乐谱”。
- 你只有曲名：选“寻找来源”。

真正要导入三角洲音乐播放器的结果始终是 `*_melody_only.mid`，不是 `.py` 文件。详见 [输出说明](docs/03-output-and-delta-player.md)。
