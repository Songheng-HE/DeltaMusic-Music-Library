# 不同 AI 平台如何使用这个资料库与 Skill

`$delta-music-score-to-midi` 不是所有聊天框都认识的通用命令。只有在 Skill 已经安装、且 AI 有本地文件与 Python 执行权限时，才能完成完整转换。

## Codex 与 ChatGPT 桌面本地项目

这是推荐的完整路线：

1. 下载或克隆本仓库。
2. 进入 `delta-music-score-to-midi` 目录；该目录保留了新版 `.agents/skills/delta-music-score-to-midi`。
3. 在 Codex CLI 或 IDE 中输入 `$delta-music-score-to-midi`；在支持技能选择的 ChatGPT 桌面界面中，输入 `@` 选择该 Skill。
4. 上传实际 MIDI、PDF、图片或简谱，或在已获得本地文件权限的项目里给出完整路径。
5. 先看审计报告和待确认项，再要求生成 MIDI；播放器先用 `--dry-run`。

OpenAI 的官方文档说明：Codex 会发现项目或用户目录中的 `.agents/skills`；ChatGPT 使用 `@`，Codex 使用 `$` 显式调用技能。详见 [OpenAI Skills 文档](https://learn.chatgpt.com/zh-Hans/docs/build-skills)。

## Deep Code

Deep Code 是一个开源第三方 CLI；DeepSeek 官方 API 文档提供了接入说明。可采用本包的 Windows 安装脚本，将 Skill 放进用户目录：

```text
%USERPROFILE%\\.agents\\skills\\delta-music-score-to-midi
```

安装后在 Deep Code 中输入：

```text
/delta-music-score-to-midi
```

需要自行配置 Deep Code、Node.js、Python、所需依赖和自己的 DeepSeek API Key。DeepSeek 的官方文档列出了用户级 `~/.agents/skills/<name>/SKILL.md` 发现位置；详见 [Deep Code 接入文档](https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/deepcode/)。

## ArkClaw、普通豆包与普通 DeepSeek

- **ArkClaw** 是火山引擎的独立 Agent 产品，不等于普通豆包聊天。它支持 Skills，但是否能安装本仓库外部 Skill 取决于管理员权限与当前技能管理入口。首次尝试时，先要求它列出会读取的文件、依赖和权限；未经确认不要执行脚本。
- **普通豆包、普通 DeepSeek 网页/App**：不要把本仓库当作可自动安装的本地插件，也不要只发 `C:\\...` 路径。请上传平台允许的实际文件与 `SKILL.md`，把它们作为审阅流程参考。
- **ChatGPT 网页普通对话**：同样不能直接读取你电脑上的路径。可以上传允许的文件并请它协助分析，但完整的本地转换仍应使用 Codex、ChatGPT 桌面本地项目或 Deep Code。

普通聊天版第一句可以改为：

```text
我已上传文件和本项目的 SKILL.md。请仅将 SKILL.md 作为流程规范；
不要声称读取了我的 C:\\ 路径、运行了 Python，
或已生成经过验证的 MIDI。
先输出：结构判断与不确定项、需要我确认的选择、
以及供我在 Codex 或 Deep Code 本地执行的下一步命令。
```

如果平台不支持上传 `.mid`，不要通过改扩展名伪装上传。请改用 Codex/Deep Code，或上传本工具已生成的审计报告、乐谱截图，再请求平台协助分析。
