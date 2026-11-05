# 系统｜UE 原型接口 v0.2（供《UE 原型制作大纲》v1.2 并入）

- 日期：2026-11-05（Asia/Shanghai）
- 性质：文档合同；不定死类名与插件选型；不写工程代码
- 对齐：`docs/h5/HAND_MODEL_PLAN.md`（分支 `cursor/h5-with-handmodel` tip `6d632bb`）｜#12 平滑（`f66d847`）｜大纲 v1.2
- 说明：早期草稿把对齐点写成 `7fca31a`。接口以当前 tip 的计划为准，并保留 #12 平滑句。两套呈现都不进入 `HitValidate`。

## 原型一局必须跑通

日课｜交错十击｜`input=camera_pose`｜左冲／右膀二分｜瞬时或维持 3s｜击后冷却 2s｜60s｜失败可重打不停表｜出画／丢手软暂停｜同帧双手门｜训练可 `debug_tap`／F·J｜比赛专用关兜底。

十击、60s、3s、2s 是与 H5 探针对齐的节奏，不是锁定的最终手感表。宽横屏分栏、加大木人、竖屏靶环内收只属于布局／呈现，不进入命中语义。

## 系统锁

1. Pose 独掌冲／膀命中。Hand 只发 `HandPresent`：`need_both`／`both`／`miss_*`（`miss_left`、`miss_right`）／`guard`／`punch_drive`／`bong_bridge`／`lost`。Hand 不写 `classifyPose`，不写 `confidence`。`punch_drive`／`bong_bridge` 只是呈现标签。
2. 摄像头日课开课须同一帧同时有左手与右手。蒙皮叠层与护手只做呈现，不改 `HitValidate`。
3. 叠层的位置、角度、缩放使用短窗平滑与 `wristAgrees` 滞回。`frozen` 是当帧瞬时目标，画面向它插值。tip 计划的固定车道与 `push` 可以同时存在。两套都只属于呈现，冲突时并列保留，都不进入 `HitValidate`。
4. 十击、60s、维持 3s、击后冷却 2s 不改。布局不进命中。

## 建议模块边界

| 模块 | 职责 | 吃什么 | 吐什么 |
|------|------|--------|--------|
| `DrillSession` | 状态机：就绪→课中→结算 | DrillBootstrap | 阶段事件、结算摘要 |
| `SequenceDriver` | `moveSequence[step]`、切招 | Bootstrap.sequence | `OnStepChanged` |
| `HitValidate` | 统一判定（含侧分、冷却、维持）。只读 Pose | StrikeIntent | valid／wrong／near／blocked |
| `PoseIngress` | 摄像头→招形候选 | 设备帧 | PoseHitCandidate（shape 二分 + side + confidence + quality） |
| `HandIngress` | 摄像头→双手门与呈现态 | 同帧 | HandPresent（上表状态集）。不写 classifyPose，不写 confidence |
| `Gate` | 同帧双手门／软暂停。只开关课钟 | HandPresent、Pose lost | 是否允许推进课钟 |
| `InputRouter` | 合并 Pose 与 debug_tap；按 mode 关开兜底。不读 Hand 招形 | PoseHitCandidate / Tap | StrikeIntent |
| `ClockService` | 课钟；lost／need_both／miss_* 时软暂停 | Gate | 剩余时间 |
| `PresentHands` | 蒙皮与车道。只画画面 | Pose 本侧或脉冲、HandPresent、frozen 目标 | 画面层 |
| `FeedbackBus` | 体验事件名 | Pose 判定／门控短签 | UI／SFX／短签 |
| `ResolveWriter` | 结算字段 | 课中累计 | 结算面板 |

`OnHitValid`／`OnHitWrong` 只由 `HitValidate` 发出。`Gate` 可以挡住课钟，使暂停期间不结算新的有效击；它不改 Pose 已经给出的 shape、side、confidence、quality。

## DataAsset 概念

- `DA_DrillLesson`：mode、label、`timeLimitSec=60`、`targetHits=10`、`holdPassMs=3000`、`postHitCooldownMs=2000`、moveSequence、allowTapFallback、input、lateralRule。时间与次数是探针节奏字段，不是最终手感表
- `DA_MoveDef`：moveId、shape（straight|bridge）、side（Left|Right）、反馈标签。shape 与 side 只供 Pose 路径使用

## 输入口

```
Camera ─┬→ PoseIngress → PoseHitCandidate → InputRouter → StrikeIntent → HitValidate
        └→ HandIngress → HandPresent ─┬→ Gate → Clock
                                      └→ PresentHands（仅画面）
debug_tap / F·J（仅日课）──────────→ InputRouter
```

验收：同谱面下，摄像头认对与日课兜底成功须走同一 `FeedbackBus` 成功事件。`HandPresent`、蒙皮、车道 `push`、`frozen` 显示插值都不进 `HitValidate`。

## 呈现（不进 HitValidate）

句子优先采用 tip 的 `HAND_MODEL_PLAN` 与 #12。二者冲突时都保留为呈现：

- **车道（tip `6d632bb`）**：左手在杆左、右手在杆右。`push` 从 0 护手到 1 前推，以约 90ms 时间常数指数靠近目标。目标由 Pose 本侧达标或日课 F／J／触控脉冲驱动，不由 Hand 左右标签驱动。
- **平滑（#12 `f66d847`）**：`frozen` 是当帧瞬时目标。画面上的根位置、角度和 `palmScale` 以约 45ms 时间常数向该目标指数靠近。`wristAgrees` 对指尖相对腕的 dy 用进入 0.02、保持 0.006 两档。左右标签只对调一帧时，在 `PRESENT_MISS_GRACE_MS` 内保持原侧精灵。静止时不跟单帧噪声跳。

蒙皮盖住骨架，不得挡住高亮靶臂。横屏可见长度约视口宽度 1/3。待机不抖；冲／膀跟随使用上面的短窗，不要发黏的滞后。计击保留木人臂闪光与音字，不显示「寸劲到位」。纯格斗游戏 HUD 底板、武侠分镜式堆叠禁止出现。细节见大纲 §2.5 与 §5。

## OUT

人对战；手部点参与命中；寸劲辉光；「寸劲到位」短签；把 60s／3s／2s／十击写成最终手感表；把布局写进命中语义；数值定稿表；合仓库工程代码。

合入会把上述锁打回去的过期分叉。任何把 Hand 送进命中判定的改动，包括 Hand 写 `classifyPose` 或 `confidence`，或让蒙皮／`punch_drive`／`bong_bridge` 改 `HitValidate`。
