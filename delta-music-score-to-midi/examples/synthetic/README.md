# 无版权合成示例

`create_demo_midi.py` 会在你指定的位置创建一段简单、严格单旋律的测试 MIDI。它不是任何真实歌曲的旋律，也不包含下载的音乐材料。
这个合成旋律按 [CC0 1.0](CC0-1.0.txt) 公开，方便你用于测试和演示。

最简单的运行方式是双击仓库根目录下的：

```text
scripts\Run-Synthetic-Demo.cmd
```

它会创建输入 MIDI、审计它、提取单旋律、生成播放器并运行 `--dry-run`。所有生成结果都放入本目录的 `generated\run-时间戳` 文件夹，且被 Git 忽略。
