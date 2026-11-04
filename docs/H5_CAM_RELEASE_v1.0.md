# H5-CAM 示例发布 · tag v1.0

- 日期：2026-11-04（Asia/Shanghai）
- 内容版本：drill-cam-v1.9.html（发布别名 drill-cam-v1.0.html）
- Git tag：v1.0

## 冻结合同摘要
- 谱：冲-膀-冲-冲-膀-冲-膀-冲-冲-膀
- 形：斜上＝冲，斜下＝膀
- 双路径：瞬时 ok 短去抖 或 维持满 3s，先到先计
- 冷却：有效击后 2s；总时 60s
- 日课可触控演示；比赛关点按
- 依赖：docs/h5/vendor/pose_landmarker_lite.task + 浏览器 MediaPipe（须 localhost／HTTPS）

## 运行
cd docs/h5 && python3 -m http.server 8765
打开 http://127.0.0.1:8765/drill-cam-v1.0.html
