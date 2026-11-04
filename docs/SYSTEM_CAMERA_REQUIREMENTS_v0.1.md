# 系统｜UE 原型·摄像头识别要求 v0.1

- 日期：2026-11-04（Asia/Shanghai）
- 用途：补进《UE 原型制作大纲》专节；仍只文档，不定死 SDK

## 目标（Demo 最低标准）
在竖屏／手机前置（若实现更简单则用前置）画面中，能稳定区分两种出招形，并驱动同一套 `HitValidate`：

| shape | 招式 | 可观测完成条件（玩法已锁） |
|-------|------|---------------------------|
| `straight` | 日字冲拳 | 前手**直线前伸**（直桥） |
| `bridge` | 膀手 | 前臂**斜桥／肘外翻** |
| `unknown` | — | 分不清或未完成 → 不计不跳格 |

不做细关节教学分、不做完成度百分制。

## 功能要求

1. **权限与取景**：课前申请摄像头；镜框内需看见上半身／出招臂；`inFrame=false` → `pose_lost`，课钟软暂停，回框后续时不跳格。
2. **输出**：每识别周期产出 `PoseHitCandidate{shape, confidence, quality, t, source=camera_pose}`；`shape` 映射 `moveId`（straight→冲拳，bridge→膀手）。
3. **与序列对齐**：仅当 `shape`（或 moveId）匹配 `moveSequence[step]` 且 `quality=ok`、置信过门限 → 有效击并 `step++`；错形／unknown／near → 灰闪不计、可重打、时限不停（lost 除外）。
4. **门限原则**：`CONF_PASS` 从宽，以「两招不易互认」为准；近完成 `near` 弱提示不计。
5. **冷却**：有效击后短冷却，防止同一动作连计多击。
6. **模式**：日课允许 `debug_tap` 注入同成功反馈；咏春比赛专用关闭点按，仅摄像头。
7. **反馈口**：识别中／成功／错招／近／出画须打到体验已定事件：`OnPoseRecognizing`／`OnHitValid`／`OnHitWrong`／`OnHitNear`／`OnPoseLost`／`OnPoseResumed`。

## 里程碑对齐

| 里程碑 | 识别相关交付 |
|--------|----------------|
| M0–M1 | 可不接真摄像头；点按跑谱 |
| M2 | `PoseIngress` 占位：键盘／调试键模拟 `straight`｜`bridge`，走完整判定链 |
| M3 | **真机前置（或更简单方案）二分识别**上线；满足上表最低标准与出画软暂停 |
| M4 | 比赛关兜底；无点按；识别失败可重打手感打磨 |

## 验收用例（识别专条）

1. 当前步要冲拳：做直线前伸 → 计 1 并切下一招；故意做斜桥 → 不计不跳格。
2. 当前步要膀手：做斜桥／肘外翻 → 计并跳格；故意直臂冲拳 → 不计。
3. 遮挡或走出镜框 → 虚线框＋计时停；回框后 step 不变，可继续当前击。
4. 模糊／未完成 → `near` 或 unknown，不计。
5. 日课无识别时点按仍可过当前击；比赛专用点按无效。

## OUT
锁死具体姿态 SDK／模型版本；云端识别强制联网；全屏骨架特效；人对战姿态同步。

## 请制作人
将本节作为大纲 **「§摄像头识别要求」** 并入 v1.1；§3 模块表可加一句「M3 必须满足本节验收」。

## 附录｜置信与门限伪规则（不定死数值）

```
每周期 PoseHitCandidate C:
  if not inFrame:          quality=lost;  Clock.softPause; return
  if shape==unknown:       quality=near或wrong按实现；不计不跳格
  if confidence < CONF_NEAR: 丢弃或 near；不计
  if CONF_NEAR <= confidence < CONF_PASS: quality=near；OnHitNear；不计
  if shape 与 moveSequence[step] 不符: quality=wrong；OnHitWrong；不计不跳格
  if confidence >= CONF_PASS 且 shape 匹配:
       quality=ok → StrikeIntent → OnHitValid → step++；启动 postHitCooldown
```

原则：`CONF_PASS` 从宽，优先「两招不互认」；`CONF_NEAR` < `CONF_PASS`；具体浮点由工程在 M3 标定后回写附录，创意合同不锁表。

---

## 修订｜Owner 放宽（2026-11-04）

最低可区分标准改为：
- `straight`：斜向上出拳即可
- `bridge`：斜向下出拳即可

详见 `SYSTEM_BROWSER_POSE_PSEUDO_v0.2.md`。旧「直桥肘角／斜桥外翻」细节降为可选观感，不作过线硬条件。
