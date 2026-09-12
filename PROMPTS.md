# 可复制提示词

在 Codex 中保留 `使用 $delta-music-score-to-midi`；在 Deep Code 中把开头改为 `使用 /delta-music-score-to-midi`；在支持 Skill 的 ChatGPT 桌面界面中，先输入 `@` 选择该 Skill，再粘贴后续内容。

普通 ChatGPT 网页、普通豆包和普通 DeepSeek 不应使用本地路径；请上传实际文件与 `SKILL.md`，并使用 [平台说明](PLATFORM_GUIDE.md) 中的“提示词参考版”开头。

## 已经有 MIDI

```yaml
使用 $delta-music-score-to-midi 处理这个文件：
C:\\完整路径\\曲目.mid

先审计 MIDI 并判断结构类型，不要直接默认提取最高音，有时候可能是多个音轨在交替演奏旋律。
确认方案后生成单旋律 MIDI和审计报告。
```

## 已经有 PDF、图片或简谱

```yaml
使用 $delta-music-score-to-midi 处理这个乐谱：
C:\\完整路径\\乐谱.pdf

先按页、谱表和小节转录，建立 reviewed_score.json，
把所有不确定符号列出来，未经我确认不要编译。
确认后生成 MIDI、审计报告。
```

## 还没有乐谱，需要寻找

```text
使用 $delta-music-score-to-midi，为《曲名》寻找适合提取单旋律的乐谱或 MIDI。

优先公开、授权清楚、容易复核的来源。
MidiShow 可以作为权利情况未知的技术备用方案，不要直接排除。
只提供原始页面、费用和授权情况，不要替我绕过付费或下载限制。
```

## 生成后先验收

```text
在生成任何 MIDI 前，请先给我一个“待确认清单”。
只要涉及声部选择、反复顺序、八度、速度、休止、重复、截断音符或移调，
就先解释你的建议并等我确认。
```

最终生成后，请检查是否严格单旋律、是否保留重要休止与重复、是否超出三八度范围，并说明哪个文件可以导入播放器。
