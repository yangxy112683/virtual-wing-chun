# 虚拟咏春｜UE 原型制作大纲 v1.2

- 日期：2026-11-05（Asia/Shanghai）
- 状态：**待 owner 终审**（相对 v1.1，按四条系统锁与体验呈现约束收口）
- 依据：H5 日课探针节奏｜`docs/h5/HAND_MODEL_PLAN.md`（分支 `cursor/h5-with-handmodel` tip `6d632bb`）｜#12 平滑（`f66d847`）｜`drill-cam-v1.0.html`
- 说明：早期草稿把对齐点写成 `7fca31a`（Pages workflow）。手模句子以当前 tip 上的 `HAND_MODEL_PLAN` 为准，并保留 #12 的平滑句。两套呈现若冲突，都只属于画面。

---

## 0. 一句话

Unreal 第一人称木人桩日课：摄像头路径上 **Pose 独掌冲／膀命中**；Hand 只发 `HandPresent`。同帧双手入镜才允许摄像头日课开课。蒙皮叠层与手模只做呈现，不改命中。日课允许触控／键位兜底；咏春比赛专用禁止兜底。

## 0.1 四条系统锁

1. **Pose 独掌冲／膀命中。** Hand 只发出 `HandPresent`：`need_both`／`both`／`miss_*`（`miss_left`、`miss_right`）／`guard`／`punch_drive`／`bong_bridge`／`lost`。Hand 不写 `classifyPose`，不写 `confidence`。`punch_drive`／`bong_bridge` 只是呈现标签，即使与招形同名，也不计击。
2. **摄像头日课开课须同帧双手。** 蒙皮叠层、护手、盖住骨架的手模只做呈现，不得改 `HitValidate`。
3. **叠层的位置、角度、缩放走短窗平滑，并带 `wristAgrees` 滞回。** `frozen` 是同帧瞬时目标，必须当帧立刻对齐，不得跟着约 45ms 的显示平滑拖尾。只有画面层的根位置、角度和 `palmScale` 向该 `frozen` 目标做短窗平滑，并带已写明的 `wristAgrees` 滞回与宽限。tip 计划里的固定车道与 `push` 可以同时存在。两套都只属于呈现，都不进入 `HitValidate`。句子优先采用 tip 的 `HAND_MODEL_PLAN` 与 #12 平滑段；二者冲突时并列写下，并写明都不进判定。
4. **十击谱、60s、维持 3s、击后冷却 2s 保持不变。** 这四项是与 H5 探针对齐的节奏，不是锁定的最终手感表。宽横屏分栏、加大木人、竖屏靶环内收只属于布局／呈现，**不进入命中语义**。

## 1. 已锁创意合同（工程不得改玩法）

| 项 | 合同 |
|----|------|
| 谱 | `冲-膀-冲-冲-膀-冲-膀-冲-冲-膀`（10 击） |
| 形 | `straight`＝日字冲拳；`bridge`＝膀手；只求二分可区分。分类只由 Pose 完成 |
| 侧分 | **左臂只判冲，右臂只判膀**（键位／触控：左／F＝冲，右／J＝膀）。侧分属于 Pose 命中，不属于 Hand |
| 过关双路径 | **瞬时 ok**，或对谱形 **连续维持 3s**（`HOLD_PASS_MS=3000`） |
| 击后冷却 | 有效击后 **2s** 不可再计（`POST_HIT_COOLDOWN=2000`） |
| 时限 | **60s**（`TIME_LIMIT=60`）；错招／未识别灰闪不计可重打，时限不停；`near` 不计 |
| 出画／丢手 | Pose 出画，或摄像头日课上 `HandPresent` 进入 `need_both`／`miss_*`／`lost` → **软暂停计时**，步序下标不推进。这是课钟门，不改招形分类 |
| 日课兜底 | `allowTapFallback=true`：无摄像头可直接开课；触控／F／J 可绕过双手门。成功仍走 Pose 侧的同一条反馈 |
| 比赛专用 | `allowTapFallback=false`：无点按／键位伪造；必须有摄像头且同帧过双手门 |

上表的十击、60s、3s、2s 是探针节奏。原型按此跑通。本文不另写一套数当作最终手感表。

---

## 2. 摄像头与手部识别（硬性｜原型必须交付）

### 2.1 目标

真机（优先前置）上：

