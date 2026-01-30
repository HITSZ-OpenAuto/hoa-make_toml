# 嵌入式系统

**课程代码:** AUTO3024

## 考试

考试题型大概是四个选择（每题 5 分）外加 8-10 个简答和简单计算，除选择题外基本上见于 `materials/2024-嵌入式复习.pptx`。给分很高。

> 文 / [Oliver Wu]([https://github.com/oliverwu515](https://github.com/oliverwu515)), 2025.1

期末考试的题型有：选择题、简答题和问答题。需要计算，允许拿计算器。
考试内容需要背背每节课上最后几分钟用的签到题，一般下一节课就会给对应答案，同时需要背 `materials/2024-嵌入式复习.pptx`。
课上老师会展示几道往年考过的题。
实际该年考试总体给分不高，但难度中规中矩，花一天背一背拿个 60、70 不是一件困难的事，总分 90 以上的人数低于 5 人。

> 文 / [ZhuQi]([https://github.com/zhuqi000](https://github.com/zhuqi000)), 2026.1

## 实验

共设置基础实验 12 个（共 8 学时，每 2 个学时完成 3 个实验），难度不大。
在基础实验里，记得把 SYS 中的 Debug 设置成 JTAG(4pins)，指导书里没提这一点。
基础实验完成后是电机控制调速实验（共 4 学时，相比于原先的 8 学时有了大幅度的压缩，难度也随之增大，所以请提前写好代码。之前基础实验中部分代码可以复用）。

> 文 / [Oliver Wu]([https://github.com/oliverwu515](https://github.com/oliverwu515)), 2024.7

实验对着指导书一点点做就行了，难度很低，最后的调试实验多看指导书的配置，指导书有的配置没用醒目标识框起来。

> 文 / [ZhuQi]([https://github.com/zhuqi000](https://github.com/zhuqi000)), 2026.1

## 建议

实验课的内容是 STM32 开发，MCU 型号是 STM32F407ZGT6。
推荐大家使用 STM32CubeIDE 这个 All in one 的软件（包含了 CubeMX，可以不用单独下载）进行使用，它提供对 MacOS 或者 Linux 操作系统的支持。

> 文 / [Kowyo]([https://github.com/kowyo](https://github.com/kowyo)), 2024.6

## 课程安排

理论课共 20 学时，主要分为：
- 嵌入式系统概述
- CubeMX 配置与 Keil 编程环境
- GPIO
- 中断（中断及复位启动，中断优先级及配置、中断服务函数、外部中断/事件控制器）
- 串口与 DMA
- AD/DA
- 定时器（systick 定时器、基本定时器、通用定时器；输入捕获、输出比较等功能）
- 高级定时器（编码器接口、霍尔传感器接口……）

实验课共 12 学时。基础实验内容包括：
1. 单个 LED 闪烁实验（GPIO）
2. LED 流水灯实验（GPIO）
3. 按键控制 LED 实验（GPIO）
4. 外部中断实验（EXTI）
5. 定时器定时应用实验（TIM）
6. DAC 基本实验
7. TFT 屏基本实验
8. 串行通讯基本实验（UART）
9. DMA 直接内存访问实验
10. DMA-UART 收发实验
11. ADC 采集实验
12. AD 转换及定时器 PWM 输出实验
