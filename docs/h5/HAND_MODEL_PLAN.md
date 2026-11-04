# H5 手部建模准备（分支 cursor/h5-with-handmodel）

基准：与线上 Pages 一致的 `docs/h5/drill-cam-v1.0.html`（main @ d0372af / Safari 分享版）。

## 目标
在现有 PoseLandmarker（全身姿态）之上，增加 **手部关键点**，用于冲／膀出拳时腕、掌、指的可读反馈与更稳的命中判定。

## 建议接口（本阶段只定方向，不定死数值）
1. 模型：MediaPipe Hand Landmarker（或 Pose+Hands 组合），与现有 `tasks-vision` 同栈。
2. 加载：CDN 优先，本地 `docs/h5/mediapipe/` 后备；失败时日课触控演示仍可用。
3. 与玩法：手部结果只增强「瞬时／维持」路径的置信度，不改 3s／2s／60s 与十击谱。
4. 渲染：左手／右手骨架叠在 `overlayCanvas`；不挡木人高亮靶臂。

## 下一步
- [ ] 接入 HandLandmarker 加载与权限同路径
- [ ] 腕点与冲／膀方向一致性启发
- [ ] 竖屏 390 宽可读性复验（C4）

未合 main；Pages 仍指当前分享版。
