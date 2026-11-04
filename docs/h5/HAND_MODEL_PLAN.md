# H5 手部建模准备（分支 cursor/h5-with-handmodel）

基准：与线上 Pages 一致的 `docs/h5/drill-cam-v1.0.html`（main @ d0372af / Safari 分享版）。

## 目标
在现有 PoseLandmarker（全身姿态）之上，增加 **手部关键点**。手部只用于冲／膀出拳时腕、掌、指的可读反馈，以及寸劲的画面呈现。

## 建议接口（本阶段只定方向，不定死数值）
1. 模型：MediaPipe Hand Landmarker（或 Pose+Hands 组合），与现有 `tasks-vision` 同栈。
2. 加载：CDN 优先，本地 `docs/h5/mediapipe/` 后备；失败时日课触控演示仍可用。
3. 与玩法：Hand 只驱动呈现与寸劲反馈（`HandPresent`／FxLayer）；Pose 独掌 `ArmShape` 与命中；手模不进入判定、不改置信度。
4. 渲染：左手／右手骨架叠在 `overlayCanvas`；不挡木人高亮靶臂。

`HandPresent`∈{`guard`,`punch_drive`,`bong_bridge`,`lost`}。动作语义只跟冲／膀，无手指戏。`HandViewState` 挂接 `onPoseShape`、`onHitOk`、`onHoldProgress`、`onTrackLost`。这些钩子只更新手模呈现与寸劲反馈。

## 下一步
- [ ] 接入 HandLandmarker 加载与权限同路径
- [ ] 腕点与冲／膀方向一致性启发
- [ ] 竖屏 390 宽可读性复验（C4）
- [ ] 同帧时间戳对齐 Pose+Hand
- [ ] 腕根驱动手模 + 丢失淡出

未合 main；Pages 仍指当前分享版。

## 手模 ↔ 摄像头同步口径（对照 FPV 参考图）

1. 同源同帧：同一视频帧同时跑 PoseLandmarker 与 Hand Landmarker。用手部结果时必须带同一视频时间戳，禁止用手部上一帧去配姿态本帧。
2. 驱动分工：Pose 继续负责冲／膀二形与命中（瞬时或维持 3s、冷却 2s、60s 十击谱不变）。Hand 的 21 点只驱动画面下手模的根位（腕）与指形，用于呈现与寸劲反馈，不另开命中判定通道。
3. 空间映射：自拍镜像后，腕点映射到手模根。掌心法线与指尖相对腕映射到冲（斜上伸）／膀（斜下桥）两套目标姿态。手点丢失时手模淡出，Pose 日课与触控演示仍可用。
4. 画面层：手模叠在摄像头预览之上，不得遮挡木人高亮靶臂（armRU／arm.mid）与中线。竖屏约 390 宽须过 C4 可读门。
5. 模式边界：参考图中「10 秒内击打右上桩手 10 次」是另一套节奏表，可共用同步层，但不得改当前木人桩课 60s／3s／2s。未过线前不合 main、不刷 Pages。

## 叙事短签（HandPresent → 文案）

短签属 FxLayer，不改 Pose／Hit 判定。口令仍用「斜上冲出／斜下成式」。

- `guard`：无短签。
- `punch_drive`／`bong_bridge`：显示「手模跟手中」。
- `lost`：显示「手模丢失，回到框内」。
- 计击瞬间（`onHitOk`）：显示「寸劲到位」。
