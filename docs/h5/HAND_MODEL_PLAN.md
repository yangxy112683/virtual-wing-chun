# H5 手部建模准备（分支 cursor/h5-with-handmodel）

基准：与线上 Pages 一致的 `docs/h5/drill-cam-v1.0.html`（main @ d0372af / Safari 分享版）。

## 目标
在现有 PoseLandmarker（全身姿态）之上，增加 **手部关键点**。手部只用于冲／膀出拳时腕、掌、指的可读反馈，以及寸劲的画面呈现。

摄像头路径在允许按下「开始」之前，须由 HandLandmarker 在同一帧里同时检出左手与右手。触控演示可以不经过这道门。

## 建议接口（本阶段只定方向，不定死数值）
1. 模型：MediaPipe Hand Landmarker（或 Pose+Hands 组合），与现有 `tasks-vision` 同栈。
2. 加载：CDN 优先，本地 `docs/h5/mediapipe/` 后备；失败时日课触控演示仍可用。
3. 与玩法：摄像头路径须同帧检出左右手，才允许「开始」；触控演示可绕过。Hand 只驱动呈现与寸劲反馈（`HandPresent`／FxLayer）；Pose 独掌 `ArmShape` 与命中；手模不进入判定、不改置信度。
4. 渲染：最终观感用前臂中段到指尖的皮肤贴图（透明 PNG，长边不超过 512），放在画面下约 1/3，叠层低于木人高亮靶臂。不用线框收尾，不画上身与脸。规格见下文「皮肤贴图」。页面已按此绘制。

就绪先分 `need_both` 与 `both_ready`（或等价名）。`both_ready` 之后，`HandPresent`∈{`guard`,`punch_drive`,`bong_bridge`,`lost`}。`need_both` 不进入冲／膀呈现。动作语义只跟冲／膀，无手指戏。`HandViewState` 挂接 `onPoseShape`、`onHitOk`、`onHoldProgress`、`onTrackLost`。这些钩子只更新手模呈现与寸劲反馈。

## 下一步
- [x] 接入 HandLandmarker 加载与权限同路径
- [x] 腕点与冲／膀方向一致性启发
- [ ] 竖屏 390 宽可读性复验（C4）
- [x] 同帧时间戳对齐 Pose+Hand
- [x] 腕根驱动手模 + 丢失淡出
- [x] 双手同帧门：摄像头「开始」须同一帧检出左手与右手；触控演示可绕过
- [x] `need_both`／`both_ready`：不足左右手时不进冲／膀，不画挡住木人的单手残影
- [x] 课中单手丢失：呈现软暂停，不推进步骤下标；双手回到后续上

未合 main；Pages 仍指当前分享版。

## 表现层落地（本分支，未合 main）

`docs/h5/drill-cam-v1.0.html` 已接上表现层。`HOLD_PASS_MS`、击后冷却、60s 与十击谱未改。Hand 不进入 `classifyPose`，不写 `confidence`。

- 加载：摄像头权限成功后的同一条 `initPose` 路径创建 HandLandmarker，且不阻塞开课。模型先取 Google 存储 CDN，再试 `docs/h5/mediapipe/hand_landmarker.task`。失败或仍在下载时，Pose 日课与触控演示继续。
- 同帧：视频 `currentTime` 变化时取一个时间戳，同时交给 Pose 与 Hand。不把上一帧手点配到本帧姿态。
- 腕根：landmark 0 驱动虚手根，并避开木人中线。指尖相对腕只在与当前冲／膀同向时，把绘制角向该方向轻推；反向时仍用斜上／斜下规范角。护手不跟手指。
- 画面：皮肤精灵画在 `#handOverlay` 下三分之一。`armRU`／`arm.mid` 高亮的 `z-index` 压过虚手。摄像头小窗只留 Pose 关节点。
- 丢手：单帧漏检先留上一对双手。超过短暂间隔后清掉虚手。缺一手显示「请双手入镜」并软暂停；两手都没了显示「手模丢失，回到框内」。
- 双手门：摄像头日课点「开始」后，摄像头不可用、权限失败或手模未加载时也不进课，短签和 camStatus 都是「请双手入镜」。同一帧同时有左手和右手才开课。触控演示不经这道门。
- 皮肤：`docs/h5/hand-skin-L.png`、`docs/h5/hand-skin-R.png`，从参考图裁前臂中段到指尖，最长边 512。护手／冲／膀共用这两张，靠腕角和掌倾区分，画在 `#handOverlay` 下三分之一。
- 未在此环境验证：Safari 实机，以及竖屏 390 宽的 C4 可读门。