1. **Pose**：判断当前步所需手臂是否做出匹配招形；仅 `quality==ok`（瞬时或维持满 3s）且匹配当前步 → 计击并跳格。冲／膀是否有效只看这一路。
2. **Hand**：同一视频帧同时检出左手与右手，才允许摄像头日课开课。课中再丢手则软暂停。Hand 的输出只有 §0.1 的 `HandPresent`。
3. **手模／蒙皮**：盖住骨架的叠层，以及固定车道上的前后推，都只更新画面。不进入 `classifyPose`／`confidence`／`HitValidate`。

点按／键位不是正式摄像头判定源，但日课兜底须走同一成功反馈总线。

### 2.2 最低识别能力（首板）

| 输出 | 对应招 | 玩家须呈现的可区分特征（概念） | 判定侧 |
|------|--------|--------------------------------|--------|
| `straight` | 日字冲拳 | 左臂直桥前伸意图（对向右上桩手） | 仅左臂 Pose |
| `bridge` | 膀手 | 右臂斜桥／肘外翻意图（对向中桩手） | 仅右臂 Pose |
| `unknown` | — | 无法归类 | 不计有效击 |

**明确不做（首板命中）**：逐关节角度表、力度、步法、多招细谱教学认证；手部 21 点参与命中；用腕点、车道 `push`、`frozen` 或 `HandPresent` 改写 `classifyPose`／`confidence`；寸劲辉光；「寸劲到位」短签。

腕根叠层若按 #12 出现，只画在画面上，见 §2.5。它不在本表的判定侧。

### 2.3 双手入镜门（与 H5 `HAND_MODEL_PLAN` 冻结口径一致）

1. 摄像头日课点「开始」后：同一帧 Hand 同时给出左、右手才开课。只见一手、两手同侧、或左右分属相邻帧 → 不开门。
2. 日课无摄像头（权限失败／未开）→ 直接开课；触控演示／F／J 不经此门。
3. 比赛专用：无摄像头或未过门 → 不可开课。
4. `HandPresent` 状态集锁定如下。计划文里的 `both_ready` 只是 `both` 的别名，必须映射回 `both`，不得另开判定字段。
   - `need_both`：开了摄像头且尚未同帧左右手。短签「请双手入镜」。不画挡住木人的手模。软暂停，不计击。
   - `both`：同帧左右手都在。解锁摄像头开课，可进入护手呈现。
   - `miss_left`／`miss_right`：只见一手。短签仍是「请双手入镜」。软暂停，不计击。
   - `guard`：双手已就绪时的护手。无出招短签。
   - `punch_drive`／`bong_bridge`：冲／膀的手模呈现标签。不计击，不写 `classifyPose`，不写 `confidence`。
   - `lost`：曾到达 `both` 之后双手都离开。短签「手模丢失，回到框内」。不推进步序。还没到过 `both` 时，双手都不在仍算 `need_both`。
5. 单帧漏检先宽限去抖，再改短签／态。去抖只影响门与呈现。

### 2.4 运行时合同

1. 开课前请求摄像头权限。
2. 同帧时间戳同时喂给 Pose 与 Hand；禁止用手部上一帧配姿态本帧。
3. `PoseIngress` → `PoseHitCandidate{ shape, moveId?, zoneId?, side, confidence, quality: ok|near|wrong|lost, t }`。`shape`、`side`、`confidence`、`quality` 只从 Pose 来。
4. `HandIngress` → `HandPresent{ state: need_both|both|miss_left|miss_right|guard|punch_drive|bong_bridge|lost, t }`。只做门控与呈现。
5. `HitValidate` 只读 Pose 来的 `StrikeIntent`：双手门允许课钟推进，且 `quality==ok`、shape／moveId 匹配当前步、侧分正确、不在击后冷却内 → `OnHitValid` 并 `step++`。`HandPresent` 不进入此函数。
6. `quality==wrong` 或不符 → `OnHitWrong`，不跳格。
7. `quality==near` → 弱提示，不跳格。
8. Pose `lost`，或 `HandPresent` 为 `need_both`／`miss_*`／`lost` → 软暂停课钟；恢复后续时，已计数与 `step` 保留。暂停不改写已产生的 Pose 分类。
9. 日课 `debug_tap`／F／J：伪造当前招 `ok`，须走同一 `FeedbackBus` 成功路径。这条路径仍不读 Hand 的招形。
10. 比赛专用：UI 不得出现点按／键位入口。

### 2.5 手模与蒙皮（只呈现，不进判定）

皮肤精灵盖住骨架线，范围是前臂中段到指尖；左／右贴图。叠层低于高亮靶臂，不得挡住 `right_upper`／`mid_arm`（H5 对应 `armRU`／`arm.mid`）。横屏可见长度约视口宽度 1/3。竖屏不盖中臂与右上靶臂。

