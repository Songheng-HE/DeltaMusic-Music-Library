# 在 ChatGPT、DeepSeek 与普通聊天 AI 中使用

## 先分清：模型不是运行环境

这个 Skill 安装在能读文件、运行脚本的 Agent 环境里，不是安装在“GPT”或“DeepSeek”模型本身。完整、经过测试的路径是 Codex；其他平台可以使用同一套工作方法，但能力取决于它实际提供的文件、Python 和联网工具。

| 你使用的环境 | 怎么开始 | 能承诺什么 |
| --- | --- | --- |
| Codex Desktop / CLI / IDE | 打开仓库根目录，输入 `$delta-music-score-to-midi` | **完整正式支持**：读取本机文件、运行 Python、生成并验证 MIDI |
| ChatGPT Desktop（可见 Skills 界面时） | 输入 `@` 并选择该 Skill，再发送提示词正文 | 取决于当前桌面端权限；先运行无版权自检 |
| ChatGPT 网页版 / 手机端 | 上传资料，使用 [通用提示词](08-generic-chat-ai.md) | 分析、转录草稿、找谱建议；不承诺本机脚本或播放器 |
| DeepSeek 网页 / App | 上传资料，使用 [通用提示词](08-generic-chat-ai.md) | 同上 |
| DeepSeek API 接入 Codex | 按 DeepSeek 官方的 Codex 接入说明配置，再按 Codex 路线使用 | **完整 Codex 流程**；Skill 仍由 Codex 加载，需 API 配置和费用 |
| 普通豆包聊天 | 上传资料，使用 [通用提示词](08-generic-chat-ai.md) | 分析、转录草稿、找谱建议；不承诺本机脚本或播放器 |

OpenAI 官方说明中，Codex 用 `$` 显式调用 Skill，ChatGPT 用 `@` 选择 Skill。[OpenAI Skills 文档](https://developers.openai.com/codex/skills) DeepSeek 官方也提供将其模型接入 Codex 的方法。[DeepSeek 接入 Codex](https://api-docs.deepseek.com/quick_start/agent_integrations/codex/)

## 普通聊天 AI 的正确预期

普通网页/手机聊天通常不能直接读取你电脑上的 `C:\完整路径`，也不能控制本机三角洲窗口。请上传 MIDI、PDF 或图片，而不是只粘贴本机路径。

如果平台没有明确的 Python 执行和文件导出能力，它可以帮你：

- 审阅乐谱、列出不确定符号；
- 起草 `reviewed_score.json`；
- 搜索并比较原始来源页面；
- 生成可在本机运行的操作步骤或代码。

但它不能声称自己已经运行本仓库脚本、生成经过验证的 `.mid`，或真正按下你电脑中的游戏按键。使用 [通用提示词](08-generic-chat-ai.md) 可以让它先说明能力边界。

## 给其他本地编码 Agent 的迁移方式

Claude Code、Cursor、Cline、OpenCode 等工具可能支持同类目录结构，但各自的安装目录、权限与调用语法不同。若要尝试迁移，复制完整目录：

```text
.agents/skills/delta-music-score-to-midi/
├── SKILL.md
├── agents/
├── scripts/
├── references/
└── tests/
```

并让该工具先验证：它能读 `SKILL.md`、能导入 `mido`、能创建 MIDI 文件，以及会在版权或转写不确定时停下来向用户确认。任一项不满足时，把它当作“提示词参考”而不是完整自动化 Skill。
