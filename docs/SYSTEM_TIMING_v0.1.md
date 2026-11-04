# 系统｜课钟与识别间隔 v0.1（Owner 已拍）

- 日期：2026-11-04（Asia/Shanghai）

## 锁定
| 字段 | 值 | 说明 |
|------|-----|------|
| `timeLimitSec` | **60** | 一课总时长 1 分钟 |
| `targetHits` | 10 | 不变 |
| `postHitCooldownMs` | **6000** | 每次有效识别后冷却 6 秒，期间新候选不计 |
| 谱 | 锁定十击交错 | 不变 |

与节奏关系：10 次 × 6 秒 ≈ 60 秒满课节奏；错招／near 不占用冷却（或仅有效击启动冷却——**有效击才开 6 秒间隔**）。

## DrillBootstrap 增量
`timeLimitSec=60`，`intentGate.postHitCooldownMs=6000`（覆盖旧 10s／短冷却示意）。

## 文案
揭示句改为：「…1 分钟内按序有效击 10 次。」（叙事可补「有效击后稍候再出下一招」）

## HitValidate
有效击成功 → `lastHitAt`；`now - lastHitAt < 6000` 则丢弃候选（不灰闪也可，避免噪声）。