页面已按下一节口径接上。`both_ready` 在页面里记为 `both`。缺左、缺右记为 `miss_left`、`miss_right`，短签仍是「请双手入镜」。还没双齐时，两手都不在记为 `need_both`。

## 手模 ↔ 摄像头同步口径（对照 FPV 参考图）

1. 同源同帧：同一视频帧同时跑 PoseLandmarker 与 Hand Landmarker。用手部结果时必须带同一视频时间戳，禁止用手部上一帧去配姿态本帧。双手入镜门也用这一帧的 HandLandmarker 结果：左手与右手必须出现在同一帧。
2. 驱动分工：Pose 继续负责冲／膀二形与命中（瞬时或维持 3s、冷却 2s、60s 十击谱不变）。Hand 的 21 点只驱动画面下手模的根位（腕）与指形，用于呈现与寸劲反馈，不另开命中判定通道。
3. 空间映射：自拍镜像后，腕点映射到手模根。掌心法线与指尖相对腕映射到冲（斜上伸）／膀（斜下桥）两套目标姿态。手点丢失时手模淡出，Pose 日课与触控演示仍可用。
4. 画面层：手模叠在摄像头预览之上，不得遮挡木人高亮靶臂（armRU／arm.mid）与中线。竖屏约 390 宽须过 C4 可读门。
5. 模式边界：参考图中「10 秒内击打右上桩手 10 次」是另一套节奏表，可共用同步层，但不得改当前木人桩课 60s／3s／2s。未过线前不合 main、不刷 Pages。

## 制片冻结：双手入镜门与就绪态

以下口径已冻结，并已写进 `docs/h5/drill-cam-v1.0.html`。

1. 摄像头日课的「开始」：同一帧 HandLandmarker 同时给出左手与右手，才允许按下。只看到一只手、两只落在同一侧、或左右手分属相邻帧，都不开门。触控演示不走这道门。
2. `need_both`：跟踪不足左右各一只，包括缺左、缺右、以及两只都不在。短签为「请双手入镜」。此态不进入 `punch_drive`／`bong_bridge`，也不画单手残影挡住木人。
3. `both_ready`（或等价名）：同一帧左手与右手都在。摄像头「开始」可以解锁。解锁之后沿用已有呈现：`guard`／`punch_drive`／`bong_bridge`／`lost`。
4. 课中再丢一只手：呈现按 `need_both` 软暂停，短签用「请双手入镜」，不保持冲／膀画面。双手重新入镜后，回到暂停前的呈现。软暂停不推进步骤下标。Pose 仍独掌 `ArmShape`、命中、`confidence`、维持 3s、冷却 2s、60s 十击；手模门不改这些计时与计击。
5. 曾经 `both_ready` 之后双手都离开：呈现记为 `lost`，短签保持「手模丢失，回到框内」，不并成「请双手入镜」。约束与 `need_both` 相同：不进冲／膀，不留挡住木人的单手残影，不推进步骤下标；双手回到后再续。还没到达过 `both_ready` 时，双手都不在画面里仍算 `need_both`。
6. 单帧漏检不立刻改短签。去抖结束后仍不满足左右手，再进入上面的 `need_both` 或 `lost`。

同帧时间戳、Pose 独掌命中这两条不变。

## 皮肤贴图

呈现使用裁切后的人手皮肤精灵，不再用线框收尾。

- 资源：`docs/h5/hand-skin-L.png`、`docs/h5/hand-skin-R.png`。范围是前臂中段到指尖。透明 PNG。单边最长 512。
- 位置：画面下约 1/3。叠层低于高亮靶臂（`armRU`／`arm.mid`）。
- 不画上身，不画脸。
- 手部结果仍不进入 `classifyPose`，不写 `confidence`。

## 叙事短签（HandPresent → 文案）

短签只走 FxLayer，不改 Pose／Hit 判定。口令仍用「斜上冲出／斜下成式」。

- `need_both`：「请双手入镜」。
- `guard` 且双手已就绪：无短签。
- `punch_drive`／`bong_bridge`：「手模跟手中」。
- `lost`（就绪之后双手都离开）：「手模丢失，回到框内」。
- 计击瞬间（`onHitOk`）：「寸劲到位」。
