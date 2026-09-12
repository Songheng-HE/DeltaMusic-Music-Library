# 第一次使用：不需要懂 AI

这份指南假定你只会基本的“下载、解压、打开文件和发消息”。你不需要理解 Python、MIDI、Skill 或命令行，先按下面做即可。

## 你要实现的事

把你合法取得的一份 MIDI 或清晰乐谱交给 Codex，让它先检查材料，再生成可导入播放器的单旋律 MIDI。

## 第 1 步：下载并解压

1. 在 GitHub 仓库主页点击绿色 **Code** 按钮。
2. 选择 **Download ZIP**。
3. 在“下载”文件夹找到 ZIP，右键选择“全部解压缩”。
4. 记住解压后的文件夹。打开它后，应该能看到 `README.md`、`docs` 和一个名为 `.agents` 的文件夹。

不要在 ZIP 压缩包里面直接使用，也不要只打开 `.agents` 文件夹；要打开**仓库最外层文件夹**。

## 第 2 步：在 Codex 打开文件夹

1. 打开 Codex。
2. 选择“打开本地文件夹”或创建一个使用本地文件夹的新任务。
3. 选择刚才解压得到的仓库根目录。
4. 新建一个聊天任务。

Codex 会发现本仓库的 `.agents/skills/delta-music-score-to-midi`。这是 Codex 官方规定的项目级 Skill 放置方式；如果你在输入 `$` 后看不到它，完全关闭并重新打开 Codex，再确认文件夹选对了。[官方说明](https://developers.openai.com/codex/skills)

## 第 3 步：叫出 Skill

在 Codex 的聊天输入框键入：

```text
$delta-music-score-to-midi
```

或者只输入 `$`，从列表中选择“Delta 乐谱与 MIDI 转换”。选择后再上传文件、补充曲名或粘贴提示词。

## 第 4 步：选一种情况

| 你手里的材料 | 看哪一段提示词 |
| --- | --- |
| `.mid` 或 `.midi` 文件 | [已有 MIDI](02-prompt-library.md#1-我已经有-midi) |
| 简谱照片、五线谱 PDF、扫描图片 | [已有乐谱](02-prompt-library.md#2-我已经有-pdf图片或简谱) |
| 只有曲名，资料还没找 | [寻找来源](02-prompt-library.md#3-我还没有资料先寻找正规来源) |

## 第 5 步：怎么看结果

任务完成后，你可能会看到很多文件。真正放到你的三角洲音乐播放器“MIDI 导入”界面的，是：

```text
曲名_melody_only.mid
```

不是 `*.py`，不是 `manifest.json`，也不是报告文件。完整说明见 [输出文件与播放器](03-output-and-delta-player.md)。

## 先做一个完全无版权的练习（可选）

想先确认电脑环境，而不想拿真实歌曲做测试？双击：

```text
scripts\Run-Synthetic-Demo.cmd
```

它只会创建本仓库自制的短测试旋律，运行转换链路和 `--dry-run`；它不会发送真实键盘/鼠标输入。看到“演示成功”后，说明本地工具链基本正常。

首次运行会询问是否允许通过 Python pip 安装核心依赖 `mido`；按 `Y` 才会安装。该本地演示需要 Python 3.10+。
