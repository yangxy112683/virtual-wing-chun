import assert from "node:assert/strict";
import test from "node:test";
import {
  captureTipAudience,
  composeCaptureTip,
  releaseDebugCaptureTip,
  showCaptureTipText,
} from "../capture-tip.mjs";

const PLAYER = [
  "请双手入镜",
  "回到框内",
  "识别中…",
  "人偏下：屏幕前倾或坐远一点",
  "冷却中 2s",
  "冲态维持中 1.2/3s · 40%",
  "膀态维持中 0.4/3s · 13%",
  "需 HTTPS／localhost",
  "申请权限…",
  "权限失败／待开启",
  "加载识别模型…",
  "识别待命",
  "模型就绪·请开摄像头",
  "模型失败",
  "调试·无摄像头",
  "待开启",
  "待开启 · 日课可直接开始",
  "摄像头未开",
];

const DEBUG = [
  "unknown 弱特征",
  "unknown 左臂弱特征",
  "unknown 右臂弱特征",
  "unknown 左臂方向不明",
  "unknown 右臂上下接近",
  "unknown 未出招",
  "unknown 无人",
  "unknown 出画",
  "straight 冲↑ dy=0.12",
  "bridge 膀↓ dy=0.20",
  "检出 0/2 只手",
  "检出 1/2 只手",
  "检出 2/2 只手",
];

test("玩家短签在调试关和调试开时都原样留下", () => {
  for (const text of PLAYER) {
    assert.equal(captureTipAudience(text), "player", text);
    assert.equal(showCaptureTipText(text, false), text, text);
    assert.equal(showCaptureTipText(text, true), text, text);
  }
});

test("unknown、弱特征和检出只数只在调试模式出现", () => {
  for (const text of DEBUG) {
    assert.equal(captureTipAudience(text), "debug", text);
    assert.equal(showCaptureTipText(text, false), "", text);
    assert.equal(showCaptureTipText(text, true), text, text);
  }
});

test("双手入镜门每次都显示请双手入镜，调试信息只追加不替换", () => {
  assert.equal(composeCaptureTip("请双手入镜", "检出 1/2 只手", false), "请双手入镜");
  assert.equal(
    composeCaptureTip("请双手入镜", "检出 1/2 只手", true),
    "请双手入镜 · 检出 1/2 只手",
  );
  assert.equal(
    composeCaptureTip("请双手入镜 · 人偏下：屏幕前倾或坐远一点", "检出 0/2 只手", false),
    "请双手入镜 · 人偏下：屏幕前倾或坐远一点",
  );
  assert.equal(
    composeCaptureTip("请双手入镜 · 人偏下：屏幕前倾或坐远一点", "检出 0/2 只手", true),
    "请双手入镜 · 人偏下：屏幕前倾或坐远一点 · 检出 0/2 只手",
  );
  assert.equal(
    composeCaptureTip("请双手入镜", "检出 1/2 只手 · unknown 弱特征", true),
    "请双手入镜 · 检出 1/2 只手 · unknown 弱特征",
  );
  assert.equal(
    releaseDebugCaptureTip("请双手入镜 · 检出 1/2 只手 · unknown 弱特征"),
    "请双手入镜",
  );
});

test("关掉调试后剥掉调试后缀，维持进度里的百分号留下", () => {
  assert.equal(releaseDebugCaptureTip("请双手入镜 · 检出 1/2 只手"), "请双手入镜");
  assert.equal(
    releaseDebugCaptureTip("请双手入镜 · 人偏下：屏幕前倾或坐远一点 · 检出 0/2 只手"),
    "请双手入镜 · 人偏下：屏幕前倾或坐远一点",
  );
  assert.equal(releaseDebugCaptureTip("冲态维持中 1.2/3s · 40%"), "冲态维持中 1.2/3s · 40%");
  assert.equal(releaseDebugCaptureTip("unknown 弱特征"), "");
  assert.equal(releaseDebugCaptureTip("调试·无摄像头"), "调试·无摄像头");
});