静止时不跟单帧噪声抖。冲／膀要跟手，平滑窗保持短，不要拖成发黏的滞后。下面两档都只约束画面：#12 的显示插值约 45ms，且只作用于画面层；`frozen` 当帧立刻对齐，不走这档。tip 计划的 `push` 约 90ms。它们不是命中参数，也不是最终手感表。

两套呈现并列。冲突时都不进入 `HitValidate`。

**A. tip `HAND_MODEL_PLAN`（`6d632bb`）固定车道**

- 左手在杆左、右手在杆右。每只手一个 `push`（0 护手 → 1 前推并略缩小），以约 90ms 时间常数指数靠近目标。
- `push` 目标由 **Pose 本侧达标** 或日课 F／J／触控脉冲驱动，不由 Hand 的左右标签驱动车道。
- 这一套不跟腕点、不左右翻转、无掌倾、无寸劲辉光。

**B. #12（`f66d847`）短窗平滑**

- `frozen` 是同帧瞬时目标，必须当帧立刻对齐，不得跟着约 45ms 的显示平滑拖尾。只有画面层的根位置、角度和 `palmScale` 以约 45ms 时间常数向该 `frozen` 目标指数靠近。静止时不跟单帧噪声跳。
- `wristAgrees` 对指尖相对腕的 dy 用进入 0.02、保持 0.006 两档，避免贴着分界每帧翻转角度混合。
- 左右标签只对调一帧时，在 `PRESENT_MISS_GRACE_MS` 内保持原侧精灵，不立刻对调或清掉。
- 这套可以出现腕根与角度。它只更新叠层，不写命中。

短签（FxLayer）：`need_both` 与 `miss_*`「请双手入镜」；左手呈现「左手 · 日字冲拳」；右手呈现「右手 · 膀手」；`guard` 无出招短签；`lost`「手模丢失，回到框内」。计击瞬间不显示「寸劲到位」。木人臂闪光与音字保留，命中仍要一眼可读。#12 旧句里的「手模跟手中」「寸劲到位」不得写回短签。

### 2.6 摄像头验收用例（出门必测）

| ID | 步骤 | 期望 |
|----|------|------|
| CAM-01 | 日课开课，授予摄像头 | 预览可见；未双齐前为 `need_both` |
| CAM-02 | 同帧双手入镜后开始 | 进入课中；可画护手位手模 |
| CAM-03 | 第 1 击左臂直桥 → Pose `straight+ok` | 计数+1，切膀；进入 2s 冷却。不依赖 `punch_drive` |
| CAM-04 | 第 1 击故意右臂斜桥／错侧 | 不计不跳格 |
| CAM-05 | 对谱形维持满 3s（无瞬时 ok） | 计 1 并跳格 |
| CAM-06 | 有效击后 2s 内重复同形 | 不计第二次 |
| CAM-07 | 课中遮挡／丢一手或出画 | 计时暂停；回框后续上，计数与步序保留 |
| CAM-08 | 日课关摄像头，仅触控／F／J | 可跑完谱；标明触控演示；不经双手门 |
| CAM-09 | 咏春比赛专用 | 无点按；无摄像头或未过门不可开课 |
| CAM-10 | 连续错形刷分 | 有效击不增加 |

蒙皮是否盖住骨架、横屏手长约 1/3、静止不抖、冲／膀跟随不发黏，只验收呈现。这些观察不改变上表的计击期望。

### 2.7 工程实现提示（不锁 SDK）

- Pose／Hand 可用任意移动端方案，只要能稳定输出上表语义。Hand 的稳定输出是 `HandPresent`，不是招形置信度。
- M2 允许键盘模拟 Pose／Hand 事件；**M3 必须真机摄像头**，CAM-02～07、09 通过才算原型达标。
- SDK／UE 版本由工程选定后回写附录。

---

## 3. 场景与布局

- `L_Dojo_Drill`；`BP_PlayerPawn_FP`；`BP_WoodenDummy` sockets：`right_upper`／`mid_arm`（竖屏木人尺度参考 H5 大桩；右上靶环竖屏内收，矮横屏不跟收）。
- **布局**：竖屏与宽度不足约 1000px 的横屏 → 单栏舞台；更宽横屏 → 左栏（摄像头／示范）｜舞台｜右栏（任务卡）；桩臂以杆中线为根；短签靠边，不压中线。
- `DrillSession` 持课状态；安全区与手模不得挡高亮靶臂与中线。
- 宽横屏分栏、加大木人、竖屏靶环内收只属于布局与呈现，不进入命中语义，不改变十击、60s、3s、2s。

