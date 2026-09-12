# 《当年情》通道 1 单旋律提取记录

- 输入：`input/当年情.mid`（SHA-256 `c13aa6ee5edbf05d5d18ddab5da9be45ec3dd62dc99b13188cd0a8d92b07505f`）
- 用户选择：源 Type 0 轨 0 中的 **通道 1**（零基通道 0；Bright Acoustic Piano）。
- 选择依据：63 个事件、63 个起音、最大同时音 1、无重叠；通道 2 是完全重复的音色叠层，未合并。
- 处理：原始起止时值、速度、拍号与调号保留；未截断、未按全曲最高音混选、未移调、未裁去开头。
- 输出：`dang-nian-qing_melody_only.mid`（SHA-256 `a77c848a5339e9ec8303b16a071a14d7dea274d28490bbcc5017fdc2ad1a15e1`）
- 验证：63 个音符，最大同时音 1，重叠 0，音域 A♯4–D♯6；详见 `melody_audit.md`。
- 权利：来源权利状态仍为 `unknown`。仅记录为私下技术工作流，不能据此公开或再分发衍生 MIDI／播放器。
