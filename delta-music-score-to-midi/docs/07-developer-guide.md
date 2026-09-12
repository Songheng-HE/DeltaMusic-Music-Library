# 开发、测试与贡献

## 仓库结构

```text
.agents/skills/delta-music-score-to-midi/  # 实际 Skill
├── SKILL.md                                # 入口与工作流
├── agents/openai.yaml                      # Codex/ChatGPT UI 元数据
├── scripts/                                # MIDI 审计、编译、播放器生成
├── references/                             # 规则与 JSON schema
└── tests/                                  # 自动测试
scripts/                                    # Windows 安装、自检与无版权演示
examples/synthetic/                         # 不含真实歌曲的测试生成器
docs/                                       # 面向使用者与贡献者的说明
```

## 本地测试

Python 3.10+：

```powershell
py -3 -m pip install -r requirements.txt
py -3 -B -m unittest discover -s .agents\skills\delta-music-score-to-midi\tests -v
```

如果系统没有 `py`，改用可用的 `python` 命令。Windows 用户也可以双击 `scripts\Test-DeltaMusicSkill.cmd`。

CI 会在 Python 3.10 与 3.12 上运行同一组测试。当前测试重点包括：MIDI 结构分类、严格单旋律提取、乐谱 IR 校验、哈希/报告一致性、播放器生成和 dry-run。

## 进行行为测试

不要只测试文字是否出现。请用独立、真实的任务提示验证：

- 复杂总谱时不会默认抽最高音；
- 来源查找不会越过登录、付费或下载边界；
- 清晰单旋律谱会建立可追溯的复核数据；
- 不确定符号会被列出，而不是被猜掉；
- 真实输入播放始终先 dry-run，并保留可停止机制。

## 发布检查

推送公开仓库前，确认：

1. `git status` 中没有真实曲目、MIDI、报告、截图、用户路径或本地输出。
2. 软件许可证已由仓库所有者明确选择。
3. `requirements-player.txt` 仍然是可选项，没有被安装脚本自动执行。
4. README 中的安装、调用和输出说明与当前版本一致。
5. CI 与本地测试通过。