## 4. 模块边界

```
Camera ─┬→ PoseIngress → PoseHitCandidate → InputRouter → StrikeIntent → HitValidate
        └→ HandIngress → HandPresent ─┬→ Gate（同帧双手门／软暂停）→ ClockService
                                      └→ PresentHands（蒙皮／车道／平滑；不进命中）
debug_tap / F·J（仅日课）──────────→ InputRouter
HitValidate → SequenceDriver / DrillSession → FeedbackBus
```

`HandPresent` 不到达 `InputRouter`，也不到达 `HitValidate`。`DA_DrillLesson`：mode、`timeLimitSec=60`、`targetHits=10`、`holdPassMs=3000`、`postHitCooldownMs=2000`、allowTapFallback、moveSequence[10]、lateralRule（左冲右膀）。这些时间与次数是探针节奏字段，不是最终手感表。

## 5. UMG／事件／文案与体验呈现

控件：镜框、谱面步进、倒计时环、双手门短签、出招短签、结算。

事件：`OnBothReady`、`OnNeedBoth`、`OnHandLost`、`OnHitValid`、`OnHitWrong`、`OnPoseLost`、`OnPoseResumed`、`OnStepChanged`。`OnHitValid`／`OnHitWrong` 只由 Pose 路径发出。比赛专用不出现点按／键位文案。

以下全部只约束呈现与 UMG，不进入命中判定：

- 蒙皮手盖住骨架，不得挡住高亮靶臂 `right_upper`／`mid_arm`。
- 横屏手的可见长度约视口宽度的 1/3。
- 待机不抖。冲／膀跟随清楚，短窗平滑，不要发黏的滞后。窗口用 §2.5 已写的约 45ms 与约 90ms，不另造一档。
- 命中反馈保留冲击关键词：木人臂闪光、音字。不弹出「寸劲到位」。命中仍要一眼可读。
- **禁止**：纯格斗游戏 HUD 底板；武侠分镜式的画面层层堆叠。

## 6. 一局必过验收

玩法谱面路径 + **§2.6 CAM**；仅兜底跑通 **不能** 替代 M3。手模抽搐、挡住靶臂、寸劲辉光或「寸劲到位」回潮、格斗 HUD 底板、武侠分镜堆叠，视为体验打回。这些打回不改命中语义。

## 7. 里程碑

| M | 内容 | 摄像头／手 |
|---|------|------------|
| M0 | 场景+UMG+点按跑谱 | 无 |
| M1 | DataAsset＋60s／3s／2s／十击＋结算＋模式开关 | 无 |
| M2 | Pose 事件占位 + Hand 只发 `HandPresent`（键盘模拟招形与双手门） | 模拟 |
| **M3** | **真机 Pose 二分 + 同帧双手门 + 手模呈现（车道与 #12 平滑都不进命中）** | **必达 CAM-02～07、09** |
| M4 | 横屏分栏／竖屏靶环与大桩、权限失败路径、音画打磨 | 真机 |

## 8. OUT

人对战；创意团队写工程代码；细关节教学认证；手部点参与命中；寸劲辉光；「寸劲到位」短签；锁死某一家姿态 SDK。

把 60s／3s／2s／十击写成锁定的最终手感表。把宽横屏分栏、加大木人、竖屏靶环内收写进命中语义。

合入会把上述锁打回去的过期分叉。任何把 Hand 送进命中判定的改动，包括让 Hand 写 `classifyPose` 或 `confidence`，或让 `punch_drive`／`bong_bridge`／蒙皮叠层改 `HitValidate`。

## 9. 相对 v1.1 的变更摘要

1. 时限 10s → **60s**；补 **维持 3s／击后冷却 2s** 双路径。二者与十击谱都是探针节奏，不是最终手感表。
2. 补 **Hand 双手入镜门** 与软暂停语义。Hand 只发 `HandPresent`，不写招形与置信度。
3. 明确 **左冲右膀** 侧分由 Pose 独占。手模呈现并列 tip 的固定车道＋`push`，以及 #12 的 `frozen`／显示插值／`wristAgrees`。两套都不进判定。
4. 布局对齐 H5：宽横屏三列、竖屏大桩与靶环内收、手模尺度。这些只属于布局／呈现。
5. 验收表扩展 CAM-02～10。去掉「寸劲到位」短签。命中保留臂闪光与音字。
6. 对齐当前 tip `6d632bb` 的 `HAND_MODEL_PLAN`，并保留 #12（`f66d847`）平滑句。Pages workflow 提交仍是历史上的 `7fca31a`。
